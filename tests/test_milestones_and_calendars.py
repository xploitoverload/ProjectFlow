# tests/test_milestones_and_calendars.py
"""
Working Calendars & Milestone Management Tests
Verifies working day rules, weekend skipping, holiday exceptions,
milestone lifecycle, overdue detection, and API endpoints.
"""

import pytest
import json
from datetime import date, datetime, timedelta
from models import db, Milestone, WorkingCalendar, Project, User
from app.services.scheduling_service import SchedulingService


def test_working_calendar_rules_and_calculations(app, test_project):
    """Test working calendar day checks, weekend skipping, and holiday additions."""
    with app.app_context():
        cal = SchedulingService.get_or_create_calendar(test_project.id)
        assert cal is not None
        assert cal.hours_per_day == 8.0

        # Configure custom holidays
        # Nov 6 2026 is Friday, Nov 7 is Sat, Nov 8 is Sun, Nov 9 is Mon (Holiday)
        cal.holidays_json = json.dumps(['2026-11-09'])
        db.session.commit()

        fri = date(2026, 11, 6)
        sat = date(2026, 11, 7)
        sun = date(2026, 11, 8)
        mon = date(2026, 11, 9)
        tue = date(2026, 11, 10)

        # 1. Check working day status
        assert cal.is_working_day(fri) is True
        assert cal.is_working_day(sat) is False  # Weekend
        assert cal.is_working_day(sun) is False  # Weekend
        assert cal.is_working_day(mon) is False  # Holiday exception
        assert cal.is_working_day(tue) is True

        # 2. Add working days:
        # Starting Friday Nov 6, add 2 working days:
        # Day 1: Tuesday Nov 10 (skips Sat, Sun, Mon holiday)
        # Day 2: Wednesday Nov 11
        result_d = cal.add_working_days(fri, 2)
        assert result_d == date(2026, 11, 11)

        # 3. Working days between Nov 6 and Nov 11 inclusive:
        # Nov 6 (Fri): 1
        # Nov 7 (Sat): 0
        # Nov 8 (Sun): 0
        # Nov 9 (Mon holiday): 0
        # Nov 10 (Tue): 1
        # Nov 11 (Wed): 1
        # Total = 3 working days
        cnt = cal.working_days_between(fri, date(2026, 11, 11))
        assert cnt == 3


def test_milestone_lifecycle_and_overdue_detection(app, admin_user, test_project):
    """Test creating, editing, overdue checking, and deleting delivery milestones."""
    with app.app_context():
        # 1. Create future milestone
        future_date = date.today() + timedelta(days=14)
        ok, m1, msg = SchedulingService.create_milestone(
            project_id=test_project.id,
            name='Alpha Release Milestone',
            target_date=future_date,
            description='Kernel architecture signoff',
            owner_id=admin_user.id,
            created_by=admin_user.id
        )
        assert ok is True
        assert m1.is_overdue is False
        assert m1.status == 'open'

        # 2. Create past milestone (overdue)
        past_date = date.today() - timedelta(days=5)
        ok, m2, msg = SchedulingService.create_milestone(
            project_id=test_project.id,
            name='Overdue Deliverable',
            target_date=past_date,
            owner_id=admin_user.id
        )
        assert ok is True
        assert m2.is_overdue is True

        # 3. Mark m2 completed -> is_overdue becomes False
        ok, m2_updated, msg = SchedulingService.update_milestone(
            milestone_id=m2.id,
            data={'status': 'completed'},
            updated_by=admin_user.id
        )
        assert ok is True
        assert m2_updated.status == 'completed'
        assert m2_updated.completed_at is not None
        assert m2_updated.is_overdue is False

        # 4. List project milestones
        all_m = SchedulingService.get_project_milestones(test_project.id)
        assert len(all_m) >= 2

        # 5. Delete milestone
        ok, del_msg = SchedulingService.delete_milestone(m2.id, deleted_by=admin_user.id)
        assert ok is True
        assert Milestone.query.get(m2.id) is None


def test_milestone_and_calendar_api_endpoints(client, admin_user, test_project):
    """Test Milestone and Working Calendar REST APIs."""
    with client.session_transaction() as sess:
        sess['user_id'] = admin_user.id
        sess['_fresh'] = True

    # 1. Create milestone via API
    resp = client.post(f'/api/v1/project/{test_project.id}/milestones', json={
        'name': 'API Production Milestone',
        'target_date': '2026-12-01',
        'description': 'Production deployment milestone'
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data['success'] is True
    m_id = data['milestone']['id']

    # 2. Get milestones
    resp = client.get(f'/api/v1/project/{test_project.id}/milestones')
    assert resp.status_code == 200
    assert len(resp.get_json()['milestones']) >= 1

    # 3. Update milestone
    resp = client.put(f'/api/v1/project/{test_project.id}/milestones/{m_id}', json={
        'status': 'completed'
    })
    assert resp.status_code == 200
    assert resp.get_json()['milestone']['status'] == 'completed'

    # 4. Get working calendar
    resp = client.get(f'/api/v1/project/{test_project.id}/calendar')
    assert resp.status_code == 200
    cal_data = resp.get_json()['calendar']
    assert cal_data['hours_per_day'] == 8.0

    # 5. Update working calendar
    resp = client.post(f'/api/v1/project/{test_project.id}/calendar', json={
        'hours_per_day': 7.5,
        'working_days': '0,1,2,3,4,5',  # 6-day work week
        'holidays': ['2026-12-25']
    })
    assert resp.status_code == 200
    assert resp.get_json()['calendar']['hours_per_day'] == 7.5

    # 6. Delete milestone
    resp = client.delete(f'/api/v1/project/{test_project.id}/milestones/{m_id}')
    assert resp.status_code == 200
    assert resp.get_json()['success'] is True
