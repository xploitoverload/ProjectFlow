"""
Migration script to add many-to-many relationship between projects and teams.
Creates the project_teams association table and adds team_type/color columns to teams.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text

def run_migration():
    """Run the migration to add project_teams table and update Team model."""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if project_teams table already exists
            result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='project_teams'"))
            if result.fetchone():
                print("✓ project_teams table already exists")
            else:
                # Create the project_teams association table
                db.session.execute(text('''
                    CREATE TABLE project_teams (
                        project_id INTEGER NOT NULL,
                        team_id INTEGER NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (project_id, team_id),
                        FOREIGN KEY (project_id) REFERENCES project(id) ON DELETE CASCADE,
                        FOREIGN KEY (team_id) REFERENCES team(id) ON DELETE CASCADE
                    )
                '''))
                print("✓ Created project_teams association table")
            
            # Check if team_type column exists in team table
            result = db.session.execute(text("PRAGMA table_info(team)"))
            columns = [row[1] for row in result.fetchall()]
            
            if 'team_type' not in columns:
                db.session.execute(text("ALTER TABLE team ADD COLUMN team_type VARCHAR(50) DEFAULT 'general'"))
                print("✓ Added team_type column to team table")
            else:
                print("✓ team_type column already exists")
            
            if 'color' not in columns:
                db.session.execute(text("ALTER TABLE team ADD COLUMN color VARCHAR(7) DEFAULT '#6366f1'"))
                print("✓ Added color column to team table")
            else:
                print("✓ color column already exists")
            
            db.session.commit()
            print("\n✅ Migration completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Migration failed: {e}")
            raise e

if __name__ == '__main__':
    run_migration()
