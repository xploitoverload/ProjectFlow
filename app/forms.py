#!/usr/bin/env python
# app/forms.py - Extended with ProgressUpdateForm

from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField, SelectField, 
    TextAreaField, IntegerField, FloatField, BooleanField, DateField
)
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional
from models import User
from datetime import datetime, timedelta

# Existing form imports and definitions...

class ProgressUpdateForm(FlaskForm):
    """Form for employee to submit progress updates"""
    
    reporting_period = SelectField(
        'Reporting Period',
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly')
        ],
        validators=[DataRequired()],
        description='Select the reporting period for this update'
    )
    
    period_start_date = DateField(
        'Period Start Date',
        validators=[DataRequired()],
        description='Start date of the reporting period'
    )
    
    period_end_date = DateField(
        'Period End Date',
        validators=[DataRequired()],
        description='End date of the reporting period'
    )
    
    completed_work = TextAreaField(
        'Completed Work',
        validators=[DataRequired(), Length(min=10, max=5000)],
        description='What work did you complete during this period? Be specific with tasks, features, or deliverables.'
    )
    
    work_in_progress = TextAreaField(
        'Work Currently In Progress',
        validators=[DataRequired(), Length(min=10, max=5000)],
        description='What are you currently working on? Include status and expected completion date.'
    )
    
    blocked_tasks = TextAreaField(
        'Blocked Tasks',
        validators=[Optional(), Length(max=2000)],
        description='Any tasks that are blocked or stuck? Leave blank if none.'
    )
    
    blocked_reasons = TextAreaField(
        'Reasons for Blocked Tasks',
        validators=[Optional(), Length(max=2000)],
        description='Why are these tasks blocked? What dependencies or issues are preventing progress?'
    )
    
    hours_spent = FloatField(
        'Hours Spent This Period',
        validators=[Optional()],
        description='Total hours worked during this reporting period'
    )
    
    effort_level = SelectField(
        'Effort Level',
        choices=[
            ('low', 'Low (25% capacity)'),
            ('medium', 'Medium (50-75% capacity)'),
            ('high', 'High (75-100% capacity)')
        ],
        default='medium',
        validators=[DataRequired()],
        description='Your overall effort level during this period'
    )
    
    individual_contributions = TextAreaField(
        'Individual Contributions',
        validators=[DataRequired(), Length(min=10, max=3000)],
        description='Highlight your individual achievements, learnings, or improvements made.'
    )
    
    team_work = TextAreaField(
        'Team-Related Work',
        validators=[Optional(), Length(max=3000)],
        description='How did you contribute to the team? Collaboration, mentoring, support, etc.'
    )
    
    features_worked = TextAreaField(
        'Product Features Worked On',
        validators=[Optional(), Length(max=2000)],
        description='List features or product improvements you worked on.'
    )
    
    bugs_fixed = TextAreaField(
        'Bugs Fixed',
        validators=[Optional(), Length(max=2000)],
        description='List bugs you fixed, with issue IDs if available.'
    )
    
    improvements = TextAreaField(
        'Improvements & Enhancements',
        validators=[Optional(), Length(max=2000)],
        description='Any process improvements, code optimizations, or other enhancements made.'
    )
    
    project_status = SelectField(
        'Project Status',
        choices=[
            ('on_track', 'On Track'),
            ('at_risk', 'At Risk'),
            ('delayed', 'Delayed')
        ],
        default='on_track',
        validators=[DataRequired()],
        description='Overall status of the project(s) you are working on.'
    )
    
    risks_dependencies = TextAreaField(
        'Risks & Dependencies',
        validators=[Optional(), Length(max=2000)],
        description='Any risks, external dependencies, or constraints affecting your work.'
    )
    
    challenges = TextAreaField(
        'Challenges & Obstacles',
        validators=[Optional(), Length(max=2000)],
        description='Any challenges or obstacles you faced during this period.'
    )
    
    next_priorities = TextAreaField(
        'Priorities for Next Period',
        validators=[DataRequired(), Length(min=10, max=3000)],
        description='What are your planned priorities and goals for the next reporting period?'
    )
    
    notes = TextAreaField(
        'Additional Notes',
        validators=[Optional(), Length(max=2000)],
        description='Any additional notes, context, or information for the admin.'
    )
    
    escalations = TextAreaField(
        'Escalations for Admin',
        validators=[Optional(), Length(max=2000)],
        description='Any items that need admin attention or escalation.'
    )
    
    submit = SubmitField('Submit Progress Update')
    
    def validate_period_end_date(self, field):
        """Validate that end date is after start date"""
        if field.data <= self.period_start_date.data:
            raise ValidationError('End date must be after start date.')
    
    def validate_hours_spent(self, field):
        """Validate hours spent is reasonable"""
        if field.data and field.data < 0:
            raise ValidationError('Hours spent cannot be negative.')
        if field.data and field.data > 24 * 30:  # Max 30 days * 24 hours
            raise ValidationError('Hours spent seems unreasonably high. Please verify.')


class ReviewProgressUpdateForm(FlaskForm):
    """Form for admin to review progress updates"""
    
    review_status = SelectField(
        'Review Status',
        choices=[
            ('reviewed', 'Reviewed'),
            ('approved', 'Approved')
        ],
        validators=[DataRequired()],
        description='Mark the review status for this progress update.'
    )
    
    admin_comments = TextAreaField(
        'Admin Comments',
        validators=[Optional(), Length(max=2000)],
        description='Your feedback, observations, or comments on this progress update.'
    )
    
    submit = SubmitField('Save Review')
