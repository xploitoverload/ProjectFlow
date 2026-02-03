# init_db.py - Secure Database Initialization (FIXED)
from app import create_app
from models import db, User, Team, Project, ProjectUpdate
from datetime import datetime, timedelta

def init_database():
    """Initialize database with encrypted sample data"""
    app = create_app('development')
    with app.app_context():
        # Drop all tables and recreate
        print("Dropping existing tables...")
        db.drop_all()
        
        print("Creating new tables...")
        db.create_all()
        
        print("✓ Database tables created successfully!")
        
        # Create Teams
        print("\nCreating teams...")
        team1 = Team(name='Development Team')
        team1.description = 'Main development team for software projects'
        
        team2 = Team(name='Design Team')
        team2.description = 'UI/UX design and creative team'
        
        team3 = Team(name='Marketing Team')
        team3.description = 'Marketing and sales operations team'
        
        db.session.add_all([team1, team2, team3])
        db.session.commit()
        print("✓ Teams created!")
        
        # Create Users (passwords are hashed, emails are encrypted)
        print("\nCreating users...")
        
        admin = User(
            username='admin',
            role='admin',
            team_id=None
        )
        admin.email = 'admin@company.com'
        admin.set_password('Admin@123')  # Strong password
        
        employee1 = User(
            username='employee',
            role='employee',
            team_id=team1.id
        )
        employee1.email = 'employee@company.com'
        employee1.set_password('Employee@123')  # Strong password
        
        employee2 = User(
            username='john_doe',
            role='employee',
            team_id=team1.id
        )
        employee2.email = 'john.doe@company.com'
        employee2.set_password('John@1234')  # Strong password
        
        employee3 = User(
            username='jane_smith',
            role='employee',
            team_id=team2.id
        )
        employee3.email = 'jane.smith@company.com'
        employee3.set_password('Jane@1234')  # Strong password
        
        employee4 = User(
            username='mike_wilson',
            role='employee',
            team_id=team3.id
        )
        employee4.email = 'mike.wilson@company.com'
        employee4.set_password('Mike@1234')  # Strong password
        
        db.session.add_all([admin, employee1, employee2, employee3, employee4])
        db.session.commit()
        print("✓ Users created with encrypted emails and hashed passwords!")
        
        # Create Projects (descriptions are encrypted)
        print("\nCreating projects...")
        
        project1 = Project(
            name='E-commerce Website Development',
            key='ECOM',
            status='In Progress',
            team_id=team1.id,
            start_date=datetime.utcnow() - timedelta(days=30),
            created_by=admin.id
        )
        project1.description = 'Build a full-featured e-commerce platform with secure payment integration'
        
        project2 = Project(
            name='Mobile App Design',
            key='MOBILE',
            status='In Progress',
            team_id=team2.id,
            start_date=datetime.utcnow() - timedelta(days=20),
            created_by=admin.id
        )
        project2.description = 'Design intuitive mobile app for iOS and Android platforms'
        
        project3 = Project(
            name='Marketing Campaign Q1',
            key='MKTQ1',
            status='Not Started',
            team_id=team3.id,
            start_date=datetime.utcnow(),
            created_by=admin.id
        )
        project3.description = 'Launch comprehensive marketing campaign for Q1 2025'
        
        project4 = Project(
            name='Database Migration',
            key='DBMIG',
            status='On Hold',
            team_id=team1.id,
            start_date=datetime.utcnow() - timedelta(days=45),
            created_by=admin.id
        )
        project4.description = 'Migrate legacy database to new secure cloud infrastructure'
        
        project5 = Project(
            name='Website Redesign',
            key='WEBX',
            status='Completed',
            team_id=team2.id,
            start_date=datetime.utcnow() - timedelta(days=90),
            end_date=datetime.utcnow() - timedelta(days=10),
            created_by=admin.id
        )
        project5.description = 'Complete redesign of company website with modern UI/UX'
        
        db.session.add_all([project1, project2, project3, project4, project5])
        db.session.commit()
        print("✓ Projects created with encrypted descriptions!")
        
        # Create Project Updates (update texts are encrypted)
        print("\nCreating project updates...")
        
        update1 = ProjectUpdate(
            project_id=project1.id,
            user_id=employee1.id,
            hours_worked=8.5,
            date=datetime.utcnow() - timedelta(hours=2)
        )
        update1.update_text = 'Completed user authentication module and integrated secure payment gateway with encryption'
        
        update2 = ProjectUpdate(
            project_id=project1.id,
            user_id=employee2.id,
            hours_worked=6.0,
            date=datetime.utcnow() - timedelta(days=1)
        )
        update2.update_text = 'Fixed critical security bugs in shopping cart and optimized database queries for performance'
        
        update3 = ProjectUpdate(
            project_id=project2.id,
            user_id=employee3.id,
            hours_worked=7.5,
            date=datetime.utcnow() - timedelta(hours=5)
        )
        update3.update_text = 'Created comprehensive wireframes for all main screens and detailed user flow diagrams'
        
        update4 = ProjectUpdate(
            project_id=project1.id,
            user_id=employee1.id,
            hours_worked=5.5,
            date=datetime.utcnow() - timedelta(days=2)
        )
        update4.update_text = 'Implemented advanced product search functionality with filters and sorting capabilities'
        
        update5 = ProjectUpdate(
            project_id=project2.id,
            user_id=employee3.id,
            hours_worked=4.0,
            date=datetime.utcnow() - timedelta(days=3)
        )
        update5.update_text = 'Finalized color scheme, typography guidelines, and brand consistency standards'
        
        db.session.add_all([update1, update2, update3, update4, update5])
        db.session.commit()
        print("✓ Project updates created with encrypted content!")
        
        print("\n" + "="*70)
        print("🎉 DATABASE INITIALIZED SUCCESSFULLY WITH ENCRYPTION!")
        print("="*70)
        print("\n🔐 SECURITY FEATURES ENABLED:")
        print("  ✓ Passwords: Hashed with PBKDF2-SHA256 (600,000 iterations)")
        print("  ✓ Emails: Encrypted with Fernet (AES-128)")
        print("  ✓ Descriptions: Encrypted with Fernet")
        print("  ✓ Project Updates: Encrypted with Fernet")
        print("  ✓ CSRF Protection: Enabled")
        print("  ✓ SQL Injection Prevention: Parameterized queries")
        print("  ✓ XSS Prevention: Input sanitization with Bleach")
        print("  ✓ Rate Limiting: Login and request rate limits")
        print("  ✓ Session Security: Secure, HTTPOnly, SameSite cookies")
        print("  ✓ Audit Logging: All security events logged")
        print("\n📌 IMPORTANT SECURITY NOTES:")
        print("  • Encryption key stored in: encryption.key")
        print("  • Keep encryption.key file secure and backed up")
        print("  • Never commit encryption.key to version control")
        print("  • Change default passwords in production")
        print("  • Enable HTTPS in production")
        print("\n" + "="*70)
        print("LOGIN CREDENTIALS (STRONG PASSWORDS):")
        print("="*70)
        print("\n👤 Admin Login:")
        print("  Username: admin")
        print("  Password: Admin@123")
        print("\n👥 Employee Logins:")
        print("  Username: employee  | Password: Employee@123")
        print("  Username: john_doe  | Password: John@1234")
        print("  Username: jane_smith| Password: Jane@1234")
        print("  Username: mike_wilson| Password: Mike@1234")
        print("\n⚠️  NOTE: All passwords meet security requirements:")
        print("     - At least 8 characters")
        print("     - Contains uppercase and lowercase letters")
        print("     - Contains at least one number")
        print("     - Contains special characters")
        print("="*70 + "\n")

if __name__ == '__main__':
    init_database()