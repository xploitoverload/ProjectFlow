# tests/test_scheduling_cpm.py
"""
Critical Path Method (CPM) & Scheduling Intelligence Tests
Verifies forward pass (ES, EF), backward pass (LS, LF), Total Float, Free Float,
Critical Path identification, bottleneck detection, cycle prevention,
and preview-before-commit auto-scheduling.
"""

import pytest
from datetime import date, timedelta
from models import db, Issue, IssueLink, Project
from app.services.scheduling_service import SchedulingService, to_date


def test_cpm_forward_backward_pass_and_float_calculation(app, admin_user, test_project):
    """
    Test standard project network with two converging paths:
    Path 1: A (5d, Nov 1-5) -> B (3d, Nov 6-8) -> D (4d, Nov 9-12)  => Total: 12 days
    Path 2: A (5d, Nov 1-5) -> C (6d, Nov 6-11) -> E (2d, Nov 12-13) => Total: 13 days (CRITICAL)
    
    Expected:
    - Overall project duration: 13 days
    - Critical Path: A, C, E (Total Float = 0)
    - Non-critical tasks: B, D (Total Float = 1 day)
    """
    with app.app_context():
        # Setup tasks
        a = Issue(key='CPM-A', title='Task A (Foundation)', project_id=test_project.id, start_date=date(2026, 11, 1), due_date=date(2026, 11, 5))
        b = Issue(key='CPM-B', title='Task B (Subsystem 1)', project_id=test_project.id, start_date=date(2026, 11, 6), due_date=date(2026, 11, 8))
        c = Issue(key='CPM-C', title='Task C (Subsystem 2 - Heavy)', project_id=test_project.id, start_date=date(2026, 11, 6), due_date=date(2026, 11, 11))
        d = Issue(key='CPM-D', title='Task D (Integration 1)', project_id=test_project.id, start_date=date(2026, 11, 9), due_date=date(2026, 11, 12))
        e = Issue(key='CPM-E', title='Task E (Final Verification)', project_id=test_project.id, start_date=date(2026, 11, 12), due_date=date(2026, 11, 13))
        
        db.session.add_all([a, b, c, d, e])
        db.session.commit()

        # Dependencies: A->B, A->C, B->D, C->E
        db.session.add_all([
            IssueLink(source_issue_id=a.id, target_issue_id=b.id, link_type='finish_to_start', lag_days=0),
            IssueLink(source_issue_id=a.id, target_issue_id=c.id, link_type='finish_to_start', lag_days=0),
            IssueLink(source_issue_id=b.id, target_issue_id=d.id, link_type='finish_to_start', lag_days=0),
            IssueLink(source_issue_id=c.id, target_issue_id=e.id, link_type='finish_to_start', lag_days=0),
        ])
        db.session.commit()

        res = SchedulingService.calculate_critical_path(test_project.id)
        assert res['success'] is True
        assert res['project_duration_days'] == 13
        assert res['project_start_date'] == '2026-11-01'
        assert res['project_end_date'] == '2026-11-13'

        metrics = res['task_metrics']
        
        # Verify Critical Tasks: A, C, E have Total Float == 0
        assert metrics[a.id]['is_critical'] is True
        assert metrics[a.id]['total_float'] == 0
        assert metrics[c.id]['is_critical'] is True
        assert metrics[c.id]['total_float'] == 0
        assert metrics[e.id]['is_critical'] is True
        assert metrics[e.id]['total_float'] == 0

        # Verify Non-critical tasks: B, D have Total Float == 1
        assert metrics[b.id]['is_critical'] is False
        assert metrics[b.id]['total_float'] == 1
        assert metrics[d.id]['is_critical'] is False
        assert metrics[d.id]['total_float'] == 1

        # Check critical path sequence
        crit_ids = res['critical_path_issue_ids']
        assert a.id in crit_ids
        assert c.id in crit_ids
        assert e.id in crit_ids
        assert b.id not in crit_ids
        assert d.id not in crit_ids


