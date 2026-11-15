# app/services/issue_service.py
"""
Issue Service
Handles issue/task management business logic.
"""

from datetime import datetime, date, timedelta
from app.utils.security import sanitize_input, log_security_event
from app.utils.validators import (
    validate_required, validate_length, validate_date,
    validate_status, validate_priority, validate_issue_type,
    validate_integer, validate_float, ValidationError
)


def _to_date(val):
    if val is None:
        return None
    if isinstance(val, datetime):
        return val.date()
    return val


def check_schedule_constraint(link_type, src_start, src_due, tgt_start, tgt_due, lag_days=0):
    """
    Evaluates whether a scheduling dependency constraint is violated.
    End dates are strictly INCLUSIVE.
    - Finish-to-Start (FS): Successor start must be >= Predecessor finish + 1 day + lag_days
    - Start-to-Start (SS): Successor start must be >= Predecessor start + lag_days
    - Finish-to-Finish (FF): Successor finish must be >= Predecessor finish + lag_days
    Returns: (is_conflict: bool, min_allowed_date: date or None, violation_days: int)
    """
    lag = int(lag_days or 0)
    s_start = _to_date(src_start)
    s_due = _to_date(src_due)
    t_start = _to_date(tgt_start)
    t_due = _to_date(tgt_due)
    
    if link_type == 'finish_to_start':
        if s_due and t_start:
            min_allowed = s_due + timedelta(days=1 + lag)
            if t_start < min_allowed:
                return True, min_allowed, (min_allowed - t_start).days
        return False, None, 0

    elif link_type == 'start_to_start':
        if s_start and t_start:
            min_allowed = s_start + timedelta(days=lag)
            if t_start < min_allowed:
                return True, min_allowed, (min_allowed - t_start).days
        return False, None, 0

    elif link_type == 'finish_to_finish':
        if s_due and t_due:
            min_allowed = s_due + timedelta(days=lag)
            if t_due < min_allowed:
                return True, min_allowed, (min_allowed - t_due).days
        return False, None, 0

    return False, None, 0


