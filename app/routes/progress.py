#!/usr/bin/env python
# app/routes/progress.py - Progress update routes for employees and admins

from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from models import db, ProgressUpdate, User
from app.forms import ProgressUpdateForm, ReviewProgressUpdateForm
from datetime import datetime, timedelta, date
from functools import wraps

progress_bp = Blueprint('progress', __name__, url_prefix='/progress')

def admin_required(f):
    """Decorator to check if user is admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function


@progress_bp.route('/submit', methods=['GET', 'POST'])
@login_required
def submit_update():
    """Submit a progress update"""
    form = ProgressUpdateForm()
    
    if form.validate_on_submit():
        # Create new progress update
        update = ProgressUpdate(
            user_id=current_user.id,
            reporting_period=form.reporting_period.data,
            period_start_date=form.period_start_date.data,
            period_end_date=form.period_end_date.data,
            completed_work=form.completed_work.data,
            work_in_progress=form.work_in_progress.data,
            blocked_tasks=form.blocked_tasks.data or None,
            blocked_reasons=form.blocked_reasons.data or None,
            hours_spent=form.hours_spent.data or 0,
            effort_level=form.effort_level.data,
            individual_contributions=form.individual_contributions.data,
            team_work=form.team_work.data or None,
            features_worked=form.features_worked.data or None,
            bugs_fixed=form.bugs_fixed.data or None,
            improvements=form.improvements.data or None,
            project_status=form.project_status.data,
            risks_dependencies=form.risks_dependencies.data or None,
            challenges=form.challenges.data or None,
            next_priorities=form.next_priorities.data,
            notes=form.notes.data or None,
            escalations=form.escalations.data or None,
            submitted_at=datetime.utcnow()
        )
        
        db.session.add(update)
        db.session.commit()
        
        flash(
            f'✓ Progress update for {form.reporting_period.data} period submitted successfully! '
            'Your update has been sent to admin for review.',
            'success'
        )
        return redirect(url_for('progress.my_updates'))
    
    # Pre-fill dates if first load
    if request.method == 'GET':
        today = date.today()
        if form.reporting_period.data == 'daily' or not form.reporting_period.data:
            form.period_end_date.data = today
            form.period_start_date.data = today
        elif form.reporting_period.data == 'weekly':
            # Last week
            form.period_end_date.data = today
            form.period_start_date.data = today - timedelta(days=7)
        elif form.reporting_period.data == 'monthly':
            # This month
            form.period_end_date.data = today
            form.period_start_date.data = today.replace(day=1)
    
    return render_template('progress/submit_update.html', form=form)


@progress_bp.route('/my-updates', methods=['GET'])
@login_required
def my_updates():
    """View user's own progress updates"""
    page = request.args.get('page', 1, type=int)
    updates = ProgressUpdate.query.filter_by(user_id=current_user.id).order_by(
        ProgressUpdate.submitted_at.desc()
    ).paginate(page=page, per_page=10)
    
    return render_template(
        'progress/my_updates.html',
        updates=updates,
        title='My Progress Updates'
    )


@progress_bp.route('/view/<int:update_id>', methods=['GET'])
@login_required
def view_update(update_id):
    """View a specific progress update"""
    update = ProgressUpdate.query.get_or_404(update_id)
    
    # Check authorization - user can view their own, admin can view all
    if update.user_id != current_user.id and current_user.role != 'admin':
        flash('You do not have permission to view this update.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    return render_template(
        'progress/view_update.html',
        update=update,
        title=f'Progress Update - {update.user.username}'
    )


