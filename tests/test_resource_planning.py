import pytest
from datetime import date, timedelta
from app.models import db, User, Team, Project, Issue
from app.services.resource_service import ResourceService

def test_task_hours_calculation_and_fallbacks(app, test_project):
    with app.app_context():
        # Case 1: time_estimate present
        i1 = Issue(project_id=test_project.id, key="RP-1", title="Task 1", time_estimate=12.5)
        # Case 2: story_points present (5 pts * 8h = 40h)
        i2 = Issue(project_id=test_project.id, key="RP-2", title="Task 2", story_points=5)
        # Case 3: neither present (default 8h)
        i3 = Issue(project_id=test_project.id, key="RP-3", title="Task 3")

        assert ResourceService.calculate_task_hours(i1) == 12.5
        assert ResourceService.calculate_task_hours(i2) == 40.0
        assert ResourceService.calculate_task_hours(i3) == 8.0


def test_user_workload_and_overallocation_detection(app, test_project):
    with app.app_context():
        # Create user
        u = User(username="dev_capacity", role="developer", email="dev@test.com")
        u.set_password("DevPass123!")
        db.session.add(u)
        db.session.commit()

        start = date(2026, 9, 1) # Tuesday
        end = date(2026, 9, 7)   # Monday -> 5 working days = 40 hours

        # Assign 3 tasks:
        # Task 1: 20h
        t1 = Issue(project_id=test_project.id, key="DEV-1", title="Task A", assignee_id=u.id, status="in_progress", time_estimate=20.0, start_date=start, due_date=end)
        # Task 2: 30h -> Total 50h on 40h capacity -> 125% over-allocated!
        t2 = Issue(project_id=test_project.id, key="DEV-2", title="Task B", assignee_id=u.id, status="todo", time_estimate=30.0, start_date=start, due_date=end)
        # Task 3: 15h, but status="done" -> Should not count in remaining workload
        t3 = Issue(project_id=test_project.id, key="DEV-3", title="Task C", assignee_id=u.id, status="done", time_estimate=15.0, start_date=start, due_date=end)

        db.session.add_all([t1, t2, t3])
        db.session.commit()

        workload, err = ResourceService.get_user_workload(u.id, start_date=start, end_date=end)
        assert err is None
        assert workload['capacity_hours'] == 40.0
        assert workload['allocated_hours'] == 50.0 # t1 + t2
        assert workload['remaining_hours'] == 50.0
        assert workload['utilization_percentage'] == 125.0
        assert workload['allocation_status'] == 'over_allocated'
        assert workload['is_over_allocated'] is True
        assert workload['assigned_tasks_count'] == 2


def test_team_capacity_aggregation(app, test_project):
    with app.app_context():
        # Create team
        team = Team(name="Alpha Core Team", department="Engineering", color="#6366F1")
        db.session.add(team)
        db.session.commit()

        # Create 2 team members
        u1 = User(username="alpha_dev1", role="developer", email="alpha1@test.com", team_id=team.id)
        u1.set_password("Pass123!")
        u2 = User(username="alpha_dev2", role="developer", email="alpha2@test.com", team_id=team.id)
        u2.set_password("Pass123!")
        db.session.add_all([u1, u2])
        db.session.commit()

        start = date(2026, 10, 5) # Monday
        end = date(2026, 10, 9)   # Friday -> 40h capacity each, 80h team capacity

        # Dev1: 20h (50% optimal)
        t1 = Issue(project_id=test_project.id, key="ALPHA-1", title="Feature A", assignee_id=u1.id, status="todo", time_estimate=20.0, start_date=start, due_date=end)
        # Dev2: 48h (120% over-allocated)
        t2 = Issue(project_id=test_project.id, key="ALPHA-2", title="Feature B", assignee_id=u2.id, status="in_progress", time_estimate=48.0, start_date=start, due_date=end)
        db.session.add_all([t1, t2])
        db.session.commit()

        team_cap, err = ResourceService.get_team_capacity(team.id, start_date=start, end_date=end)
        assert err is None
        assert team_cap['total_capacity_hours'] == 80.0
        assert team_cap['total_remaining_hours'] == 68.0
        assert team_cap['team_utilization_percentage'] == 85.0
        assert team_cap['over_allocated_members_count'] == 1
        assert len(team_cap['members']) == 2


def test_project_resource_utilization_api(client, app, admin_user, test_project):
    with app.app_context():
        start = date(2026, 11, 2)
        end = date(2026, 11, 6)
        
        # Assigned task
        i1 = Issue(project_id=test_project.id, key="PRU-1", title="Assigned Task", assignee_id=admin_user.id, status="todo", time_estimate=16.0, start_date=start, due_date=end)
        # Unassigned task
        i2 = Issue(project_id=test_project.id, key="PRU-2", title="Unassigned Task", assignee_id=None, status="todo", time_estimate=8.0, start_date=start, due_date=end)
        db.session.add_all([i1, i2])
        db.session.commit()

    with client.session_transaction() as sess:
        sess['user_id'] = admin_user.id

    # 1. GET Project Resource Capacity
    res = client.get(f'/api/v1/project/{test_project.id}/resources/capacity?start_date=2026-11-02&end_date=2026-11-06')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    rp = data['resource_planning']
    assert rp['unassigned_tasks_count'] >= 1
    assert rp['unassigned_hours'] >= 8.0
    assert len(rp['resources']) >= 1

    # 2. GET User Resource Workload
    res = client.get(f'/api/v1/user/{admin_user.id}/resources/workload?start_date=2026-11-02&end_date=2026-11-06')
    assert res.status_code == 200
    u_data = res.get_json()
    assert u_data['success'] is True
    assert u_data['user_workload']['assigned_tasks_count'] >= 1
