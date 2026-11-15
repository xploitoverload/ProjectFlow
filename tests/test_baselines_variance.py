import json
from datetime import date, timedelta
import pytest
from app.models import db, User, Project, Issue, Milestone, ScheduleBaseline
from app.services.scheduling_service import SchedulingService

def test_baseline_creation_and_snapshot_immutability(app, test_project):
    with app.app_context():
        p = Project.query.get(test_project.id)
        start = date(2026, 6, 1)
        i1 = Issue(project_id=p.id, key="BTP-1", title="Task 1", status="todo", start_date=start, due_date=start + timedelta(days=4))
        i2 = Issue(project_id=p.id, key="BTP-2", title="Task 2", status="in_progress", start_date=start + timedelta(days=5), due_date=start + timedelta(days=9))
        m1 = Milestone(project_id=p.id, name="Sprint 1 Gate", target_date=start + timedelta(days=10))
        db.session.add_all([i1, i2, m1])
        db.session.commit()

        # Create baseline
        ok, baseline, msg = SchedulingService.create_baseline(p.id, "Initial Baseline", "Initial schedule plan")
        assert ok is True
        assert baseline.name == "Initial Baseline"
        
        snap = baseline.get_snapshot()
        assert len(snap['tasks']) >= 2
        assert len(snap['milestones']) >= 1
        
        # Verify initial dates in snapshot
        t1_snap = [t for t in snap['tasks'] if t['key'] == "BTP-1"][0]
        assert t1_snap['start_date'] == "2026-06-01"
        assert t1_snap['due_date'] == "2026-06-05"
        assert t1_snap['duration'] == 5

        # Now mutate current issue dates
        i1.due_date = start + timedelta(days=7) # Delayed by 3 days
        db.session.commit()

        # Verify snapshot data did NOT change (immutability)
        snap_after = baseline.get_snapshot()
        t1_snap_after = [t for t in snap_after['tasks'] if t['key'] == "BTP-1"][0]
        assert t1_snap_after['due_date'] == "2026-06-05"


def test_schedule_variance_calculation(app, test_project):
    with app.app_context():
        p = Project(name="Variance Project", key="VAR", status="active")
        db.session.add(p)
        db.session.commit()

        start = date(2026, 7, 1)
        # Task 1: 5 days
        i1 = Issue(project_id=p.id, key="VAR-1", title="Delayed Task", status="in_progress", start_date=start, due_date=start + timedelta(days=4))
        # Task 2: 5 days
        i2 = Issue(project_id=p.id, key="VAR-2", title="Ahead Task", status="done", start_date=start, due_date=start + timedelta(days=4))
        # Task 3: 5 days
        i3 = Issue(project_id=p.id, key="VAR-3", title="On Track Task", status="todo", start_date=start, due_date=start + timedelta(days=4))
        # Milestone
        m1 = Milestone(project_id=p.id, name="Alpha", target_date=start + timedelta(days=5))
        db.session.add_all([i1, i2, i3, m1])
        db.session.commit()

        ok, baseline, _ = SchedulingService.create_baseline(p.id, "Plan A")
        assert ok is True

        # Now induce schedule drift:
        # i1 delayed by 4 days
        i1.due_date = start + timedelta(days=8)
        # i2 finished 2 days ahead
        i2.due_date = start + timedelta(days=2)
        # i3 stays exactly same
        # Milestone drifted by 3 days
        m1.target_date = start + timedelta(days=8)
        db.session.commit()

        comparison, err = SchedulingService.compare_baseline(p.id, baseline.id)
        assert err is None
        assert comparison is not None

        summary = comparison['summary']
        assert summary['delayed_tasks_count'] == 1
        assert summary['ahead_tasks_count'] == 1
        assert summary['on_track_tasks_count'] == 1
        assert summary['max_task_delay_days'] == 4

        # Check individual task variances
        task_vars = {t['key']: t for t in comparison['task_variances']}
        assert task_vars['VAR-1']['finish_variance_days'] == 4
        assert task_vars['VAR-1']['variance_category'] == 'delayed'

        assert task_vars['VAR-2']['finish_variance_days'] == -2
        assert task_vars['VAR-2']['variance_category'] == 'ahead'

        assert task_vars['VAR-3']['finish_variance_days'] == 0
        assert task_vars['VAR-3']['variance_category'] == 'on_track'

        # Check milestone variance
        m_var = comparison['milestone_variances'][0]
        assert m_var['name'] == 'Alpha'
        assert m_var['variance_days'] == 3


def test_baseline_api_endpoints(client, app, admin_user, test_project):
    project_id = test_project.id
    with app.app_context():
        start = date(2026, 8, 1)
        i = Issue(project_id=project_id, key="ABP-1", title="API Task", status="todo", start_date=start, due_date=start + timedelta(days=3))
        db.session.add(i)
        db.session.commit()

    # Log in as admin
    with client.session_transaction() as sess:
        sess['user_id'] = admin_user.id

    # 1. POST create baseline
    res = client.post(f'/api/v1/project/{project_id}/baselines', json={
        'name': 'API Baseline 1',
        'description': 'Baseline via API'
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data['success'] is True
    baseline_id = data['baseline']['id']

    # 2. GET list baselines
    res = client.get(f'/api/v1/project/{project_id}/baselines')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert len(data['baselines']) >= 1

    # 3. GET compare baseline
    res = client.get(f'/api/v1/project/{project_id}/baselines/{baseline_id}/compare')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert 'comparison' in data
    assert data['comparison']['summary']['tracked_tasks'] >= 1

    # 4. DELETE baseline
    res = client.delete(f'/api/v1/project/{project_id}/baselines/{baseline_id}')
    assert res.status_code == 200
    assert res.get_json()['success'] is True

    # Verify deleted
    res = client.get(f'/api/v1/project/{project_id}/baselines')
    assert len(res.get_json()['baselines']) == 0
