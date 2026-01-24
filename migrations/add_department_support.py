"""
Migration script to add department support and create core teams.
- Adds 'department' column to User table
- Adds 'department' and 'is_core_team' columns to Team table
- Creates core teams for each department
- Updates existing users with their department based on role
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text

# Import the department utility
from app.utils.department import get_department_from_role, get_core_teams_config, get_department_color

def run_migration():
    """Run the migration to add department support."""
    app = create_app()
    
    with app.app_context():
        try:
            # 1. Add department column to user table
            result = db.session.execute(text("PRAGMA table_info(user)"))
            user_columns = [row[1] for row in result.fetchall()]
            
            if 'department' not in user_columns:
                db.session.execute(text("ALTER TABLE user ADD COLUMN department VARCHAR(50)"))
                print("✓ Added department column to user table")
            else:
                print("✓ department column already exists in user table")
            
            # 2. Add columns to team table
            result = db.session.execute(text("PRAGMA table_info(team)"))
            team_columns = [row[1] for row in result.fetchall()]
            
            if 'department' not in team_columns:
                db.session.execute(text("ALTER TABLE team ADD COLUMN department VARCHAR(50)"))
                print("✓ Added department column to team table")
            else:
                print("✓ department column already exists in team table")
            
            if 'is_core_team' not in team_columns:
                db.session.execute(text("ALTER TABLE team ADD COLUMN is_core_team BOOLEAN DEFAULT 0"))
                print("✓ Added is_core_team column to team table")
            else:
                print("✓ is_core_team column already exists in team table")
            
            db.session.commit()
            
            # 3. Create core teams for each department
            from models import Team, User
            
            core_teams_config = get_core_teams_config()
            created_teams = 0
            
            for config in core_teams_config:
                # Check if core team already exists
                existing = Team.query.filter_by(
                    department=config['department'],
                    is_core_team=True
                ).first()
                
                if not existing:
                    team = Team(
                        name=config['name'],
                        department=config['department'],
                        color=config['color'],
                        is_core_team=True,
                        team_type='core'
                    )
                    team.description = f"Core {config['department']} department team"
                    db.session.add(team)
                    created_teams += 1
            
            db.session.commit()
            print(f"✓ Created {created_teams} core teams")
            
            # 4. Update existing users with their department based on role
            users = User.query.all()
            updated_users = 0
            
            for user in users:
                if not user.department and user.role:
                    user.department = get_department_from_role(user.role)
                    
                    # Auto-assign to core team if not already in a team
                    if not user.team_id:
                        core_team = Team.query.filter_by(
                            department=user.department,
                            is_core_team=True
                        ).first()
                        if core_team:
                            user.team_id = core_team.id
                    
                    updated_users += 1
            
            db.session.commit()
            print(f"✓ Updated {updated_users} users with department info")
            
            print("\n✅ Migration completed successfully!")
            
            # Show summary
            print("\n📊 Core Teams Created:")
            core_teams = Team.query.filter_by(is_core_team=True).all()
            for team in core_teams:
                member_count = len(team.members)
                print(f"   - {team.name}: {member_count} members")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Migration failed: {e}")
            import traceback
            traceback.print_exc()
            raise e

if __name__ == '__main__':
    run_migration()