class IssueService:
    """Service for handling issue operations."""
    
    VALID_STATUSES = ['open', 'todo', 'in_progress', 'code_review', 
                      'testing', 'ready_deploy', 'done', 'closed', 'reopened']
    
    VALID_PRIORITIES = ['lowest', 'low', 'medium', 'high', 'highest', 'critical']
    
    VALID_TYPES = ['story', 'task', 'bug', 'epic', 'subtask']
    
    @staticmethod
    def create_issue(project_id, title, description=None, issue_type='task',
                    priority='medium', status='todo', assignee_id=None, reporter_id=None,
                    story_points=None, time_estimate=None, due_date=None,
                    sprint_id=None, epic_id=None, parent_id=None):
        """
        Create a new issue.
        
        Returns:
            tuple: (success: bool, issue: Issue or None, message: str)
        """
        from app.models import Issue, Project, db
        
        try:
            # Validate project exists
            project = Project.query.get(project_id)
            if not project:
                return False, None, 'Project not found'
            
            # Validate inputs
            title = sanitize_input(validate_required(title, 'title'))
            validate_length(title, 'title', min_length=1, max_length=200)
            
            validate_issue_type(issue_type)
            validate_priority(priority)
            validate_status(status)
            
            # Generate issue key
            key = IssueService._generate_issue_key(project_id)
            
            # Parse dates
            if isinstance(due_date, str):
                due_date = validate_date(due_date, 'due_date')
            
            # Validate numeric fields
            if story_points is not None:
                story_points = validate_integer(story_points, 'story_points', min_value=1, max_value=100)
            
            if time_estimate is not None:
                time_estimate = validate_float(time_estimate, 'time_estimate', min_value=0, max_value=1000)
            
            # Get max position for new issues with same status
            max_position = db.session.query(db.func.max(Issue.position)).filter_by(
                project_id=project_id, status=status
            ).scalar() or 0
            
            # Create issue
            issue = Issue(
                key=key,
                title=title,
                project_id=project_id,
                issue_type=issue_type,
                priority=priority,
                status=status,
                assignee_id=int(assignee_id) if assignee_id else None,
                reporter_id=reporter_id,
                story_points=story_points,
                time_estimate=time_estimate,
                due_date=due_date,
                sprint_id=int(sprint_id) if sprint_id else None,
                epic_id=int(epic_id) if epic_id else None,
                parent_id=int(parent_id) if parent_id else None,
                position=max_position + 1
            )
            
            if description:
                issue.description = sanitize_input(description, allow_html=True)
            
            db.session.add(issue)
            db.session.commit()
            
            log_security_event(
                'ISSUE_CREATED',
                user_id=reporter_id,
                details=f'Created issue: {key} in project {project.key}',
                severity='INFO'
            )
            
            return True, issue, 'Issue created successfully'
            
        except ValidationError as e:
            return False, None, str(e)
        except Exception as e:
            db.session.rollback()
            return False, None, f'Error creating issue: {str(e)}'
    
    @staticmethod
    def update_issue(issue_id, data, updated_by=None):
        """Update issue information."""
        from app.models import Issue, WorkflowTransition, db
        
        try:
            issue = Issue.query.get(issue_id)
            if not issue:
                return False, None, 'Issue not found'
            
            old_status = issue.status
            
            if 'title' in data:
                issue.title = sanitize_input(data['title'])
            
            if 'description' in data:
                issue.description = sanitize_input(data['description'], allow_html=True)
            
            if 'status' in data:
                new_status = data['status']
                validate_status(new_status)
                
                if new_status != old_status:
                    # Record workflow transition
                    transition = WorkflowTransition(
                        issue_id=issue.id,
                        from_status=old_status,
                        to_status=new_status,
                        user_id=updated_by
                    )
                    db.session.add(transition)
                    
                    issue.status = new_status
                    
                    # Set completion time
                    if new_status in ['done', 'closed'] and old_status not in ['done', 'closed']:
                        issue.closed_at = datetime.utcnow()
                    elif new_status not in ['done', 'closed']:
                        issue.closed_at = None
            
            if 'priority' in data:
                validate_priority(data['priority'])
                issue.priority = data['priority']
            
            if 'issue_type' in data:
                validate_issue_type(data['issue_type'])
                issue.issue_type = data['issue_type']
            
            if 'assignee_id' in data:
                issue.assignee_id = int(data['assignee_id']) if data['assignee_id'] else None
            
            if 'story_points' in data:
                issue.story_points = validate_integer(data['story_points'], 'story_points', min_value=1, max_value=100)
            
            if 'time_estimate' in data:
                issue.time_estimate = validate_float(data['time_estimate'], 'time_estimate', min_value=0)
            
            if 'time_spent' in data:
                issue.time_spent = validate_float(data['time_spent'], 'time_spent', min_value=0)
            
            if 'due_date' in data:
                parsed_due = validate_date(data['due_date'], 'due_date') if data['due_date'] else None
                issue.due_date = parsed_due.date() if isinstance(parsed_due, datetime) else parsed_due
            
            if 'start_date' in data:
                parsed_start = validate_date(data['start_date'], 'start_date') if data['start_date'] else None
                issue.start_date = parsed_start.date() if isinstance(parsed_start, datetime) else parsed_start

            if 'position' in data:
                issue.position = int(data['position']) if data['position'] is not None else 0

            if 'parent_id' in data:
                new_parent_id = int(data['parent_id']) if data['parent_id'] else None
                if new_parent_id == issue.id:
                    raise ValidationError('parent_id', 'An issue cannot be its own parent')
                if new_parent_id:
                    parent_issue = Issue.query.get(new_parent_id)
                    if not parent_issue:
                        raise ValidationError('parent_id', 'Parent issue not found')
                    if issue.issue_type == 'epic':
                        raise ValidationError('parent_id', 'Epics are top-level and cannot have a parent issue')
                    if parent_issue.issue_type == 'subtask':
                        raise ValidationError('parent_id', 'A subtask cannot be a parent issue')
                    # Check cycle
                    curr = parent_issue
                    visited = {issue.id, new_parent_id}
                    while curr and curr.parent_id:
                        if curr.parent_id in visited:
                            raise ValidationError('parent_id', 'Circular parent-child hierarchy detected')
                        visited.add(curr.parent_id)
                        curr = Issue.query.get(curr.parent_id)
                issue.parent_id = new_parent_id
            
            if 'sprint_id' in data:
                issue.sprint_id = int(data['sprint_id']) if data['sprint_id'] else None
            
            if 'epic_id' in data:
                issue.epic_id = int(data['epic_id']) if data['epic_id'] else None
            
            issue.updated_at = datetime.utcnow()
            db.session.commit()
            
            log_security_event(
                'ISSUE_UPDATED',
                user_id=updated_by,
                details=f'Updated issue: {issue.key}',
                severity='INFO'
            )
            
            return True, issue, 'Issue updated successfully'
            
        except ValidationError as e:
            return False, None, str(e)
        except Exception as e:
            db.session.rollback()
            return False, None, f'Error updating issue: {str(e)}'
    
    @staticmethod
    def update_status(issue_id, new_status, updated_by=None):
        """Quick status update for drag-and-drop."""
        return IssueService.update_issue(issue_id, {'status': new_status}, updated_by)
    
    @staticmethod
    def delete_issue(issue_id, deleted_by=None):
        """Delete an issue."""
        from app.models import Issue, IssueLink, db
        
        try:
            issue = Issue.query.get(issue_id)
            if not issue:
                return False, 'Issue not found'
            
            issue_key = issue.key
            project_id = issue.project_id
            
            # Clean up links explicitly
            IssueLink.query.filter(
                (IssueLink.source_issue_id == issue_id) | (IssueLink.target_issue_id == issue_id)
            ).delete(synchronize_session=False)
            
            db.session.delete(issue)
            db.session.commit()
            
            log_security_event(
                'ISSUE_DELETED',
                user_id=deleted_by,
                details=f'Deleted issue: {issue_key}',
                severity='WARNING'
            )
            
            return True, 'Issue deleted successfully'
            
        except Exception as e:
            db.session.rollback()
            return False, f'Error deleting issue: {str(e)}'
    
    @staticmethod
    def get_issue_by_id(issue_id):
        """Get issue by ID."""
        from app.models import Issue
        return Issue.query.get(issue_id)
    
    @staticmethod
    def get_issue_by_key(key):
        """Get issue by key (case-insensitive with whitespace trimming)."""
        from app.models import Issue, db
        if not key:
            return None
        clean_key = str(key).strip().upper()
        issue = Issue.query.filter_by(key=clean_key).first()
        if not issue:
            issue = Issue.query.filter(db.func.upper(Issue.key) == clean_key).first()
        return issue
    
    @staticmethod
    def get_issues_by_project(project_id, filters=None):
        """Get issues for a project with optional filters."""
        from app.models import Issue
        
        query = Issue.query.filter_by(project_id=project_id)
        
        if filters:
            if 'status' in filters and filters['status']:
                query = query.filter_by(status=filters['status'])
            if 'priority' in filters and filters['priority']:
                query = query.filter_by(priority=filters['priority'])
            if 'assignee_id' in filters and filters['assignee_id']:
                query = query.filter_by(assignee_id=int(filters['assignee_id']))
            if 'issue_type' in filters and filters['issue_type']:
                query = query.filter_by(issue_type=filters['issue_type'])
            if 'sprint_id' in filters and filters['sprint_id']:
                query = query.filter_by(sprint_id=int(filters['sprint_id']))
            if 'epic_id' in filters and filters['epic_id']:
                query = query.filter_by(epic_id=int(filters['epic_id']))
        
        return query.order_by(Issue.position).all()
    
    @staticmethod
    def get_issues_grouped_by_status(project_id):
        """Get issues grouped by status for Kanban board."""
        from app.models import Issue
        
        issues = Issue.query.filter_by(project_id=project_id).order_by(Issue.position).all()
        
        grouped = {status: [] for status in IssueService.VALID_STATUSES}
        
        for issue in issues:
            if issue.status in grouped:
                grouped[issue.status].append(issue)
        
        return grouped
    
    @staticmethod
    def add_comment(issue_id, user_id, text):
        """Add a comment to an issue."""
        from app.models import Issue, Comment, db
        
        try:
            issue = Issue.query.get(issue_id)
            if not issue:
                return False, None, 'Issue not found'
            
            text = sanitize_input(validate_required(text, 'text'), allow_html=True)
            
            comment = Comment(
                issue_id=issue_id,
                user_id=user_id
            )
            comment.text = text
            
            db.session.add(comment)
            issue.updated_at = datetime.utcnow()
            db.session.commit()
            
            return True, comment, 'Comment added successfully'
            
        except Exception as e:
            db.session.rollback()
            return False, None, f'Error adding comment: {str(e)}'
    
    @staticmethod
    def link_issues(source_id, target_id, link_type, lag_days=0, created_by=None):
        """Create a link or dependency between two issues with cycle prevention and inverse semantics."""
        from app.models import Issue, IssueLink, db
        
        try:
            source = Issue.query.get(source_id)
            target = Issue.query.get(target_id)
            
            if not source or not target:
                return False, None, 'Issue not found'
            
            if source_id == target_id:
                return False, None, 'Cannot link an issue to itself'
            
            all_valid_types = IssueLink.RELATION_TYPES + IssueLink.DEPENDENCY_TYPES
            if link_type not in all_valid_types:
                return False, None, f'Invalid link type. Must be one of: {", ".join(all_valid_types)}'
            
            # Canonical normalization for inverse relationships to avoid duplicate reversed rows
            canonical_flips = {
                'is_blocked_by': 'blocks',
                'is_duplicated_by': 'duplicates',
                'is_cloned_by': 'clones',
                'is_implemented_by': 'implements'
            }
            if link_type in canonical_flips:
                link_type = canonical_flips[link_type]
                source_id, target_id = target_id, source_id
                source, target = target, source

            # Check for existing link (or symmetric reverse for relates_to)
            existing = IssueLink.query.filter_by(
                source_issue_id=source_id,
                target_issue_id=target_id,
                link_type=link_type
            ).first()
            if existing:
                return False, None, 'Link already exists'
                
            if link_type == 'relates_to':
                rev = IssueLink.query.filter_by(
                    source_issue_id=target_id,
                    target_issue_id=source_id,
                    link_type='relates_to'
                ).first()
                if rev:
                    return False, None, 'Symmetric relationship already exists'
            
            # Transitive circular dependency prevention for directed relations
            directed_types = ['blocks', 'finish_to_start', 'start_to_start', 'finish_to_finish']
            if link_type in directed_types:
                pred_id, succ_id = source_id, target_id
                
                # Check if succ_id can already reach pred_id through existing directed edges
                visited = set()
                queue = [succ_id]
                while queue:
                    curr = queue.pop(0)
                    if curr == pred_id:
                        return False, None, 'Circular dependency chain detected'
                    if curr in visited:
                        continue
                    visited.add(curr)
                    
                    # Outgoing edges from curr
                    out_edges = IssueLink.query.filter(
                        IssueLink.source_issue_id == curr,
                        IssueLink.link_type.in_(directed_types)
                    ).all()
                    for edge in out_edges:
                        if edge.target_issue_id not in visited:
                            queue.append(edge.target_issue_id)
            
            link = IssueLink(
                source_issue_id=source_id,
                target_issue_id=target_id,
                link_type=link_type,
                lag_days=int(lag_days) if lag_days else 0,
                created_by=created_by
            )
            
            db.session.add(link)
            db.session.commit()
            
            log_security_event(
                'ISSUE_LINKED',
                user_id=created_by,
                details=f'Linked {source.key} to {target.key} via {link_type}',
                severity='INFO'
            )
            
            return True, link, 'Link created successfully'
            
        except Exception as e:
            db.session.rollback()
            return False, None, f'Error creating link: {str(e)}'

    @staticmethod
    def unlink_issues(link_id, deleted_by=None, current_issue_id=None):
        """Remove an issue relationship by ID with verification."""
        from app.models import IssueLink, db
        try:
            link = IssueLink.query.get(link_id)
            if not link:
                return False, 'Link not found'
            
            if current_issue_id and link.source_issue_id != current_issue_id and link.target_issue_id != current_issue_id:
                return False, 'Link does not belong to this issue'

            db.session.delete(link)
            db.session.commit()
            
            log_security_event(
                'ISSUE_UNLINKED',
                user_id=deleted_by,
                details=f'Removed link {link_id}',
                severity='INFO'
            )
            return True, 'Link removed successfully'
        except Exception as e:
            db.session.rollback()
            return False, f'Error removing link: {str(e)}'

    @staticmethod
    def get_issue_links(issue_id):
        """Get all relationships, hierarchy, and dependencies for an issue with correct inverse semantics."""
        from app.models import Issue, IssueLink
        issue = Issue.query.get(issue_id)
        if not issue:
            return None
        
        outgoing = IssueLink.query.filter_by(source_issue_id=issue_id).all()
        incoming = IssueLink.query.filter_by(target_issue_id=issue_id).all()
        
        links = []
        for l in outgoing:
            d = l.to_dict()
            d['direction'] = 'outgoing'
            d['other_issue'] = {
                'id': l.target_issue.id,
                'key': l.target_issue.key,
                'title': l.target_issue.title,
                'status': l.target_issue.status,
                'start_date': l.target_issue.start_date.isoformat() if l.target_issue.start_date else None,
                'due_date': l.target_issue.due_date.isoformat() if l.target_issue.due_date else None
            }
            is_conflict, min_req, viol = check_schedule_constraint(
                l.link_type,
                l.source_issue.start_date, l.source_issue.due_date,
                l.target_issue.start_date, l.target_issue.due_date,
                l.lag_days
            )
            d['is_conflict'] = is_conflict
            d['conflict_min_date'] = min_req.isoformat() if min_req else None
            d['violation_days'] = viol
            links.append(d)
            
        for l in incoming:
            d = l.to_dict()
            d['direction'] = 'incoming'
            d['display_type'] = l.inverse_type
            d['display_label'] = IssueLink.LABELS.get(l.inverse_type, l.inverse_type.replace('_', ' ').title())
            d['other_issue'] = {
                'id': l.source_issue.id,
                'key': l.source_issue.key,
                'title': l.source_issue.title,
                'status': l.source_issue.status,
                'start_date': l.source_issue.start_date.isoformat() if l.source_issue.start_date else None,
                'due_date': l.source_issue.due_date.isoformat() if l.source_issue.due_date else None
            }
            is_conflict, min_req, viol = check_schedule_constraint(
                l.link_type,
                l.source_issue.start_date, l.source_issue.due_date,
                l.target_issue.start_date, l.target_issue.due_date,
                l.lag_days
            )
            d['is_conflict'] = is_conflict
            d['conflict_min_date'] = min_req.isoformat() if min_req else None
            d['violation_days'] = viol
            links.append(d)
            
        return {
            'issue_id': issue_id,
            'parent': {
                'id': issue.parent.id,
                'key': issue.parent.key,
                'title': issue.parent.title,
                'status': issue.parent.status
            } if issue.parent else None,
            'subtasks': [{
                'id': s.id,
                'key': s.key,
                'title': s.title,
                'status': s.status
            } for s in issue.subtasks],
            'links': links
        }

    @staticmethod
    def propagate_schedule(issue_id, updated_by=None):
        """
        Cascade date changes downstream through scheduling dependencies (FS, SS, FF).
        Preserves durations of downstream tasks. Runs transactionally.
        Returns: (success: bool, shifted_issues: list, remaining_conflicts: list)
        """
        from app.models import Issue, IssueLink, db
        try:
            root = Issue.query.get(issue_id)
            if not root or not root.start_date or not root.due_date:
                return True, [], []

            queue = [issue_id]
            visited = set()
            shifted_map = {}

            while queue:
                curr_id = queue.pop(0)
                visited.add(curr_id)
                curr = Issue.query.get(curr_id)
                if not curr:
                    continue

                out_deps = IssueLink.query.filter(
                    IssueLink.source_issue_id == curr_id,
                    IssueLink.link_type.in_(IssueLink.DEPENDENCY_TYPES)
                ).all()

                for dep in out_deps:
                    succ = dep.target_issue
                    if not succ or succ.id in visited:
                        continue

                    s_st = _to_date(succ.start_date)
                    s_due = _to_date(succ.due_date)
                    succ_duration = 0
                    if s_st and s_due:
                        succ_duration = max(0, (s_due - s_st).days)

                    is_conflict, min_req, _ = check_schedule_constraint(
                        dep.link_type,
                        curr.start_date, curr.due_date,
                        succ.start_date, succ.due_date,
                        dep.lag_days
                    )

                    if is_conflict and min_req:
                        if dep.link_type in ['finish_to_start', 'start_to_start']:
                            succ.start_date = min_req
                            succ.due_date = min_req + timedelta(days=succ_duration)
                        elif dep.link_type == 'finish_to_finish':
                            succ.due_date = min_req
                            succ.start_date = max(s_st or min_req, min_req - timedelta(days=succ_duration))
                        
                        succ.updated_at = datetime.utcnow()
                        shifted_map[succ.id] = succ
                        if succ.id not in queue:
                            queue.append(succ.id)

            db.session.commit()
            
            shifted_list = list(shifted_map.values())
            if shifted_list and updated_by:
                log_security_event(
                    'SCHEDULE_PROPAGATED',
                    user_id=updated_by,
                    details=f'Cascaded schedule from {root.key} to {len(shifted_list)} issues',
                    severity='INFO'
                )

            all_conflicts = []
            for s_issue in [root] + shifted_list:
                info = IssueService.get_issue_links(s_issue.id)
                if info:
                    for l in info.get('links', []):
                        if l.get('is_conflict'):
                            all_conflicts.append(f"{s_issue.key}: conflict with {l['other_issue']['key']}")

            return True, shifted_list, list(set(all_conflicts))
        except Exception as e:
            db.session.rollback()
            return False, [], [f'Propagation error: {str(e)}']

    @staticmethod
    def update_dates(issue_id, start_date=None, due_date=None, cascade=False, updated_by=None):
        """Update issue start and due dates with validation and optional schedule propagation."""
        from app.models import Issue, db
        try:
            issue = Issue.query.get(issue_id)
            if not issue:
                return False, None, 'Issue not found', []

            new_start = None
            if start_date:
                parsed = validate_date(start_date, 'start_date') if isinstance(start_date, str) else start_date
                new_start = parsed.date() if isinstance(parsed, datetime) else parsed
            elif start_date == '':
                new_start = None
            else:
                new_start = issue.start_date

            new_due = None
            if due_date:
                parsed = validate_date(due_date, 'due_date') if isinstance(due_date, str) else due_date
                new_due = parsed.date() if isinstance(parsed, datetime) else parsed
            elif due_date == '':
                new_due = None
            else:
                new_due = issue.due_date

            if new_start and new_due and new_start > new_due:
                return False, None, 'Start date cannot be after due date', []

            issue.start_date = new_start
            issue.due_date = new_due
            issue.updated_at = datetime.utcnow()
            db.session.commit()

            conflicts = []
            if cascade and issue.start_date and issue.due_date:
                _, shifted, conflicts = IssueService.propagate_schedule(issue.id, updated_by=updated_by)
            else:
                info = IssueService.get_issue_links(issue.id)
                if info:
                    for l in info.get('links', []):
                        if l.get('is_conflict'):
                            conflicts.append(f"Scheduling conflict with {l['other_issue']['key']}")

            return True, issue, 'Dates updated successfully', conflicts
        except Exception as e:
            db.session.rollback()
            return False, None, f'Error updating dates: {str(e)}', []

    @staticmethod
    def reorder_kanban(issue_id, new_status, new_position=0, updated_by=None):
        """Move an issue to a status and reorder positions consecutively with dense indexing."""
        from app.models import Issue, db
        try:
            issue = Issue.query.get(issue_id)
            if not issue:
                return False, None, 'Issue not found'
            
            valid_statuses = ['open', 'backlog', 'todo', 'in_progress', 'code_review', 'testing', 'ready_deploy', 'done', 'closed', 'reopened']
            if new_status not in valid_statuses:
                return False, None, 'Invalid status'
            
            old_status = issue.status
            issue.status = new_status
            
            dest_issues = Issue.query.filter(
                Issue.project_id == issue.project_id,
                Issue.status == new_status,
                Issue.id != issue.id
            ).order_by(Issue.position.asc(), Issue.id.asc()).all()
            
            new_position = max(0, min(new_position, len(dest_issues)))
            dest_issues.insert(new_position, issue)
            
            for idx, item in enumerate(dest_issues):
                item.position = idx
            
            if old_status != new_status:
                old_issues = Issue.query.filter(
                    Issue.project_id == issue.project_id,
                    Issue.status == old_status,
                    Issue.id != issue.id
                ).order_by(Issue.position.asc(), Issue.id.asc()).all()
                for idx, item in enumerate(old_issues):
                    item.position = idx
            
            issue.updated_at = datetime.utcnow()
            db.session.commit()
            
            log_security_event(
                'KANBAN_REORDERED',
                user_id=updated_by,
                details=f'Moved {issue.key} from {old_status} to {new_status} at position {new_position}',
                severity='INFO'
            )
            return True, issue, 'Kanban updated successfully'
        except Exception as e:
            db.session.rollback()
            return False, None, f'Error reordering: {str(e)}'
        except Exception as e:
            db.session.rollback()
            return False, None, f'Error reordering: {str(e)}'
    
    @staticmethod
    def log_time(issue_id, hours, user_id):
        """Log time spent on an issue."""
        from app.models import Issue, db
        
        try:
            issue = Issue.query.get(issue_id)
            if not issue:
                return False, 'Issue not found'
            
            hours = validate_float(hours, 'hours', min_value=0, max_value=24)
            
            issue.time_spent = (issue.time_spent or 0) + hours
            issue.updated_at = datetime.utcnow()
            db.session.commit()
            
            return True, f'Logged {hours} hours'
            
        except Exception as e:
            db.session.rollback()
            return False, f'Error logging time: {str(e)}'
    
    @staticmethod
    def _generate_issue_key(project_id):
        """Generate unique issue key like PROJ-123."""
        from app.models import Issue, Project, db
        
        try:
            project = Project.query.get(project_id)
            if not project:
                raise ValueError('Project not found')
            
            # Handle NULL or empty project key
            prefix = (project.key or '').strip()
            if not prefix:
                prefix = ''.join([c for c in project.name.upper() if c.isalnum()])[:4]
            
            # Ensure prefix is at least 2 chars
            if not prefix or len(prefix) < 2:
                prefix = 'PROJ'
            
            # Get the last issue number for this project with lock to prevent race conditions
            last_issue = Issue.query.filter_by(project_id=project_id).order_by(Issue.id.desc()).first()
            
            if last_issue and last_issue.key:
                try:
                    number = int(last_issue.key.split('-')[-1]) + 1
                except ValueError:
                    number = Issue.query.filter_by(project_id=project_id).count() + 1
            else:
                number = 1
            
            key = f"{prefix}-{number}"
            
            # Verify uniqueness (double-check)
            while Issue.query.filter_by(key=key).first():
                number += 1
                key = f"{prefix}-{number}"
            
            return key
        except Exception as e:
            raise ValueError(f'Error generating issue key: {str(e)}')
