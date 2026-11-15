import pytest
from datetime import datetime, date, timedelta
from app.models import db, User, Project, Issue, IssueLink
from app.services.issue_service import IssueService, check_schedule_constraint


def test_ordinary_relationships_and_canonical_mapping(app, admin_user, test_project):
    """Test all ordinary issue relationship types with inverse labels and canonical mapping."""
    with app.app_context():
        i1 = Issue(key='ORD-1', title='Issue 1', project_id=test_project.id, status='todo')
        i2 = Issue(key='ORD-2', title='Issue 2', project_id=test_project.id, status='todo')
        i3 = Issue(key='ORD-3', title='Issue 3', project_id=test_project.id, status='todo')
        db.session.add_all([i1, i2, i3])
        db.session.commit()

        # 1. Relates to (symmetric)
        ok, link_rel, msg = IssueService.link_issues(i1.id, i2.id, 'relates_to', created_by=admin_user.id)
        assert ok is True
        assert link_rel.is_relationship is True
        assert link_rel.is_dependency is False
        
        # Prevent symmetric duplicate for relates_to
        ok_dup, _, err = IssueService.link_issues(i2.id, i1.id, 'relates_to', created_by=admin_user.id)
        assert ok_dup is False
        assert 'exists' in err.lower()

        # 2. Blocks / Is Blocked By (canonical normalization)
        # When creating "i3 is_blocked_by i1", canonical normalization stores "i1 blocks i3"
        ok, link_block, msg = IssueService.link_issues(i3.id, i1.id, 'is_blocked_by', created_by=admin_user.id)
        assert ok is True
        assert link_block.source_issue_id == i1.id
        assert link_block.target_issue_id == i3.id
        assert link_block.link_type == 'blocks'
        assert link_block.is_relationship is True
        assert link_block.is_dependency is False  # ordinary relationship, not scheduling dependency

        # 3. Viewing from both perspectives
        i1_links = IssueService.get_issue_links(i1.id)
        i3_links = IssueService.get_issue_links(i3.id)
        assert any(l['link_type'] == 'blocks' and l['direction'] == 'outgoing' for l in i1_links['links'])
        assert any(l['display_type'] == 'is_blocked_by' and l['direction'] == 'incoming' for l in i3_links['links'])

        # 4. Duplicates / Is Duplicated By
        ok, link_dup, _ = IssueService.link_issues(i2.id, i3.id, 'duplicates', created_by=admin_user.id)
        assert ok is True
        assert link_dup.link_type == 'duplicates'
        assert link_dup.inverse_type == 'is_duplicated_by'


def test_parent_child_hierarchy_and_cycle_prevention(app, admin_user, test_project):
    """Test parent-child hierarchy rules, subtasks, and cycle prevention."""
    with app.app_context():
        epic = Issue(key='HIE-1', title='Epic Alpha', issue_type='epic', project_id=test_project.id)
        story = Issue(key='HIE-2', title='Story Beta', issue_type='story', project_id=test_project.id)
        subtask = Issue(key='HIE-3', title='Subtask Gamma', issue_type='subtask', project_id=test_project.id)
        db.session.add_all([epic, story, subtask])
        db.session.commit()

        # 1. Valid hierarchy: story parent is epic
        ok, updated_story, msg = IssueService.update_issue(story.id, {'parent_id': epic.id}, updated_by=admin_user.id)
        assert ok is True
        assert updated_story.parent_id == epic.id

        # 2. Valid hierarchy: subtask parent is story
        ok, updated_sub, msg = IssueService.update_issue(subtask.id, {'parent_id': story.id}, updated_by=admin_user.id)
        assert ok is True
        assert updated_sub.parent_id == story.id

        # 3. Invalid: Self-parenting
        ok, _, err = IssueService.update_issue(story.id, {'parent_id': story.id}, updated_by=admin_user.id)
        assert ok is False
        assert 'own parent' in err.lower()

        # 4. Invalid: Circular hierarchy (epic parent set to subtask)
        ok, _, err = IssueService.update_issue(epic.id, {'parent_id': subtask.id}, updated_by=admin_user.id)
        assert ok is False
        assert 'cannot have a parent' in err.lower() or 'circular' in err.lower()

        # 5. Invalid: Subtask cannot be parent
        new_task = Issue(key='HIE-4', title='Task Delta', issue_type='task', project_id=test_project.id)
        db.session.add(new_task)
        db.session.commit()
        ok, _, err = IssueService.update_issue(new_task.id, {'parent_id': subtask.id}, updated_by=admin_user.id)
        assert ok is False
        assert 'subtask cannot be a parent' in err.lower()


