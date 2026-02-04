#!/usr/bin/env python
# create_sample_data.py - Create sample data matching the Jira images

from app import create_app
from models import (
    User, Team, Project, Issue, Epic, Label, Comment, Sprint,
    WorkflowTransition, IssueLink, Attachment, IssueWatcher, db
)
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

app = create_app('development')

def create_sample_data():
    """Create sample data for demonstration"""
    
    print("Creating sample data...")
    
    # Clean up existing data
    db.drop_all()
    db.create_all()
    print("✓ Database recreated")
    
    # Create users
    admin_user = User(
        username='admin',
        role='admin',
        avatar_color='#667eea'
    )
    admin_user.email = 'admin@example.com'
    admin_user.set_password('password123')
    
    user1 = User(
        username='john_doe',
        role='developer',
        avatar_color='#0c66e4'
    )
    user1.email = 'john@example.com'
    user1.set_password('password123')
    
    user2 = User(
        username='jane_smith',
        role='developer',
        avatar_color='#22a06b'
    )
    user2.email = 'jane@example.com'
    user2.set_password('password123')
    
    user3 = User(
        username='bob_wilson',
        role='designer',
        avatar_color='#e2b203'
    )
    user3.email = 'bob@example.com'
    user3.set_password('password123')
    
    db.session.add_all([admin_user, user1, user2, user3])
    db.session.commit()
    print("✓ Users created")
    
    # Create team
    team = Team(name='Beyond Gravity', description='Software development team')
    db.session.add(team)
    db.session.commit()
    print("✓ Team created")
    
    # Assign users to team
    admin_user.team_id = team.id
    user1.team_id = team.id
    user2.team_id = team.id
    user3.team_id = team.id
    db.session.commit()
    
    # Create projects
    project = Project(
        name='Lunar Rover',
        key='NUC',
        status='Active',
        workflow_type='agile',
        team_id=team.id,
        created_by=admin_user.id
    )
    project.description = 'Space exploration mission software'
    db.session.add(project)
    
    project2 = Project(
        name='E-Commerce Platform',
        key='SHOP',
        status='Active',
        workflow_type='agile',
        team_id=team.id,
        created_by=admin_user.id
    )
    project2.description = 'Next-generation online shopping platform'
    db.session.add(project2)
    
    project3 = Project(
        name='Mobile App Redesign',
        key='MOBILE',
        status='Planning',
        workflow_type='agile',
        team_id=team.id,
        created_by=admin_user.id
    )
    project3.description = 'Complete redesign of mobile application'
    db.session.add(project3)
    
    project4 = Project(
        name='Infrastructure Upgrade',
        key='INFRA',
        status='In Progress',
        workflow_type='agile',
        team_id=team.id,
        created_by=admin_user.id
    )
    project4.description = 'Cloud infrastructure modernization'
    db.session.add(project4)
    
    db.session.commit()
    print("✓ 4 Projects created")
    
    # Create sprints for each project
    sprint1 = Sprint(
        name='Sprint 1',
        project_id=project.id,
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=14),
        goal='Implement core features',
        status='active'
    )
    
    sprint2 = Sprint(
        name='Sprint 1',
        project_id=project2.id,
        start_date=datetime.utcnow() - timedelta(days=7),
        end_date=datetime.utcnow() + timedelta(days=7),
        goal='Payment integration',
        status='active'
    )
    
    sprint3 = Sprint(
        name='Sprint Planning',
        project_id=project3.id,
        start_date=datetime.utcnow() + timedelta(days=7),
        end_date=datetime.utcnow() + timedelta(days=21),
        goal='Design phase',
        status='planning'
    )
    
    sprint4 = Sprint(
        name='Phase 1',
        project_id=project4.id,
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=30),
        goal='AWS migration',
        status='active'
    )
    
    db.session.add_all([sprint1, sprint2, sprint3, sprint4])
    db.session.commit()
    print("✓ 4 Sprints created")
    
    # Create epics for each project
    epic1 = Epic(
        name='Web App Development',
        project_id=project.id,
        color='#0052cc',
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=60),
        status='active'
    )
    epic1.description = 'Build complete web application'
    
    epic2 = Epic(
        name='Payment System',
        project_id=project2.id,
        color='#ae2a19',
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=45),
        status='active'
    )
    epic2.description = 'Implement secure payment gateway'
    
    epic3 = Epic(
        name='Mobile UI Refresh',
        project_id=project3.id,
        color='#22a06b',
        start_date=datetime.utcnow() + timedelta(days=7),
        end_date=datetime.utcnow() + timedelta(days=90),
        status='planning'
    )
    epic3.description = 'Complete redesign of mobile interface'
    
    epic4 = Epic(
        name='Cloud Migration',
        project_id=project4.id,
        color='#ae7527',
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=60),
        status='active'
    )
    epic4.description = 'Migrate services to AWS'
    
    db.session.add_all([epic1, epic2, epic3, epic4])
    db.session.commit()
    print("✓ 4 Epics created")
    
    # Create labels for all projects
    labels_lunar = []
    labels_shop = []
    labels_mobile = []
    labels_infra = []
    
    label_configs = [
        ('ACCOUNTS', '#E2B203'),
        ('BILLING', '#AE2A19'),
        ('FORMS', '#8B2CA4'),
        ('FEEDBACK', '#FEC57B'),
    ]
    
    # Lunar Rover labels
    for name, color in label_configs:
        label = Label(name=name, color=color, project_id=project.id)
        labels_lunar.append(label)
        db.session.add(label)
    
    # E-Commerce labels
    shop_labels = [
        ('BUG', '#D3222C'),
        ('FEATURE', '#0052CC'),
        ('ENHANCEMENT', '#36B37E'),
    ]
    for name, color in shop_labels:
        label = Label(name=name, color=color, project_id=project2.id)
        labels_shop.append(label)
        db.session.add(label)
    
    # Mobile labels
    mobile_labels = [
        ('UI', '#5E4DB2'),
        ('ANDROID', '#00B341'),
        ('IOS', '#000000'),
    ]
    for name, color in mobile_labels:
        label = Label(name=name, color=color, project_id=project3.id)
        labels_mobile.append(label)
        db.session.add(label)
    
    # Infrastructure labels
    infra_labels = [
        ('AWS', '#FF9900'),
        ('SECURITY', '#AE2A19'),
        ('PERFORMANCE', '#22A06B'),
    ]
    for name, color in infra_labels:
        label = Label(name=name, color=color, project_id=project4.id)
        labels_infra.append(label)
        db.session.add(label)
    
    db.session.commit()
    print("✓ 12 Labels created for all projects")
    
    # Create issues for Lunar Rover (matching the images)
    issues_data = [
        # TO DO Column
        {
            'key': 'NUC-344',
            'title': 'Optimize experience for mobile web',
            'status': 'open',
            'priority': 'low',
            'type': 'task',
            'assignee': user2,
            'reporter': admin_user,
            'labels': [labels_lunar[0]],  # ACCOUNTS
            'points': 5,
            'project': project,
            'sprint': sprint1,
            'epic': epic1,
        },
        {
            'key': 'NUC-360',
            'title': 'Onboard workout options (OWO)',
            'status': 'todo',
            'priority': 'high',
            'type': 'task',
            'assignee': user1,
            'reporter': admin_user,
            'labels': [labels_lunar[0]],  # ACCOUNTS
            'points': 3,
            'project': project,
            'sprint': sprint1,
            'epic': epic1,
        },
        {
            'key': 'NUC-339',
            'title': 'Billing system integration - frontend',
            'status': 'todo',
            'priority': 'medium',
            'type': 'task',
            'assignee': user3,
            'reporter': admin_user,
            'labels': [labels_lunar[1], labels_lunar[2]],  # BILLING, FORMS
            'points': 3,
            'project': project,
            'sprint': sprint1,
            'epic': epic1,
        },
        {
            'key': 'NUC-341',
            'title': 'Quick payment',
            'status': 'todo',
            'priority': 'high',
            'type': 'task',
            'assignee': user2,
            'reporter': admin_user,
            'labels': [labels_lunar[3]],  # FEEDBACK
            'points': 3,
            'project': project,
            'sprint': sprint1,
            'epic': epic1,
        },
        
        # IN PROGRESS Column
        {
            'key': 'NUC-342',
            'title': 'Fast trip search',
            'status': 'in_progress',
            'priority': 'high',
            'type': 'story',
            'assignee': user1,
            'reporter': admin_user,
            'labels': [labels_lunar[0]],  # ACCOUNTS
            'points': 5,
            'project': project,
            'sprint': sprint1,
            'epic': epic1,
        },
        {
            'key': 'NUC-338',
            'title': 'Affiliate links integration - frontend',
            'status': 'in_progress',
            'priority': 'medium',
            'type': 'task',
            'assignee': user3,
            'reporter': admin_user,
            'labels': [labels_lunar[1]],  # BILLING
            'points': 2,
            'project': project,
            'sprint': sprint1,
            'epic': epic1,
        },
        {
            'key': 'NUC-336',
            'title': 'Quick booking for accommodations - website',
            'status': 'in_progress',
            'priority': 'high',
            'type': 'story',
            'assignee': user2,
            'reporter': admin_user,
            'labels': [labels_lunar[2]],  # FORMS
            'points': 5,
            'project': project,
            'sprint': sprint1,
            'epic': epic1,
        },
        {
            'key': 'NUC-346',
            'title': 'Adapt web app to new payments provider',
            'status': 'in_progress',
            'priority': 'low',
            'type': 'task',
            'assignee': user1,
            'reporter': admin_user,
            'labels': [labels_lunar[2]],  # FORMS
            'points': 2,
            'project': project,
            'sprint': sprint1,
            'epic': epic1,
        },
        {
            'key': 'NUC-343',
            'title': 'Fluid booking on tablets',
            'status': 'in_progress',
            'priority': 'medium',
            'type': 'bug',
            'assignee': user3,
            'reporter': admin_user,
            'labels': [labels_lunar[3]],  # FEEDBACK
            'points': 2,
            'project': project,
            'sprint': sprint1,
            'epic': epic1,
        },
        
        # IN REVIEW Column
        {
            'key': 'NUC-387',
            'title': 'Revise and streamline booking flow',
            'status': 'code_review',
            'priority': 'high',
            'type': 'story',
            'assignee': user2,
            'reporter': admin_user,
            'labels': [labels_lunar[0]],  # ACCOUNTS
            'points': 2,
            'project': project,
            'sprint': sprint1,
            'epic': epic1,
        },
        {
            'key': 'NUC-349',
            'title': 'Color of pale yellow on our pages looks incorrect',
            'status': 'code_review',
            'priority': 'low',
            'type': 'bug',
            'assignee': user3,
            'reporter': admin_user,
            'labels': [labels_lunar[3]],  # FEEDBACK
            'points': 1,
            'project': project,
            'sprint': sprint1,
            'epic': epic1,
        },
        
        # DONE Column
        {
            'key': 'NUC-345',
            'title': 'BugFix BG Web-store app crashing',
            'status': 'done',
            'priority': 'critical',
            'type': 'bug',
            'assignee': user1,
            'reporter': admin_user,
            'labels': [labels_lunar[2]],  # FORMS
            'points': 5,
            'project': project,
            'sprint': sprint1,
            'epic': epic1,
        },
        {
            'key': 'NUC-350',
            'title': 'Software bug fix for BG Web-store app crashing',
            'status': 'done',
            'priority': 'high',
            'type': 'bug',
            'assignee': user2,
            'reporter': admin_user,
            'labels': [labels_lunar[1]],  # BILLING
            'points': 3,
            'project': project,
            'sprint': sprint1,
            'epic': epic1,
        },
        {
            'key': 'NUC-351',
            'title': 'High outage: Software bug fix - BG Web-store app crashing',
            'status': 'done',
            'priority': 'critical',
            'type': 'bug',
            'assignee': user3,
            'reporter': admin_user,
            'labels': [labels_lunar[1]],  # BILLING
            'points': 4,
            'project': project,
            'sprint': sprint1,
            'epic': epic1,
        },
        {
            'key': 'NUC-352',
            'title': 'Web-store purchasing performance issue fix',
            'status': 'done',
            'priority': 'medium',
            'type': 'task',
            'assignee': user1,
            'reporter': admin_user,
            'labels': [labels_lunar[2]],  # FORMS
            'points': 3,
            'project': project,
            'sprint': sprint1,
            'epic': epic1,
        },
        
        # Additional E-Commerce issues
        {
            'key': 'SHOP-101',
            'title': 'Implement Stripe integration',
            'status': 'todo',
            'priority': 'high',
            'type': 'story',
            'assignee': user1,
            'reporter': admin_user,
            'labels': [labels_shop[1]],  # FEATURE
            'points': 8,
            'project': project2,
            'sprint': sprint2,
            'epic': epic2,
        },
        {
            'key': 'SHOP-102',
            'title': 'Cart abandonment email notifications',
            'status': 'in_progress',
            'priority': 'medium',
            'type': 'story',
            'assignee': user2,
            'reporter': admin_user,
            'labels': [labels_shop[1]],  # FEATURE
            'points': 5,
            'project': project2,
            'sprint': sprint2,
            'epic': epic2,
        },
        {
            'key': 'SHOP-103',
            'title': 'Fix mobile checkout freeze',
            'status': 'done',
            'priority': 'critical',
            'type': 'bug',
            'assignee': user3,
            'reporter': admin_user,
            'labels': [labels_shop[0]],  # BUG
            'points': 3,
            'project': project2,
            'sprint': sprint2,
            'epic': epic2,
        },
        
        # Mobile App issues
        {
            'key': 'MOBILE-201',
            'title': 'Redesign home screen layout',
            'status': 'todo',
            'priority': 'high',
            'type': 'story',
            'assignee': user2,
            'reporter': admin_user,
            'labels': [labels_mobile[0]],  # UI
            'points': 13,
            'project': project3,
            'sprint': sprint3,
            'epic': epic3,
        },
        {
            'key': 'MOBILE-202',
            'title': 'Android dark mode support',
            'status': 'todo',
            'priority': 'medium',
            'type': 'task',
            'assignee': user3,
            'reporter': admin_user,
            'labels': [labels_mobile[1]],  # ANDROID
            'points': 5,
            'project': project3,
            'sprint': sprint3,
            'epic': epic3,
        },
        {
            'key': 'MOBILE-203',
            'title': 'iOS app performance optimization',
            'status': 'todo',
            'priority': 'medium',
            'type': 'task',
            'assignee': user1,
            'reporter': admin_user,
            'labels': [labels_mobile[2]],  # IOS
            'points': 8,
            'project': project3,
            'sprint': sprint3,
            'epic': epic3,
        },
        
        # Infrastructure issues
        {
            'key': 'INFRA-301',
            'title': 'Migrate database to AWS RDS',
            'status': 'in_progress',
            'priority': 'high',
            'type': 'story',
            'assignee': user1,
            'reporter': admin_user,
            'labels': [labels_infra[0]],  # AWS
            'points': 21,
            'project': project4,
            'sprint': sprint4,
            'epic': epic4,
        },
        {
            'key': 'INFRA-302',
            'title': 'Setup VPN and security groups',
            'status': 'todo',
            'priority': 'high',
            'type': 'task',
            'assignee': user3,
            'reporter': admin_user,
            'labels': [labels_infra[1]],  # SECURITY
            'points': 5,
            'project': project4,
            'sprint': sprint4,
            'epic': epic4,
        },
        {
            'key': 'INFRA-303',
            'title': 'CloudFront CDN optimization',
            'status': 'todo',
            'priority': 'medium',
            'type': 'task',
            'assignee': user2,
            'reporter': admin_user,
            'labels': [labels_infra[2]],  # PERFORMANCE
            'points': 8,
            'project': project4,
            'sprint': sprint4,
            'epic': epic4,
        },
    ]
    
    # Create issues
    all_issues = []
    position_by_status = {}
    for issue_data in issues_data:
        status = issue_data['status']
        position = position_by_status.get(status, 0) + 1
        position_by_status[status] = position
        
        issue = Issue(
            key=issue_data['key'],
            title=issue_data['title'],
            project_id=issue_data['project'].id,
            epic_id=issue_data.get('epic').id if issue_data.get('epic') else None,
            sprint_id=issue_data.get('sprint').id if issue_data.get('sprint') else None,
            status=issue_data['status'],
            priority=issue_data['priority'],
            issue_type=issue_data['type'],
            assignee_id=issue_data['assignee'].id,
            reporter_id=issue_data['reporter'].id,
            story_points=issue_data['points'],
            position=position,
            time_estimate=issue_data['points'] * 4,  # Assume 4 hours per point
        )
        issue.labels = issue_data['labels']
        
        # Add some dates for timeline
        days_from_now = (position - 1) * 3
        issue.start_date = datetime.utcnow() + timedelta(days=days_from_now)
        issue.end_date = issue.start_date + timedelta(days=7)
        
        db.session.add(issue)
        all_issues.append(issue)
    
    db.session.commit()
    print(f"✓ Issues created ({len(all_issues)} issues across 4 projects)")
    
    # Create comments
    all_issues = Issue.query.filter_by(project_id=project.id).all()
    
    comment1 = Comment(
        issue_id=all_issues[0].id,
        user_id=user1.id,
        text='I think we should prioritize this for the next sprint.'
    )
    
    comment2 = Comment(
        issue_id=all_issues[1].id,
        user_id=user2.id,
        text='Already started working on this. Should be ready by Friday.'
    )
    
    comment3 = Comment(
        issue_id=all_issues[2].id,
        user_id=user3.id,
        text='Need design approval before proceeding.'
    )
    
    db.session.add_all([comment1, comment2, comment3])
    db.session.commit()
    print("✓ Comments created")
    
    # Create workflow transitions
    transitions = [
        WorkflowTransition(
            issue_id=all_issues[11].id,
            from_status='open',
            to_status='in_progress',
            user_id=user1.id,
            comment='Starting work on this'
        ),
        WorkflowTransition(
            issue_id=all_issues[11].id,
            from_status='in_progress',
            to_status='code_review',
            user_id=user1.id,
            comment='Ready for review'
        ),
        WorkflowTransition(
            issue_id=all_issues[11].id,
            from_status='code_review',
            to_status='done',
            user_id=user2.id,
            comment='Approved and merged'
        ),
    ]
    
    db.session.add_all(transitions)
    db.session.commit()
    print("✓ Workflow transitions created")
    
    # Create issue links (dependencies)
    if len(all_issues) > 8:
        # NUC-342 blocks NUC-346
        link1 = IssueLink(
            source_issue_id=all_issues[4].id,
            target_issue_id=all_issues[7].id,
            link_type='blocks'
        )
        
        # NUC-336 relates to NUC-343
        link2 = IssueLink(
            source_issue_id=all_issues[6].id,
            target_issue_id=all_issues[8].id,
            link_type='relates_to'
        )
        
        db.session.add_all([link1, link2])
        db.session.commit()
    print("✓ Issue links created")
    
    # Create watchers
    if len(all_issues) > 4:
        watch1 = IssueWatcher(
            issue_id=all_issues[0].id,
            user_id=user2.id
        )
        
        watch2 = IssueWatcher(
            issue_id=all_issues[4].id,
            user_id=user3.id
        )
        
        db.session.add_all([watch1, watch2])
        db.session.commit()
    print("✓ Watchers created")
    
    print("\n" + "="*70)
    print("✓ COMPREHENSIVE SAMPLE DATA CREATED SUCCESSFULLY!")
    print("="*70)
    print("\n📊 PROJECTS CREATED:")
    print(f"  ✓ Lunar Rover (NUC) - Space exploration software")
    print(f"  ✓ E-Commerce Platform (SHOP) - Online shopping platform")
    print(f"  ✓ Mobile App Redesign (MOBILE) - App redesign project")
    print(f"  ✓ Infrastructure Upgrade (INFRA) - Cloud infrastructure")
    print(f"\n📋 CONTENT SUMMARY:")
    print(f"  • Total Issues: {len(all_issues)}")
    print(f"    - Lunar Rover: 15 issues")
    print(f"    - E-Commerce: 3 issues")
    print(f"    - Mobile App: 3 issues")
    print(f"    - Infrastructure: 3 issues")
    print(f"  • Total Sprints: 4")
    print(f"  • Total Epics: 4")
    print(f"  • Total Labels: 12")
    print(f"\n👥 TEST USERS (Password: password123):")
    print(f"  ✓ admin (Admin role)")
    print(f"  ✓ john_doe (Developer)")
    print(f"  ✓ jane_smith (Developer)")
    print(f"  ✓ bob_wilson (Designer)")
    print(f"\n👨‍💼 TEAM:")
    print(f"  ✓ Beyond Gravity - 4 members")
    print(f"\n" + "="*70)
    print("Ready to login and explore all projects!")
    print("="*70 + "\n")

if __name__ == '__main__':
    with app.app_context():
        create_sample_data()
