# app/services/scheduling_service.py
"""
Scheduling & Project Intelligence Service
Implements Critical Path Method (CPM), Earliest/Latest Start/Finish passes,
Total Float, Free Float, bottleneck identification, working calendars,
and dependency-aware scheduling intelligence.
"""

from datetime import datetime, date, timedelta
import json
import logging
from app.utils.security import log_security_event

logger = logging.getLogger('scheduling')


def to_date(val):
    """Normalize datetime or string to date object."""
    if val is None:
        return None
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, date):
        return val
    if isinstance(val, str):
        try:
            return datetime.strptime(val[:10], '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return None
    return None


class SchedulingService:
    """Enterprise scheduling engine with Critical Path Method (CPM)."""

    @staticmethod
    def calculate_critical_path(project_id, reference_date=None):
        """
        Calculates the Critical Path Method (CPM) metrics for a project:
        - Earliest Start (ES) & Earliest Finish (EF) via forward pass
        - Latest Start (LS) & Latest Finish (LF) via backward pass
        - Total Float (Slack) & Free Float
        - Critical Path task sequence
        - Bottlenecks (high degree centrality + low float)
        
        Returns dict with:
        {
            'success': bool,
            'error': str or None,
            'project_duration_days': int,
            'critical_path_issue_ids': list,
            'critical_tasks': list,
            'bottlenecks': list,
            'task_metrics': dict of issue_id -> {
                'es': date, 'ef': date, 'ls': date, 'lf': date,
                'total_float': int, 'free_float': int, 'is_critical': bool
            }
        }
        """
        from app.models import Issue, IssueLink

        issues = Issue.query.filter_by(project_id=project_id).all()
        if not issues:
            return {
                'success': True,
                'error': None,
                'project_duration_days': 0,
                'critical_path_issue_ids': [],
                'critical_tasks': [],
                'bottlenecks': [],
                'task_metrics': {}
            }

        issue_ids = {iss.id for iss in issues}
        links = IssueLink.query.filter(
            IssueLink.source_issue_id.in_(issue_ids),
            IssueLink.target_issue_id.in_(issue_ids),
            IssueLink.link_type.in_(IssueLink.DEPENDENCY_TYPES)
        ).all()

        # Build adjacency graph
        # pred_map: target_id -> list of (source_id, link_type, lag_days)
        # succ_map: source_id -> list of (target_id, link_type, lag_days)
        in_degree = {i_id: 0 for i_id in issue_ids}
        pred_map = {i_id: [] for i_id in issue_ids}
        succ_map = {i_id: [] for i_id in issue_ids}

        for link in links:
            s_id = link.source_issue_id
            t_id = link.target_issue_id
            lag = int(link.lag_days or 0)
            succ_map[s_id].append((t_id, link.link_type, lag))
            pred_map[t_id].append((s_id, link.link_type, lag))
            in_degree[t_id] += 1

        # Cycle detection using Kahn's algorithm
        queue = [i_id for i_id, deg in in_degree.items() if deg == 0]
        topo_order = []
        deg_copy = dict(in_degree)

        while queue:
            curr = queue.pop(0)
            topo_order.append(curr)
            for succ_id, _, _ in succ_map[curr]:
                deg_copy[succ_id] -= 1
                if deg_copy[succ_id] == 0:
                    queue.append(succ_id)

        if len(topo_order) < len(issue_ids):
            return {
                'success': False,
                'error': 'Circular dependency chain detected in project tasks',
                'project_duration_days': 0,
                'critical_path_issue_ids': [],
                'critical_tasks': [],
                'bottlenecks': [],
                'task_metrics': {}
            }

        # Determine task durations and baseline anchor date
        ref_start = to_date(reference_date) or date.today()
        all_starts = [to_date(i.start_date) for i in issues if i.start_date]
        if all_starts:
            project_base_date = min(min(all_starts), ref_start)
        else:
            project_base_date = ref_start

        durations = {}
        for iss in issues:
            st = to_date(iss.start_date)
            du = to_date(iss.due_date)
            if st and du and du >= st:
                durations[iss.id] = (du - st).days + 1  # Inclusive days
            else:
                durations[iss.id] = 1  # Default minimum 1-day effort

        # -------------------------------------------------------------
        # 1. FORWARD PASS: Calculate ES (Earliest Start) & EF (Earliest Finish)
        # -------------------------------------------------------------
        es_map = {}
        ef_map = {}

        for t_id in topo_order:
            curr_issue = next(i for i in issues if i.id == t_id)
            planned_start = to_date(curr_issue.start_date) or project_base_date

            if not pred_map[t_id]:
                # Task with no predecessors starts on planned start or project start
                es_date = planned_start
            else:
                # Constrained by predecessors
                candidate_es = [planned_start]
                for p_id, l_type, lag in pred_map[t_id]:
                    p_ef = ef_map[p_id]
                    p_es = es_map[p_id]
                    if l_type == 'finish_to_start':
                        # Successor starts after predecessor finishes + 1 inclusive day + lag
                        candidate_es.append(p_ef + timedelta(days=1 + lag))
                    elif l_type == 'start_to_start':
                        # Successor starts after predecessor starts + lag
                        candidate_es.append(p_es + timedelta(days=lag))
                    elif l_type == 'finish_to_finish':
                        # EF_succ >= EF_pred + lag => ES_succ >= EF_pred + lag - dur + 1
                        req_ef = p_ef + timedelta(days=lag)
                        candidate_es.append(req_ef - timedelta(days=durations[t_id] - 1))
                es_date = max(candidate_es)

            es_map[t_id] = es_date
            ef_map[t_id] = es_date + timedelta(days=durations[t_id] - 1)

        # Overall project earliest completion date
        max_project_ef = max(ef_map.values()) if ef_map else project_base_date

        # -------------------------------------------------------------
        # 2. BACKWARD PASS: Calculate LF (Latest Finish) & LS (Latest Start)
        # -------------------------------------------------------------
        lf_map = {}
        ls_map = {}

        # Reverse topological order
        for t_id in reversed(topo_order):
            curr_issue = next(i for i in issues if i.id == t_id)
            planned_due = to_date(curr_issue.due_date)

            if not succ_map[t_id]:
                # Terminal task: LF is project completion (or planned due date if later)
                lf_date = max_project_ef
                if planned_due and planned_due > lf_date:
                    lf_date = planned_due
            else:
                # Constrained by successors
                candidate_lf = []
                for s_id, l_type, lag in succ_map[t_id]:
                    s_ls = ls_map[s_id]
                    s_lf = lf_map[s_id]
                    if l_type == 'finish_to_start':
                        # Predecessor must finish before successor starts - 1 day - lag
                        candidate_lf.append(s_ls - timedelta(days=1 + lag))
                    elif l_type == 'start_to_start':
                        # LS_pred <= LS_succ - lag => LF_pred <= LS_succ - lag + dur - 1
                        req_ls = s_ls - timedelta(days=lag)
                        candidate_lf.append(req_ls + timedelta(days=durations[t_id] - 1))
                    elif l_type == 'finish_to_finish':
                        # LF_pred <= LF_succ - lag
                        candidate_lf.append(s_lf - timedelta(days=lag))
                lf_date = min(candidate_lf)

            lf_map[t_id] = lf_date
            ls_map[t_id] = lf_date - timedelta(days=durations[t_id] - 1)

        # -------------------------------------------------------------
        # 3. FLOAT & CRITICAL PATH IDENTIFICATION
        # -------------------------------------------------------------
        task_metrics = {}
        critical_ids = []
        bottlenecks = []

        for t_id in topo_order:
            curr_issue = next(i for i in issues if i.id == t_id)
            es = es_map[t_id]
            ef = ef_map[t_id]
            ls = ls_map[t_id]
            lf = lf_map[t_id]

            total_float = (ls - es).days

            # Free float: delay allowed without postponing earliest start of any successor
            if not succ_map[t_id]:
                free_float = (max_project_ef - ef).days
            else:
                ff_candidates = []
                for s_id, l_type, lag in succ_map[t_id]:
                    s_es = es_map[s_id]
                    if l_type == 'finish_to_start':
                        ff_candidates.append((s_es - timedelta(days=1 + lag) - ef).days)
                    elif l_type == 'start_to_start':
                        ff_candidates.append((s_es - timedelta(days=lag) - es).days)
                    elif l_type == 'finish_to_finish':
                        ff_candidates.append((ef_map[s_id] - timedelta(days=lag) - ef).days)
                free_float = max(0, min(ff_candidates)) if ff_candidates else 0

            # A task is critical if Total Float <= 0
            is_critical = (total_float <= 0)
            if is_critical:
                critical_ids.append(t_id)

            # Bottleneck: degree centrality >= 2 (multiple in or out dependencies) AND float <= 0
            deg = len(pred_map[t_id]) + len(succ_map[t_id])
            if deg >= 2 and total_float <= 1:
                bottlenecks.append({
                    'id': t_id,
                    'key': curr_issue.key,
                    'title': curr_issue.title,
                    'predecessors_count': len(pred_map[t_id]),
                    'successors_count': len(succ_map[t_id]),
                    'total_float': total_float,
                    'is_critical': is_critical
                })

            task_metrics[t_id] = {
                'id': t_id,
                'key': curr_issue.key,
                'title': curr_issue.title,
                'duration_days': durations[t_id],
                'es': es.isoformat(),
                'ef': ef.isoformat(),
                'ls': ls.isoformat(),
                'lf': lf.isoformat(),
                'total_float': total_float,
                'free_float': free_float,
                'is_critical': is_critical
            }

        # Order critical path tasks sequentially
        critical_tasks = [task_metrics[t_id] for t_id in critical_ids]
        project_duration = (max_project_ef - project_base_date).days + 1 if topo_order else 0

        return {
            'success': True,
            'error': None,
            'project_start_date': project_base_date.isoformat(),
            'project_end_date': max_project_ef.isoformat(),
            'project_duration_days': max(1, project_duration),
            'critical_path_issue_ids': critical_ids,
            'critical_tasks': critical_tasks,
            'bottlenecks': bottlenecks,
            'task_metrics': task_metrics
        }

    @staticmethod
    def preview_auto_schedule(project_id):
        """
        Calculates proposed date shifts to resolve all scheduling conflicts,
        without mutating the database. Returns an inspection preview.
        """
        from app.models import Issue, IssueLink
        from app.services.issue_service import check_schedule_constraint

        issues = Issue.query.filter_by(project_id=project_id).all()
        issue_map = {i.id: i for i in issues}

        # Run CPM to get earliest valid dates
        cpm = SchedulingService.calculate_critical_path(project_id)
        if not cpm['success']:
            return {'success': False, 'error': cpm['error'], 'proposals': []}

        proposals = []
        metrics = cpm['task_metrics']

        for iss in issues:
            curr_st = to_date(iss.start_date)
            curr_du = to_date(iss.due_date)
            m = metrics.get(iss.id)
            if not m:
                continue

            prop_st = to_date(m['es'])
            prop_du = to_date(m['ef'])

            # Only propose changes if dates actually shift or resolve a conflict
            if curr_st != prop_st or curr_du != prop_du:
                shift_days = (prop_st - curr_st).days if curr_st else 0
                proposals.append({
                    'issue_id': iss.id,
                    'key': iss.key,
                    'title': iss.title,
                    'current_start': curr_st.isoformat() if curr_st else None,
                    'current_due': curr_du.isoformat() if curr_du else None,
                    'proposed_start': prop_st.isoformat() if prop_st else None,
                    'proposed_due': prop_du.isoformat() if prop_du else None,
                    'shift_days': shift_days,
                    'is_critical': m['is_critical'],
                    'total_float': m['total_float'],
                    'reason': 'Cascaded from predecessor completion constraints' if shift_days > 0 else 'Scheduled based on earliest topological availability'
                })

        return {
            'success': True,
            'proposals': proposals,
            'total_shifts': len(proposals),
            'project_duration_days': cpm['project_duration_days'],
            'critical_path_issue_ids': cpm['critical_path_issue_ids']
        }

    @staticmethod
    def commit_auto_schedule(project_id, updated_by=None):
        """
        Applies previewed auto-schedule dates transactionally.
        """
        from app.models import Issue, db

        preview = SchedulingService.preview_auto_schedule(project_id)
        if not preview['success']:
            return False, preview['error'], 0

        applied_count = 0
        try:
            for prop in preview['proposals']:
                issue = Issue.query.get(prop['issue_id'])
                if issue:
                    issue.start_date = to_date(prop['proposed_start'])
                    issue.due_date = to_date(prop['proposed_due'])
                    issue.updated_at = datetime.utcnow()
                    applied_count += 1

            db.session.commit()

            if applied_count > 0 and updated_by:
                log_security_event(
                    'AUTO_SCHEDULE_COMMITTED',
                    user_id=updated_by,
                    details=f'Committed auto-schedule alignment for {applied_count} tasks in project {project_id}',
                    severity='INFO'
                )

            return True, f'Successfully aligned {applied_count} tasks', applied_count
        except Exception as e:
            db.session.rollback()
            return False, f'Error committing schedule: {str(e)}', 0