def test_scheduling_constraints_mathematics():
    """Test deep mathematical correctness of FS, SS, FF constraints with lag and inclusive dates."""
    # Dates
    nov1 = date(2026, 11, 1)
    nov5 = date(2026, 11, 5)   # A finishes Nov 5 inclusive
    nov6 = date(2026, 11, 6)   # next day
    nov8 = date(2026, 11, 8)
    nov10 = date(2026, 11, 10)

    # 1. Finish-to-Start (FS), lag = 0
    # A finishes Nov 5, B starts Nov 6 -> valid (min allowed is Nov 6)
    conflict, min_d, viol = check_schedule_constraint('finish_to_start', nov1, nov5, nov6, nov10, lag_days=0)
    assert conflict is False
    assert viol == 0

    # A finishes Nov 5, B starts Nov 5 -> conflict! (B starts on same day A finishes)
    conflict, min_d, viol = check_schedule_constraint('finish_to_start', nov1, nov5, nov5, nov10, lag_days=0)
    assert conflict is True
    assert min_d == nov6
    assert viol == 1

    # 2. Finish-to-Start (FS), positive lag = 2
    # min allowed = Nov 5 + 1 day + 2 lag = Nov 8
    conflict, min_d, viol = check_schedule_constraint('finish_to_start', nov1, nov5, nov6, nov10, lag_days=2)
    assert conflict is True
    assert min_d == nov8
    assert viol == 2  # Nov 8 - Nov 6

    conflict, min_d, viol = check_schedule_constraint('finish_to_start', nov1, nov5, nov8, nov10, lag_days=2)
    assert conflict is False

    # 3. Finish-to-Start (FS), negative lag = -1 (lead time)
    # min allowed = Nov 5 + 1 - 1 = Nov 5
    conflict, min_d, viol = check_schedule_constraint('finish_to_start', nov1, nov5, nov5, nov10, lag_days=-1)
    assert conflict is False

    # 4. Start-to-Start (SS), lag = 3
    # A starts Nov 1, lag 3 -> min allowed for B is Nov 1 + 3 = Nov 4
    conflict, min_d, viol = check_schedule_constraint('start_to_start', nov1, nov5, date(2026, 11, 3), nov10, lag_days=3)
    assert conflict is True
    assert min_d == date(2026, 11, 4)

    conflict, min_d, viol = check_schedule_constraint('start_to_start', nov1, nov5, date(2026, 11, 4), nov10, lag_days=3)
    assert conflict is False

    # 5. Finish-to-Finish (FF), lag = 0
    # A finishes Nov 10 -> B must finish on or after Nov 10
    conflict, min_d, viol = check_schedule_constraint('finish_to_finish', nov1, nov10, nov1, date(2026, 11, 8), lag_days=0)
    assert conflict is True
    assert min_d == nov10

    conflict, min_d, viol = check_schedule_constraint('finish_to_finish', nov1, nov10, nov1, nov10, lag_days=0)
    assert conflict is False

    # 6. Leap year boundary: Feb 28, 2028 + 1 day -> Feb 29, 2028
    feb28 = date(2028, 2, 28)
    feb29 = date(2028, 2, 29)
    conflict, min_d, _ = check_schedule_constraint('finish_to_start', date(2028, 2, 20), feb28, feb28, date(2028, 3, 5), lag_days=0)
    assert conflict is True
    assert min_d == feb29

    # 7. Year boundary: Dec 31, 2026 + 1 day -> Jan 1, 2027
    dec31 = date(2026, 12, 31)
    jan1 = date(2027, 1, 1)
    conflict, min_d, _ = check_schedule_constraint('finish_to_start', date(2026, 12, 1), dec31, dec31, date(2027, 1, 10), lag_days=0)
    assert conflict is True
    assert min_d == jan1


def test_schedule_propagation_cascade(app, admin_user, test_project):
    """Test realistic dependency chain: A -> B -> C -> D with duration preservation."""
    with app.app_context():
        # Setup chain: A (Nov 1-5, 4d duration) -> B (Nov 6-10, 4d) -> C (Nov 11-15, 4d) -> D (Nov 16-20, 4d)
        a = Issue(key='CAS-A', title='Task A', project_id=test_project.id, start_date=date(2026, 11, 1), due_date=date(2026, 11, 5))
        b = Issue(key='CAS-B', title='Task B', project_id=test_project.id, start_date=date(2026, 11, 6), due_date=date(2026, 11, 10))
        c = Issue(key='CAS-C', title='Task C', project_id=test_project.id, start_date=date(2026, 11, 11), due_date=date(2026, 11, 15))
        d = Issue(key='CAS-D', title='Task D', project_id=test_project.id, start_date=date(2026, 11, 16), due_date=date(2026, 11, 20))
        db.session.add_all([a, b, c, d])
        db.session.commit()

        # Link chain
        IssueService.link_issues(a.id, b.id, 'finish_to_start', created_by=admin_user.id)
        IssueService.link_issues(b.id, c.id, 'finish_to_start', created_by=admin_user.id)
        IssueService.link_issues(c.id, d.id, 'finish_to_start', created_by=admin_user.id)

        # 1. Moving A later: A due date pushed out by 7 days to Nov 12
        # Without cascade: B, C, D dates stay unchanged but conflict is reported
        ok, updated_a, msg, conflicts = IssueService.update_dates(
            a.id,
            start_date='2026-11-01',
            due_date='2026-11-12',
            cascade=False,
            updated_by=admin_user.id
        )
        assert ok is True
        assert len(conflicts) > 0

        # Helper to normalize date
        def to_d(val):
            return val.date() if isinstance(val, datetime) else val

        # Verify B was NOT silently modified when cascade=False
        b_fresh = Issue.query.get(b.id)
        assert to_d(b_fresh.start_date) == date(2026, 11, 6)

        # 2. With cascade=True: B, C, D must shift forward, preserving their 4-day durations!
        ok, updated_a, msg, conflicts = IssueService.update_dates(
            a.id,
            start_date='2026-11-01',
            due_date='2026-11-12',
            cascade=True,
            updated_by=admin_user.id
        )
        assert ok is True

        b_shifted = Issue.query.get(b.id)
        c_shifted = Issue.query.get(c.id)
        d_shifted = Issue.query.get(d.id)

        # A finishes Nov 12 -> B must start Nov 13, and finish Nov 17 (4d duration)
        assert to_d(b_shifted.start_date) == date(2026, 11, 13)
        assert to_d(b_shifted.due_date) == date(2026, 11, 17)
        assert (to_d(b_shifted.due_date) - to_d(b_shifted.start_date)).days == 4

        # B finishes Nov 17 -> C must start Nov 18, and finish Nov 22 (4d duration)
        assert to_d(c_shifted.start_date) == date(2026, 11, 18)
        assert to_d(c_shifted.due_date) == date(2026, 11, 22)
        assert (to_d(c_shifted.due_date) - to_d(c_shifted.start_date)).days == 4

        # C finishes Nov 22 -> D must start Nov 23, and finish Nov 27 (4d duration)
        assert to_d(d_shifted.start_date) == date(2026, 11, 23)
        assert to_d(d_shifted.due_date) == date(2026, 11, 27)
        assert (to_d(d_shifted.due_date) - to_d(d_shifted.start_date)).days == 4


