"""
Migration to extend the role column size from String(20) to String(50)
to accommodate more comprehensive role names.
"""
import sqlite3
import os

def migrate():
    """Extend role column to support longer role names"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'project_management.db')
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # SQLite doesn't require column type changes as it uses dynamic typing
        # But we can verify the current roles and update if needed
        
        # Get current roles
        cursor.execute("SELECT DISTINCT role FROM user")
        current_roles = cursor.fetchall()
        print(f"Current roles in database: {[r[0] for r in current_roles]}")
        
        # The role column change from String(20) to String(50) in SQLite 
        # doesn't require migration since SQLite uses dynamic typing
        print("Role column extension successful (SQLite uses dynamic typing)")
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"Migration error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = migrate()
    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed!")
