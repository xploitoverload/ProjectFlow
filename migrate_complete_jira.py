# migrate_complete_jira.py - Add all Jira features to existing database
"""
This script adds:
- Epic support
- Labels (ACCOUNTS, BILLING, FORMS, FEEDBACK)
- Story points
- Issue links/dependencies
- Comments
- Attachments
- Watchers
- Workflow transitions
- Project keys
- Timeline dates
"""

from app import app, db
from models import (Project, Issue, Epic, Label, Comment, Attachment, 
                   IssueLink, IssueWatcher, WorkflowTransition, issue_labels)
from sqlalchemy import text, inspect

def migrate_complete_jira():
    print("="*70)
    print("COMPLETE JIRA FEATURE MIGRATION")
    print("="*70)
    print("\nAdding: Epics, Labels, Story Points, Dependencies, Comments, etc.")
    
    with app.app_context():
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        print(f"\nFound {len(existing_tables)} existing tables")
        
        # Step 1: Add new columns to existing tables
        print("\n" + "-"*70)
        print("STEP 1: Adding new columns to existing tables")
        print("-"*70)
        
        # Add project_key to projects
        project_columns = [col['name'] for col in inspector.get_columns('project')]
        if 'key' not in project_columns:
            print("Adding 'key' column to project table...")
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE project ADD COLUMN key VARCHAR(10)"))
                conn.commit()
            print("✓ Added project.key column")
        
        # Add story_points to issues
        if 'issue' in existing_tables:
            issue_columns = [col['name'] for col in inspector.get_columns('issue')]
            
            new_issue_columns = {
                'story_points': 'INTEGER',
                'time_remaining': 'FLOAT',
                'start_date': 'DATETIME',
                'end_date': 'DATETIME',
                'resolved_at': 'DATETIME',
                'closed_at': 'DATETIME',
                'parent_id': 'INTEGER'
            }
            
            for col_name, col_type in new_issue_columns.items():
                if col_name not in issue_columns:
                    print(f"Adding '{col_name}' to issue table...")
                    with db.engine.connect() as conn:
                        conn.execute(text(f"ALTER TABLE issue ADD COLUMN {col_name} {col_type}"))
                        conn.commit()
                    print(f"✓ Added issue.{col_name}")
        
        # Step 2: Create new tables
        print("\n" + "-"*70)
        print("STEP 2: Creating new tables")
        print("-"*70)
        
        new_tables = {
            'epic': 'Epics for grouping issues',
            'label': 'Labels for categorizing issues',
            'issue_labels': 'Issue-Label association',
            'issue_link': 'Issue dependencies',
            'comment': 'Issue comments',
            'attachment': 'File attachments',
            'issue_watcher': 'Issue watchers',
            'workflow_transition': 'Workflow audit trail'
        }
        
        tables_to_create = []
        for table_name, description in new_tables.items():
            if table_name not in existing_tables:
                print(f"Will create: {table_name} ({description})")
                tables_to_create.append(table_name)
        
        if tables_to_create:
            print(f"\nCreating {len(tables_to_create)} new tables...")
            db.create_all()
            print("✓ Created all new tables")
        else:
            print("✓ All tables already exist")
        
        # Step 3: Set project keys for existing projects
        print("\n" + "-"*70)
        print("STEP 3: Setting project keys")
        print("-"*70)
        
        projects = Project.query.filter((Project.key == None) | (Project.key == '')).all()
        for project in projects:
            # Generate key from project name (first 3-4 chars, uppercase)
            key = ''.join([c for c in project.name.upper() if c.isalnum()])[:4]
            if not key:
                key = 'PROJ'
            
            # Make sure it's unique
            existing = Project.query.filter_by(key=key).first()
            if existing and existing.id != project.id:
                key = f"{key}{project.id}"
            
            project.key = key
            print(f"  Set {project.name} -> {key}")
        
        if projects:
            db.session.commit()
            print(f"✓ Set keys for {len(projects)} projects")
        
        # Step 4: Create default labels for each project
        print("\n" + "-"*70)
        print("STEP 4: Creating default labels")
        print("-"*70)
        
        default_labels = [
            {'name': 'ACCOUNTS', 'color': '#1f845a'},
            {'name': 'BILLING', 'color': '#0055cc'},
            {'name': 'FORMS', 'color': '#5e4db2'},
            {'name': 'FEEDBACK', 'color': '#c25100'}
        ]
        
        all_projects = Project.query.all()
        labels_created = 0
        
        for project in all_projects:
            existing_labels = Label.query.filter_by(project_id=project.id).count()
            if existing_labels == 0:
                for label_data in default_labels:
                    label = Label(
                        name=label_data['name'],
                        color=label_data['color'],
                        project_id=project.id
                    )
                    db.session.add(label)
                    labels_created += 1
                print(f"  Created labels for {project.name}")
        
        if labels_created > 0:
            db.session.commit()
            print(f"✓ Created {labels_created} labels")
        else:
            print("✓ Labels already exist")
        
        # Step 5: Update issue keys to use project key
        print("\n" + "-"*70)
        print("STEP 5: Updating issue keys")
        print("-"*70)
        
        issues = Issue.query.all()
        updated_keys = 0
        
        for issue in issues:
            project = Project.query.get(issue.project_id)
            if project and project.key:
                # Check if key already has correct format
                if not issue.key.startswith(project.key + '-'):
                    # Generate new key
                    issue_number = issue.id
                    new_key = f"{project.key}-{issue_number}"
                    
                    # Make sure it's unique
                    while Issue.query.filter_by(key=new_key).first():
                        issue_number += 1000
                        new_key = f"{project.key}-{issue_number}"
                    
                    issue.key = new_key
                    updated_keys += 1
        
        if updated_keys > 0:
            db.session.commit()
            print(f"✓ Updated {updated_keys} issue keys")
        else:
            print("✓ Issue keys already correct")
        
        # Step 6: Summary
        print("\n" + "="*70)
        print("MIGRATION COMPLETED SUCCESSFULLY!")
        print("="*70)
        
        print("\n📊 Database Summary:")
        print(f"  • Projects: {Project.query.count()}")
        print(f"  • Issues: {Issue.query.count()}")
        print(f"  • Epics: {Epic.query.count()}")
        print(f"  • Labels: {Label.query.count()}")
        print(f"  • Comments: {Comment.query.count()}")
        print(f"  • Attachments: {Attachment.query.count()}")
        
        print("\n🎉 New Features Available:")
        print("  ✓ Epic management")
        print("  ✓ Labels (ACCOUNTS, BILLING, FORMS, FEEDBACK)")
        print("  ✓ Story points")
        print("  ✓ Issue dependencies")
        print("  ✓ Comments system")
        print("  ✓ File attachments")
        print("  ✓ Workflow transitions")
        print("  ✓ Timeline view support")
        
        print("\n📍 Next Steps:")
        print("  1. python app.py")
        print("  2. Visit /project/<id>/kanban for enhanced Kanban board")
        print("  3. All issues now have proper keys (e.g., NUC-342)")
        print("  4. Labels are ready to use")
        
        print("\n" + "="*70 + "\n")

if __name__ == '__main__':
    try:
        migrate_complete_jira()
    except Exception as e:
        print(f"\n❌ ERROR: Migration failed!")
        print(f"Error details: {e}")
        print("\nPlease check your database and try again.")
        import traceback
        traceback.print_exc()