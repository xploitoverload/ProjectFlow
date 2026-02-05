#!/usr/bin/env python3
"""
Create a sample user report for demonstration
Shows the reporting system in action
"""

from app import create_app
from models import User, Project, ProjectUpdate, db
from app.services import ReportService
from datetime import datetime

app = create_app('development')

def create_sample_report():
    """Create a sample report for demonstration"""
    
    with app.app_context():
        print("Creating sample user report...")
        print("=" * 70)
        
        # Get first user and project
        user = User.query.first()
        project = Project.query.first()
        
        if not user:
            print("❌ No users found. Please create users first.")
            return
            
        if not project:
            print("❌ No projects found. Please create projects first.")
            return
        
        print(f"\n📝 Report Details:")
        print(f"  User: {user.username} ({user.full_name})")
        print(f"  Project: {project.name}")
        print(f"  Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Create report using ReportService
        success, update, message = ReportService.create_status_update(
            project_id=project.id,
            user_id=user.id,
            description="Completed API integration and database schema updates. All core functionality is working. "
                       "Successfully implemented user authentication, project management, and reporting features.",
            status='on_track',
            progress=85,
            hours_worked=8.5,
            blockers="Waiting on design assets for dashboard UI",
            notes="All backend tests passing. Frontend integration in progress.",
            team_members=3,
            completion_days=3,
            reporting_period='daily'
        )
        
        if success:
            print(f"\n✅ Report created successfully!")
            print(f"\n📊 Report Information:")
            print(f"  ID: {update.id}")
            print(f"  Status: {update.status.upper()}")
            print(f"  Progress: {update.progress_percentage}%")
            print(f"  Hours Worked: {update.hours_worked}")
            print(f"  Team Members: {update.team_members_count}")
            print(f"  Days to Complete: {update.estimated_completion_days}")
            print(f"  Period: {update.reporting_period.upper()}")
            print(f"\n📝 Description:")
            print(f"  {update.update_text[:100]}...")
            print(f"\n🚫 Blockers:")
            print(f"  {update.blockers}")
            
            # Show how to retrieve it
            print(f"\n" + "=" * 70)
            print(f"📚 How to view this report:")
            print(f"\n  1. Go to: http://127.0.0.1:5000/reports")
            print(f"  2. Login as: {user.username}")
            print(f"  3. You'll see this report in your list")
            print(f"\n  Filter Options:")
            print(f"    • Today - shows last 24 hours")
            print(f"    • This Week - shows last 7 days")
            print(f"    • This Month - shows last 30 days")
            print(f"    • All Time - shows all reports")
            
            # Show statistics
            print(f"\n" + "=" * 70)
            print(f"📊 Your Updated Statistics:")
            stats = ReportService.get_user_statistics(user.id, 'all')
            print(f"  Total Reports: {stats['total']}")
            print(f"  On Track: {stats['on_track']}")
            print(f"  At Risk: {stats['at_risk']}")
            print(f"  Blocked: {stats['blocked']}")
            print(f"  Avg Progress: {stats['avg_progress']}%")
            print(f"  Total Hours: {stats['total_hours']}")
            
            print(f"\n" + "=" * 70)
            print(f"✨ Report system is working perfectly!")
            
        else:
            print(f"\n❌ Failed to create report: {message}")


if __name__ == '__main__':
    create_sample_report()
