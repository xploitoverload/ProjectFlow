# migrate_database.py - Add Issue tracking and Kanban support to existing database
"""
This script safely migrates your existing database to add:
- Issue/Task tracking tables
- Sprint and Epic support
- Workflow type to projects
- Comments and attachments for issues
"""

from app import app, db
from models import User, Team, Project, Issue, Sprint, Epic, Comment, Attachment, IssueDependency
from sqlalchemy import inspect, text

def migrate_database():
    """Add new tables and columns for Kanban/Issue tracking"""
    
    with app.app_context():
        print("="*60)
        print("PROJECT MANAGEMENT SYSTEM - DATABASE MIGRATION")
        print("="*60)
        print("\nThis will add Kanban board and issue tracking features.")
        print("Your existing data will NOT be affected.\n")
        
        # Get existing tables
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        print(f"Found {len(existing_tables)} existing tables:")
        for table in existing_tables:
            print(f"  ✓ {table}")
        
        print("\n" + "-"*60)
        print("STEP 1: Adding workflow_type to projects table")
        print("-"*60)
        
        # Check if workflow_type column exists
        project_columns = [col['name'] for col in inspector.get_columns('project')]
        
        if 'workflow_type' not in project_columns:
            print("Adding workflow_type column...")
            try:
                with db.engine.connect() as conn:
                    conn.execute(text(
                        "ALTER TABLE project ADD COLUMN workflow_type VARCHAR(20) DEFAULT 'agile'"
                    ))
                    conn.commit()
                print("✓ Added workflow_type column to projects")
            except Exception as e:
                print(f"⚠ Warning: {e}")
        else:
            print("✓ workflow_type column already exists")
        
        print("\n" + "-"*60)
        print("STEP 2: Creating new tables for issue tracking")
        print("-"*60)
        
        new_tables = {
            'sprint': 'Sprints for Agile workflow',
            'epic': 'Epics for grouping issues',
            'issue': 'Main issue/task tracking table',
            'comment': 'Comments on issues',
            'attachment': 'File attachments for issues',
            'issue_dependency': 'Issue dependencies and relationships'
        }
        
        tables_created = []
        for table_name, description in new_tables.items():
            if table_name not in existing_tables:
                print(f"Creating {table_name} table ({description})...")
                tables_created.append(table_name)
            else:
                print(f"✓ {table_name} table already exists")
        
        if tables_created:
            print("\nCreating all new tables...")
            db.create_all()
            print(f"✓ Created {len(tables_created)} new tables")
        else:
            print("✓ All required tables already exist")
        
        print("\n" + "-"*60)
        print("STEP 3: Updating existing projects")
        print("-"*60)
        
        # Set workflow type for existing projects
        from models import Project
        projects_updated = 0
        
        projects = Project.query.filter(
            (Project.workflow_type == None) | (Project.workflow_type == '')
        ).all()
        
        for project in projects:
            project.workflow_type = 'agile'
            projects_updated += 1
        
        if projects_updated > 0:
            db.session.commit()
            print(f"✓ Updated {projects_updated} projects with 'agile' workflow")
        else:
            print("✓ All projects already have workflow types")
        
        print("\n" + "-"*60)
        print("STEP 4: Updating issue table with missing columns")
        print("-"*60)
        
        # Check if completed_at column exists in issue table
        issue_columns = [col['name'] for col in inspector.get_columns('issue')]
        
        if 'completed_at' not in issue_columns:
            print("Adding completed_at column to issue table...")
            try:
                with db.engine.connect() as conn:
                    conn.execute(text(
                        "ALTER TABLE issue ADD COLUMN completed_at DATETIME"
                    ))
                    conn.commit()
                print("✓ Added completed_at column to issues")
            except Exception as e:
                print(f"⚠ Warning: {e}")
        else:
            print("✓ completed_at column already exists")
        
        print("\n" + "="*60)
        print("MIGRATION COMPLETED SUCCESSFULLY!")
        print("="*60)
        
        print("\n📊 Database Summary:")
        try:
            print(f"  • Users: {User.query.count()}")
            print(f"  • Teams: {Team.query.count()}")
            print(f"  • Projects: {Project.query.count()}")
            print(f"  • Issues: {Issue.query.count()}")
        except Exception as e:
            print(f"  ⚠ Could not count records: {e}")
        
        print("\n🎉 New Features Available:")
        print("  ✓ Drag-and-drop Kanban boards")
        print("  ✓ Issue/Task management")
        print("  ✓ Multiple workflow types (Agile, Waterfall, Hybrid)")
        print("  ✓ Sprint planning")
        print("  ✓ Epic support for large features")
        print("  ✓ Issue comments and attachments")
        print("  ✓ Task dependencies")
        
        print("\n📍 How to Use:")
        print("  1. Start your Flask app: python app.py")
        print("  2. Go to any project in the dashboard")
        print("  3. Click the '📋 Kanban' button")
        print("  4. Create issues and drag them between columns!")
        
        print("\n" + "="*60 + "\n")

if __name__ == '__main__':
    try:
        migrate_database()
    except Exception as e:
        print(f"\n❌ ERROR: Migration failed!")
        print(f"Error details: {e}")
        print("\nPlease check your database connection and try again.")
        import traceback
        traceback.print_exc()