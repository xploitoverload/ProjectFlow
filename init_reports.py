#!/usr/bin/env python3
"""Initialize reports system and recreate database"""

import os
import sys
import secrets
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, Team, Project, Issue, ProjectUpdate, Sprint, Epic, Label

def init_database():
    """Initialize database with fresh schema"""
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Database schema created successfully!")
        
        # Create sample data (only if projects don't exist)
        if Project.query.count() == 0:
            print("\n📝 Creating sample data...")
            
            # Get existing team or create one
            team = Team.query.first()
            if not team:
                team = Team(name='Development', description_encrypted='Main development team')
                db.session.add(team)
                db.session.commit()
            
            # Get passwords from environment or generate secure defaults
            admin_password_hash = generate_password_hash(
                os.environ.get('ADMIN_PASSWORD', f'Admin{secrets.randbelow(10000):04d}!'),
                method='pbkdf2:sha256:600000'
            )
            dev_password_hash = generate_password_hash(
                os.environ.get('DEV_PASSWORD', f'Dev{secrets.randbelow(10000):04d}!'),
                method='pbkdf2:sha256:600000'
            )
            
            # Get existing users or use defaults
            admin = User.query.filter_by(username='admin').first()
            dev1 = User.query.filter_by(username='john_doe').first()
            dev2 = User.query.filter_by(username='jane_smith').first()
            designer = User.query.filter_by(username='test').first()
            
            # If users don't exist, create them with secure passwords
            if not admin:
                admin = User(
                    username='admin',
                    email_encrypted='admin@example.com',
                    password=admin_password_hash,  # Use secure hash from environment or generated
                    role='admin',
                    team_id=team.id
                )
                db.session.add(admin)
            
            if not dev1:
                dev1 = User(
                    username='john_doe',
                    email_encrypted='john@example.com',
                    password=dev_password_hash,  # Use secure hash from environment or generated
                    role='developer',
                    team_id=team.id
                )
                db.session.add(dev1)
            
            if not dev2:
                dev2 = User(
                    username='jane_smith',
                    email_encrypted='jane@example.com',
                    password=dev_password_hash,  # Use secure hash from environment or generated
                    role='developer',
                    team_id=team.id
                )
                db.session.add(dev2)
            
            if not designer:
                designer = User(
                    username='test',
                    email_encrypted='test@example.com',
                    password=dev_password_hash,  # Use secure hash from environment or generated
                    role='designer',
                    team_id=team.id
                )
                db.session.add(designer)
            
            db.session.commit()
            
            # Create project
            project = Project(
                name='Lunar Rover',
                key='NUC',
                description_encrypted='Lunar rover development project',
                status='Active',
                team_id=team.id,
                created_by=admin.id,
                workflow_type='kanban'
            )
            db.session.add(project)
            db.session.commit()
            
            # Create sample updates
            now = datetime.utcnow()
            
            update1 = ProjectUpdate(
                project_id=project.id,
                user_id=dev1.id,
                update_text_encrypted='Made progress on rover navigation system. Implemented basic pathfinding algorithm.',
                status='on_track',
                progress_percentage=65,
                hours_worked=8.5,
                team_members_count=4,
                estimated_completion_days=3,
                blockers_encrypted='Need to optimize pathfinding for real-world terrain',
                reporting_period='daily',
                date=now
            )
            
            update2 = ProjectUpdate(
                project_id=project.id,
                user_id=dev2.id,
                update_text_encrypted='Completed hardware testing for wheel motors. All systems operational.',
                status='on_track',
                progress_percentage=80,
                hours_worked=7.0,
                team_members_count=3,
                estimated_completion_days=2,
                reporting_period='daily',
                date=now - timedelta(hours=6)
            )
            
            update3 = ProjectUpdate(
                project_id=project.id,
                user_id=designer.id,
                update_text_encrypted='Weekly review: All subsystems integration on schedule. Camera calibration pending.',
                status='at_risk',
                progress_percentage=72,
                hours_worked=6.0,
                team_members_count=8,
                estimated_completion_days=5,
                blockers_encrypted='Camera calibration delayed - waiting for equipment',
                reporting_period='weekly',
                date=now - timedelta(days=1)
            )
            
            db.session.add_all([update1, update2, update3])
            db.session.commit()
            
            print(f"✅ Created team, 4 users, project, and 3 sample updates")
            print(f"\n📊 Sample Data Ready:")
            print(f"   Team: {team.name}")
            print(f"   Project: {project.name} ({project.key})")
            print(f"   Users: admin, john_doe, jane_smith, test")
            print(f"   Updates: 3 (1 daily, 1 daily, 1 weekly)")

if __name__ == '__main__':
    init_database()
    print("\n✅ Database initialization complete!")