def test_cpm_dependency_types_and_lag(app, admin_user, test_project):
    """
    Test Start-to-Start (SS) and Finish-to-Finish (FF) dependencies with lag days.
    Task P (Nov 1-10, 10d)
    Task S1: SS with P, lag=2 => ES_S1 >= P_ES + 2d = Nov 3
    Task S2: FF with P, lag=3 => EF_S2 >= P_EF + 3d = Nov 13
    """
    with app.app_context():
        p = Issue(key='LAG-P', title='Parent Process', project_id=test_project.id, start_date=date(2026, 11, 1), due_date=date(2026, 11, 10))
        s1 = Issue(key='LAG-S1', title='Start Aligned Task', project_id=test_project.id, start_date=date(2026, 11, 1), due_date=date(2026, 11, 4)) # 4d duration
        s2 = Issue(key='LAG-S2', title='Finish Aligned Task', project_id=test_project.id, start_date=date(2026, 11, 5), due_date=date(2026, 11, 9)) # 5d duration
        db.session.add_all([p, s1, s2])
        db.session.commit()

        # P --(start_to_start, lag=2)--> S1
        # P --(finish_to_finish, lag=3)--> S2
        db.session.add_all([
            IssueLink(source_issue_id=p.id, target_issue_id=s1.id, link_type='start_to_start', lag_days=2),
            IssueLink(source_issue_id=p.id, target_issue_id=s2.id, link_type='finish_to_finish', lag_days=3)
        ])
        db.session.commit()

        res = SchedulingService.calculate_critical_path(test_project.id)
        assert res['success'] is True
        m = res['task_metrics']

        # S1 ES must be Nov 03 (Nov 01 + 2d)
        assert m[s1.id]['es'] == '2026-11-03'
        # S2 EF must be Nov 13 (Nov 10 + 3d)
        assert m[s2.id]['ef'] == '2026-11-13'


def test_cpm_cycle_prevention(app, admin_user, test_project):
    """Test CPM safely identifies and handles circular dependencies."""
    with app.app_context():
        t1 = Issue(key='CYC-1', title='Cycle 1', project_id=test_project.id, start_date=date(2026, 11, 1), due_date=date(2026, 11, 3))
        t2 = Issue(key='CYC-2', title='Cycle 2', project_id=test_project.id, start_date=date(2026, 11, 4), due_date=date(2026, 11, 6))
        db.session.add_all([t1, t2])
        db.session.commit()

        # Force a cycle directly in DB
        db.session.add_all([
            IssueLink(source_issue_id=t1.id, target_issue_id=t2.id, link_type='finish_to_start'),
            IssueLink(source_issue_id=t2.id, target_issue_id=t1.id, link_type='finish_to_start')
        ])
        db.session.commit()

        res = SchedulingService.calculate_critical_path(test_project.id)
        assert res['success'] is False
        assert 'Circular dependency chain detected' in res['error']


def test_preview_and_commit_auto_schedule(app, admin_user, test_project):
    """Test previewing proposed shifts before committing, then committing transactionally."""
    with app.app_context():
        # Setup conflicting schedule
        # Predecessor A finishes Nov 10
        # Successor B starts Nov 5 (5 days overlap / conflict!)
        t_a = Issue(key='PREV-A', title='Task Predecessor', project_id=test_project.id, start_date=date(2026, 11, 1), due_date=date(2026, 11, 10))
        t_b = Issue(key='PREV-B', title='Task Successor', project_id=test_project.id, start_date=date(2026, 11, 5), due_date=date(2026, 11, 8)) # 4d duration
        db.session.add_all([t_a, t_b])
        db.session.commit()

        db.session.add(IssueLink(source_issue_id=t_a.id, target_issue_id=t_b.id, link_type='finish_to_start', lag_days=0))
        db.session.commit()

        # 1. Preview: Should propose moving B to Nov 11 - Nov 14 (preserving 4d duration)
        preview = SchedulingService.preview_auto_schedule(test_project.id)
        assert preview['success'] is True
        assert preview['total_shifts'] >= 1
        
        b_prop = next(p for p in preview['proposals'] if p['issue_id'] == t_b.id)
        assert b_prop['proposed_start'] == '2026-11-11'
        assert b_prop['proposed_due'] == '2026-11-14'

        # Verify DB was NOT modified by preview
        fresh_b = Issue.query.get(t_b.id)
        assert to_date(fresh_b.start_date) == date(2026, 11, 5)

        # 2. Commit: Now apply the previewed schedule
        ok, msg, applied = SchedulingService.commit_auto_schedule(test_project.id, updated_by=admin_user.id)
        assert ok is True
        assert applied >= 1

        # Verify DB is now updated
        updated_b = Issue.query.get(t_b.id)
        assert to_date(updated_b.start_date) == date(2026, 11, 11)
        assert to_date(updated_b.due_date) == date(2026, 11, 14)


def test_cpm_api_endpoints(client, admin_user, test_project):
    """Test CPM, auto-schedule preview, and commit API endpoints with auth."""
    # Login
    with client.session_transaction() as sess:
        sess['user_id'] = admin_user.id
        sess['_fresh'] = True

    # 1. GET /cpm
    resp = client.get(f'/api/v1/project/{test_project.id}/cpm')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert 'critical_path_issue_ids' in data

    # 2. GET /auto_schedule/preview
    resp = client.get(f'/api/v1/project/{test_project.id}/auto_schedule/preview')
    assert resp.status_code == 200
    p_data = resp.get_json()
    assert p_data['success'] is True
    assert 'proposals' in p_data

    # 3. POST /auto_schedule/commit
    resp = client.post(f'/api/v1/project/{test_project.id}/auto_schedule/commit')
    assert resp.status_code == 200
    c_data = resp.get_json()
    assert c_data['success'] is True