@progress_bp.route('/edit/<int:update_id>', methods=['GET', 'POST'])
@login_required
def edit_update(update_id):
    """Edit a progress update (only if not yet reviewed)"""
    update = ProgressUpdate.query.get_or_404(update_id)
    
    # Check authorization
    if update.user_id != current_user.id and current_user.role != 'admin':
        flash('You do not have permission to edit this update.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Non-admin users can only edit pending updates
    if current_user.role != 'admin' and update.review_status != 'pending':
        flash('You can only edit updates that are pending review.', 'warning')
        return redirect(url_for('progress.view_update', update_id=update.id))
    
    form = ProgressUpdateForm()
    
    if form.validate_on_submit():
        update.reporting_period = form.reporting_period.data
        update.period_start_date = form.period_start_date.data
        update.period_end_date = form.period_end_date.data
        update.completed_work = form.completed_work.data
        update.work_in_progress = form.work_in_progress.data
        update.blocked_tasks = form.blocked_tasks.data or None
        update.blocked_reasons = form.blocked_reasons.data or None
        update.hours_spent = form.hours_spent.data or 0
        update.effort_level = form.effort_level.data
        update.individual_contributions = form.individual_contributions.data
        update.team_work = form.team_work.data or None
        update.features_worked = form.features_worked.data or None
        update.bugs_fixed = form.bugs_fixed.data or None
        update.improvements = form.improvements.data or None
        update.project_status = form.project_status.data
        update.risks_dependencies = form.risks_dependencies.data or None
        update.challenges = form.challenges.data or None
        update.next_priorities = form.next_priorities.data
        update.notes = form.notes.data or None
        update.escalations = form.escalations.data or None
        
        db.session.commit()
        
        flash('✓ Progress update updated successfully!', 'success')
        return redirect(url_for('progress.view_update', update_id=update.id))
    
    # Pre-fill form with existing data
    elif request.method == 'GET':
        form.reporting_period.data = update.reporting_period
        form.period_start_date.data = update.period_start_date
        form.period_end_date.data = update.period_end_date
        form.completed_work.data = update.completed_work
        form.work_in_progress.data = update.work_in_progress
        form.blocked_tasks.data = update.blocked_tasks
        form.blocked_reasons.data = update.blocked_reasons
        form.hours_spent.data = update.hours_spent
        form.effort_level.data = update.effort_level
        form.individual_contributions.data = update.individual_contributions
        form.team_work.data = update.team_work
        form.features_worked.data = update.features_worked
        form.bugs_fixed.data = update.bugs_fixed
        form.improvements.data = update.improvements
        form.project_status.data = update.project_status
        form.risks_dependencies.data = update.risks_dependencies
        form.challenges.data = update.challenges
        form.next_priorities.data = update.next_priorities
        form.notes.data = update.notes
        form.escalations.data = update.escalations
    
    return render_template(
        'progress/submit_update.html',
        form=form,
        update=update,
        title=f'Edit Progress Update'
    )


# ==================== ADMIN ROUTES ====================

@progress_bp.route('/admin/pending', methods=['GET'])
@login_required
@admin_required
def admin_pending():
    """View pending progress updates for admin review"""
    page = request.args.get('page', 1, type=int)
    updates = ProgressUpdate.query.filter_by(review_status='pending').order_by(
        ProgressUpdate.submitted_at.desc()
    ).paginate(page=page, per_page=15)
    
    return render_template(
        'progress/admin_pending.html',
        updates=updates,
        now=datetime.utcnow(),
        title='Pending Progress Updates'
    )


@progress_bp.route('/admin/all', methods=['GET'])
@login_required
@admin_required
def admin_all():
    """View all progress updates (admin)"""
    page = request.args.get('page', 1, type=int)
    
    # Filters
    user_id = request.args.get('user_id', type=int)
    status = request.args.get('status', default='all')
    period = request.args.get('period', default='all')
    
    query = ProgressUpdate.query
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    if status != 'all':
        query = query.filter_by(review_status=status)
    
    if period != 'all':
        query = query.filter_by(reporting_period=period)
    
    updates = query.order_by(ProgressUpdate.submitted_at.desc()).paginate(
        page=page, per_page=15
    )
    
    users = User.query.all()
    
    # Get summary counts
    total_updates = ProgressUpdate.query.count()
    pending_count = ProgressUpdate.query.filter_by(review_status='pending').count()
    approved_count = ProgressUpdate.query.filter_by(review_status='approved').count()
    revision_count = ProgressUpdate.query.filter_by(review_status='needs_revision').count()
    
    return render_template(
        'progress/admin_all.html',
        updates=updates,
        users=users,
        now=datetime.utcnow(),
        total_updates=total_updates,
        pending_count=pending_count,
        approved_count=approved_count,
        revision_count=revision_count,
        selected_user_id=user_id,
        selected_status=status,
        selected_period=period,
        title='All Progress Updates'
    )


@progress_bp.route('/admin/review/<int:update_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_review(update_id):
    """Admin review and feedback on progress update"""
    update = ProgressUpdate.query.get_or_404(update_id)
    form = ReviewProgressUpdateForm()
    
    if form.validate_on_submit():
        update.review_status = form.review_status.data
        update.admin_comments = form.admin_comments.data
        update.reviewed_at = datetime.utcnow()
        update.reviewed_by_id = current_user.id
        
        db.session.commit()
        
        # Send notification (if notification system exists)
        flash(
            f'✓ Progress update from {update.user.username} has been {form.review_status.data}. '
            'Feedback recorded.',
            'success'
        )
        return redirect(url_for('progress.admin_pending'))
    
    elif request.method == 'GET':
        form.review_status.data = update.review_status
        form.admin_comments.data = update.admin_comments
    
    return render_template(
        'progress/admin_review.html',
        update=update,
        form=form,
        title='Review Progress Update'
    )


@progress_bp.route('/admin/stats', methods=['GET'])
@login_required
@admin_required
def admin_stats():
    """Admin view of progress update statistics"""
    from sqlalchemy import func
    
    period = request.args.get('period', 'all')
    
    # Get statistics
    total_updates = ProgressUpdate.query.count()
    pending_reviews = ProgressUpdate.query.filter_by(review_status='pending').count()
    approved_reviews = ProgressUpdate.query.filter_by(review_status='approved').count()
    needs_revision = ProgressUpdate.query.filter_by(review_status='needs_revision').count()
    
    # Status breakdown
    on_track = ProgressUpdate.query.filter_by(project_status='on_track').count()
    at_risk = ProgressUpdate.query.filter_by(project_status='at_risk').count()
    delayed = ProgressUpdate.query.filter_by(project_status='delayed').count()
    
    # Effort level distribution
    effort_low = ProgressUpdate.query.filter_by(effort_level='low').count() if total_updates > 0 else 0
    effort_medium = ProgressUpdate.query.filter_by(effort_level='medium').count() if total_updates > 0 else 0
    effort_high = ProgressUpdate.query.filter_by(effort_level='high').count() if total_updates > 0 else 0
    
    # Period distribution
    period_daily = ProgressUpdate.query.filter_by(reporting_period='daily').count() if total_updates > 0 else 0
    period_weekly = ProgressUpdate.query.filter_by(reporting_period='weekly').count() if total_updates > 0 else 0
    period_monthly = ProgressUpdate.query.filter_by(reporting_period='monthly').count() if total_updates > 0 else 0
    
    # Get recent updates
    recent_updates = ProgressUpdate.query.order_by(
        ProgressUpdate.submitted_at.desc()
    ).limit(10).all()
    
    # Get users with most updates (top submitters)
    top_submitters = db.session.query(
        User, func.count(ProgressUpdate.id).label('update_count')
    ).join(ProgressUpdate).group_by(User.id).order_by(
        func.count(ProgressUpdate.id).desc()
    ).limit(10).all()
    
    # Get average hours by user
    avg_hours = db.session.query(
        User, func.avg(ProgressUpdate.hours_spent).label('avg_hours')
    ).join(ProgressUpdate).group_by(User.id).order_by(
        func.avg(ProgressUpdate.hours_spent).desc()
    ).limit(10).all()
    
    # Now convert to list of tuples for template
    top_submitters_list = [(user, count) for user, count in top_submitters]
    avg_hours_list = [(user, avg_hrs) for user, avg_hrs in avg_hours]
    
    stats = {
        'total_updates': total_updates,
        'pending_reviews': pending_reviews,
        'approved_reviews': approved_reviews,
        'needs_revision': needs_revision,
        'on_track': on_track,
        'at_risk': at_risk,
        'delayed': delayed,
        'effort_low': effort_low,
        'effort_medium': effort_medium,
        'effort_high': effort_high,
        'period_daily': period_daily,
        'period_weekly': period_weekly,
        'period_monthly': period_monthly,
    }
    
    return render_template(
        'progress/admin_stats.html',
        stats=stats,
        recent_updates=recent_updates,
        top_submitters=top_submitters_list,
        avg_hours=avg_hours_list,
        now=datetime.utcnow(),
        title='Progress Update Statistics'
    )
