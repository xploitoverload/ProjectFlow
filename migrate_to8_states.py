# migrate_to_8_states.py - Migrate from 4-state to 8-state workflow
"""
This script updates your existing issues to use the new 8-state workflow system.
Run this AFTER updating models.py and app.py
"""

from app import app, db
from models import Issue
from sqlalchemy import text

def migrate_to_8_states():
    print("="*60)
    print("MIGRATING TO 8-STATE WORKFLOW SYSTEM")
    print("="*60)
    
    with app.app_context():
        print("\nStep 1: Checking current issue statuses...")
        
        # Get count of issues by current status
        status_counts = {}
        all_issues = Issue.query.all()
        
        for issue in all_issues:
            status = issue.status or 'none'
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print(f"\nFound {len(all_issues)} total issues:")
        for status, count in status_counts.items():
            print(f"  • {status}: {count} issues")
        
        if not all_issues:
            print("\n✓ No issues to migrate. You're ready to go!")
            return
        
        print("\nStep 2: Migrating issues to new 8-state system...")
        
        migrated_count = 0
        
        # Migration logic:
        # Old 4-state → New 8-state mapping
        migrations = {
            'todo': 'todo',              # Keep as-is
            'in_progress': 'in_progress', # Keep as-is
            'in_review': 'code_review',  # Map review to code_review
            'done': 'done',              # Keep as-is
        }
        
        for issue in all_issues:
            old_status = issue.status
            
            # If status is already valid 8-state, skip
            if old_status in ['open', 'todo', 'in_progress', 'code_review', 'testing', 'ready_deploy', 'done', 'closed']:
                continue
            
            # Map old status to new status
            if old_status in migrations:
                new_status = migrations[old_status]
                issue.status = new_status
                migrated_count += 1
                print(f"  Migrated {issue.key}: {old_status} → {new_status}")
        
        if migrated_count > 0:
            db.session.commit()
            print(f"\n✓ Migrated {migrated_count} issues to new status system")
        else:
            print("\n✓ All issues already using new status system!")
        
        print("\nStep 3: Verifying new status distribution...")
        
        # Get new status counts
        new_status_counts = {}
        all_issues = Issue.query.all()
        
        for issue in all_issues:
            status = issue.status
            new_status_counts[status] = new_status_counts.get(status, 0) + 1
        
        print(f"\nNew status distribution:")
        state_order = ['open', 'todo', 'in_progress', 'code_review', 'testing', 'ready_deploy', 'done', 'closed']
        for status in state_order:
            count = new_status_counts.get(status, 0)
            if count > 0:
                print(f"  • {status}: {count} issues")
        
        print("\n" + "="*60)
        print("MIGRATION COMPLETED SUCCESSFULLY!")
        print("="*60)
        
        print("\n🎉 Your Kanban board now has 8 states:")
        print("  1. 🆕 OPEN - New issues")
        print("  2. 📋 TO DO - Ready to work")
        print("  3. ⚡ IN PROGRESS - Active work")
        print("  4. 👨‍💻 CODE REVIEW - Peer review")
        print("  5. 🧪 TESTING - QA testing")
        print("  6. 🚀 READY TO DEPLOY - Staged for release")
        print("  7. ✅ DONE - Deployed to production")
        print("  8. 🔒 CLOSED - Archived & complete")
        
        print("\n📍 Next steps:")
        print("  1. Start your Flask app: python app.py")
        print("  2. Visit any project's Kanban board")
        print("  3. You'll see all 8 columns!")
        print("  4. Drag issues between any columns")
        
        print("\n" + "="*60 + "\n")

if __name__ == '__main__':
    try:
        migrate_to_8_states()
    except Exception as e:
        print(f"\n❌ ERROR: Migration failed!")
        print(f"Error details: {e}")
        print("\nPlease check your database connection and try again.")
        import traceback
        traceback.print_exc()