def test_kanban_dense_position_reordering(app, admin_user, test_project):
    """Test Kanban intra-column and inter-column reordering with dense 0-based indices."""
    with app.app_context():
        t1 = Issue(key='KAN-1', title='Task 1', project_id=test_project.id, status='todo', position=0)
        t2 = Issue(key='KAN-2', title='Task 2', project_id=test_project.id, status='todo', position=1)
        t3 = Issue(key='KAN-3', title='Task 3', project_id=test_project.id, status='todo', position=2)
        t4 = Issue(key='KAN-4', title='Task 4', project_id=test_project.id, status='in_progress', position=0)
        db.session.add_all([t1, t2, t3, t4])
        db.session.commit()

        # 1. Inter-column move: Move t2 to in_progress at position 0
        ok, moved, msg = IssueService.reorder_kanban(t2.id, 'in_progress', 0, updated_by=admin_user.id)
        assert ok is True
        assert moved.status == 'in_progress'
        assert moved.position == 0

        # Verify old column (todo) was normalized: t1 is 0, t3 is 1 (no gaps)
        todo_issues = Issue.query.filter_by(project_id=test_project.id, status='todo').order_by(Issue.position).all()
        assert [i.id for i in todo_issues] == [t1.id, t3.id]
        assert [i.position for i in todo_issues] == [0, 1]

        # Verify destination column (in_progress) has t2 at 0 and t4 shifted to 1
        prog_issues = Issue.query.filter_by(project_id=test_project.id, status='in_progress').order_by(Issue.position).all()
        assert [i.id for i in prog_issues] == [t2.id, t4.id]
        assert [i.position for i in prog_issues] == [0, 1]

        # 2. Intra-column move: Move t4 before t2 in in_progress
        ok, reordered, msg = IssueService.reorder_kanban(t4.id, 'in_progress', 0, updated_by=admin_user.id)
        assert ok is True
        prog_issues_after = Issue.query.filter_by(project_id=test_project.id, status='in_progress').order_by(Issue.position).all()
        assert [i.id for i in prog_issues_after] == [t4.id, t2.id]
        assert [i.position for i in prog_issues_after] == [0, 1]


def test_cross_project_and_unauthorized_linking(client, admin_user, auth_user, test_project):
    """Test cross-project security and unauthorized link deletion."""
    # Create second project owned by admin
    with client.application.app_context():
        p2 = Project(name='Private Project', key='PRV', created_by=admin_user.id, lead_id=admin_user.id, status='active')
        db.session.add(p2)
        db.session.commit()
        
        i_pub = Issue(key='TST-SEC-1', title='Public Issue', project_id=test_project.id)
        i_prv = Issue(key='PRV-SEC-1', title='Private Issue', project_id=p2.id)
        db.session.add_all([i_pub, i_prv])
        db.session.commit()
        pub_id = i_pub.id
        prv_id = i_prv.id
        p2_id = p2.id

    # Auth_user (employee) tries to link public issue to private issue in p2 (to which auth_user has no access)
    with client.session_transaction() as sess:
        sess['user_id'] = auth_user.id
        sess['role'] = auth_user.role
        sess['username'] = auth_user.username

    res = client.post(
        f'/api/v1/project/{test_project.id}/issue/{pub_id}/link',
        json={'target_issue_id': prv_id, 'link_type': 'relates_to'}
    )
    # Should be rejected with 403 Access Denied
    assert res.status_code == 403
    assert 'access denied' in res.get_json()['error'].lower()
