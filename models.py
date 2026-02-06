# models.py - Complete Jira-style Database Models with All Features
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from cryptography.fernet import Fernet
from werkzeug.security import generate_password_hash, check_password_hash
import os

db = SQLAlchemy()

# Encryption key management
def get_encryption_key():
    """Get or create encryption key for database fields"""
    key_file = 'encryption.key'
    if os.path.exists(key_file):
        with open(key_file, 'rb') as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        with open(key_file, 'wb') as f:
            f.write(key)
        return key

ENCRYPTION_KEY = get_encryption_key()
cipher = Fernet(ENCRYPTION_KEY)

def encrypt_field(data):
    if data is None:
        return None
    return cipher.encrypt(data.encode()).decode()

def decrypt_field(data):
    if data is None:
        return None
    try:
        return cipher.decrypt(data.encode()).decode()
    except:
        return None

# Many-to-many relationship between Projects and Teams
project_teams = db.Table('project_teams',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id', ondelete='CASCADE'), primary_key=True),
    db.Column('team_id', db.Integer, db.ForeignKey('team.id', ondelete='CASCADE'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)

class User(UserMixin, db.Model):
    """User model with encrypted email"""
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email_encrypted = db.Column(db.Text, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, index=True)  # Extended for more roles
    department = db.Column(db.String(50), index=True)  # Auto-derived from role: software, hardware, mechanical, etc.
    team_id = db.Column(db.Integer, db.ForeignKey('team.id', ondelete='SET NULL'))  # Core team assignment
    avatar_color = db.Column(db.String(7), default='#667eea')  # For avatar gradients
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    failed_login_attempts = db.Column(db.Integer, default=0)
    last_login = db.Column(db.DateTime)
    last_activity = db.Column(db.DateTime)  # Updated on each request
    is_active = db.Column(db.Boolean, default=True)
    
    @property
    def email(self):
        return decrypt_field(self.email_encrypted)
    
    @email.setter
    def email(self, value):
        self.email_encrypted = encrypt_field(value)
    
    @property
    def is_online(self):
        """Check if user is considered online (active in last 5 minutes)."""
        if not self.last_activity:
            return False
        from datetime import timedelta
        return (datetime.utcnow() - self.last_activity) < timedelta(minutes=5)
    
    @property
    def status_text(self):
        """Get user status text."""
        if not self.is_active:
            return 'Inactive'
        if self.is_online:
            return 'Online'
        if self.last_activity:
            return f'Last seen {self.time_ago(self.last_activity)}'
        return 'Offline'
    
    @staticmethod
    def time_ago(dt):
        """Get human-readable time ago string."""
        if not dt:
            return 'Never'
        diff = datetime.utcnow() - dt
        seconds = diff.total_seconds()
        if seconds < 60:
            return 'just now'
        elif seconds < 3600:
            mins = int(seconds / 60)
            return f'{mins}m ago'
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f'{hours}h ago'
        else:
            days = int(seconds / 86400)
            return f'{days}d ago'
    
    def set_password(self, password):
        self.password = generate_password_hash(password, method='pbkdf2:sha256:600000')
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def get_id(self):
        return str(self.id)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Team(db.Model):
    """Team model with type and many-to-many project relationship"""
    __tablename__ = 'team'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    team_type = db.Column(db.String(50), default='general')  # android, web, embedded, etc.
    department = db.Column(db.String(50))  # For core teams: software, hardware, mechanical, etc.
    is_core_team = db.Column(db.Boolean, default=False)  # True = Department core team, False = Project team
    description_encrypted = db.Column(db.Text)
    color = db.Column(db.String(7), default='#6366f1')  # Team color for UI
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    members = db.relationship('User', backref='team', lazy=True)
    # Many-to-many relationship with projects
    assigned_projects = db.relationship('Project', secondary='project_teams', 
                                        backref=db.backref('teams', lazy='dynamic'),
                                        lazy='dynamic')
    
    @property
    def description(self):
        return decrypt_field(self.description_encrypted)
    
    @description.setter
    def description(self, value):
        if value:
            self.description_encrypted = encrypt_field(value)
        else:
            self.description_encrypted = None
    
    def __repr__(self):
        return f'<Team {self.name}>'

class Project(db.Model):
    """Project model with workflow type"""
    __tablename__ = 'project'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    key = db.Column(db.String(10), unique=True, nullable=False)  # e.g., "NUC"
    description_encrypted = db.Column(db.Text)
    status = db.Column(db.String(50), nullable=False, index=True)
    workflow_type = db.Column(db.String(20), default='agile')
    team_id = db.Column(db.Integer, db.ForeignKey('team.id', ondelete='SET NULL'))
    lead_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'))  # Project lead
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relationships
    team = db.relationship('Team', foreign_keys=[team_id], backref='primary_projects')
    lead = db.relationship('User', foreign_keys=[lead_id], backref='led_projects')
    updates = db.relationship('ProjectUpdate', backref='project_ref', lazy=True, cascade='all, delete-orphan')
    sprints = db.relationship('Sprint', backref='project', lazy=True, cascade='all, delete-orphan')
    epics = db.relationship('Epic', backref='project', lazy=True, cascade='all, delete-orphan')
    issues = db.relationship('Issue', backref='project', lazy=True, cascade='all, delete-orphan')
    labels = db.relationship('Label', backref='project', lazy=True, cascade='all, delete-orphan')
    
    @property
    def description(self):
        return decrypt_field(self.description_encrypted)
    
    @description.setter
    def description(self, value):
        if value:
            self.description_encrypted = encrypt_field(value)
        else:
            self.description_encrypted = None
    
    def __repr__(self):
        return f'<Project {self.name}>'

class Sprint(db.Model):
    """Sprint model for Agile workflow"""
    __tablename__ = 'sprint'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id', ondelete='CASCADE'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    goal = db.Column(db.Text)
    status = db.Column(db.String(20), default='planned')  # planned, active, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    issues = db.relationship('Issue', backref='sprint', lazy=True)
    
    def __repr__(self):
        return f'<Sprint {self.name}>'

class Epic(db.Model):
    """Epic model for grouping issues"""
    __tablename__ = 'epic'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description_encrypted = db.Column(db.Text)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id', ondelete='CASCADE'), nullable=False)
    color = db.Column(db.String(7), default='#0052cc')
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='active')  # active, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    issues = db.relationship('Issue', backref='epic', lazy=True)
    
    @property
    def description(self):
        return decrypt_field(self.description_encrypted)
    
    @description.setter
    def description(self, value):
        if value:
            self.description_encrypted = encrypt_field(value)
    
    def __repr__(self):
        return f'<Epic {self.name}>'

class Label(db.Model):
    """Label model for categorizing issues (ACCOUNTS, BILLING, FORMS, FEEDBACK)"""
    __tablename__ = 'label'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(7), nullable=False)  # Hex color
    project_id = db.Column(db.Integer, db.ForeignKey('project.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Label {self.name}>'

# Association table for Issue-Label many-to-many relationship
issue_labels = db.Table('issue_labels',
    db.Column('issue_id', db.Integer, db.ForeignKey('issue.id', ondelete='CASCADE'), primary_key=True),
    db.Column('label_id', db.Integer, db.ForeignKey('label.id', ondelete='CASCADE'), primary_key=True)
)

class Issue(db.Model):
    """Complete Issue model with all Jira features"""
    __tablename__ = 'issue'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(20), unique=True, nullable=False, index=True)  # NUC-342
    title = db.Column(db.String(200), nullable=False)
    description_encrypted = db.Column(db.Text)
    
    # Relationships
    project_id = db.Column(db.Integer, db.ForeignKey('project.id', ondelete='CASCADE'), nullable=False, index=True)
    epic_id = db.Column(db.Integer, db.ForeignKey('epic.id', ondelete='SET NULL'))
    sprint_id = db.Column(db.Integer, db.ForeignKey('sprint.id', ondelete='SET NULL'))
    assignee_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'))
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'))
    parent_id = db.Column(db.Integer, db.ForeignKey('issue.id', ondelete='CASCADE'))  # For subtasks
    
    # Issue details
    issue_type = db.Column(db.String(20), default='task')  # story, task, bug, epic, subtask
    status = db.Column(db.String(20), default='open', index=True)  # open, todo, in_progress, code_review, testing, ready_deploy, done, closed, reopened
    priority = db.Column(db.String(20), default='medium')  # lowest, low, medium, high, highest, critical
    
    # Agile fields
    story_points = db.Column(db.Integer)  # 1, 2, 3, 5, 8, 13, 21
    
    # Time tracking
    time_estimate = db.Column(db.Float)  # Original estimate in hours
    time_spent = db.Column(db.Float, default=0)  # Time logged in hours
    time_remaining = db.Column(db.Float)  # Remaining estimate
    
    # Dates
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    due_date = db.Column(db.DateTime)
    resolved_at = db.Column(db.DateTime)
    closed_at = db.Column(db.DateTime)
    
    # Timeline view fields
    start_date = db.Column(db.DateTime)  # For Gantt chart
    end_date = db.Column(db.DateTime)    # For Gantt chart
    
    # Kanban ordering
    position = db.Column(db.Integer, default=0)
    
    # Relationships
    assignee = db.relationship('User', foreign_keys=[assignee_id], backref='assigned_issues')
    reporter = db.relationship('User', foreign_keys=[reporter_id], backref='reported_issues')
    labels = db.relationship('Label', secondary=issue_labels, backref='issues')
    comments = db.relationship('Comment', backref='issue', lazy=True, cascade='all, delete-orphan', order_by='Comment.created_at')
    attachments = db.relationship('Attachment', backref='issue', lazy=True, cascade='all, delete-orphan')
    subtasks = db.relationship('Issue', backref=db.backref('parent', remote_side=[id]))
    watchers = db.relationship('IssueWatcher', backref='issue', lazy=True, cascade='all, delete-orphan')
    
    @property
    def description(self):
        return decrypt_field(self.description_encrypted)
    
    @description.setter
    def description(self, value):
        if value:
            self.description_encrypted = encrypt_field(value)
    
    @property
    def comment_count(self):
        return len(self.comments)
    
    @property
    def attachment_count(self):
        return len(self.attachments)
    
    def __repr__(self):
        return f'<Issue {self.key}>'

class IssueLink(db.Model):
    """Issue dependencies and relationships"""
    __tablename__ = 'issue_link'
    
    id = db.Column(db.Integer, primary_key=True)
    source_issue_id = db.Column(db.Integer, db.ForeignKey('issue.id', ondelete='CASCADE'), nullable=False)
    target_issue_id = db.Column(db.Integer, db.ForeignKey('issue.id', ondelete='CASCADE'), nullable=False)
    link_type = db.Column(db.String(20), nullable=False)  # blocks, is_blocked_by, relates_to, duplicates, clones
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    source_issue = db.relationship('Issue', foreign_keys=[source_issue_id], backref='outgoing_links')
    target_issue = db.relationship('Issue', foreign_keys=[target_issue_id], backref='incoming_links')
    
    def __repr__(self):
        return f'<IssueLink {self.source_issue_id} -> {self.target_issue_id}>'

class Comment(db.Model):
    """Comment model for issue discussions"""
    __tablename__ = 'comment'
    
    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey('issue.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    text_encrypted = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    edited = db.Column(db.Boolean, default=False)
    
    user = db.relationship('User', backref='comments')
    
    @property
    def text(self):
        return decrypt_field(self.text_encrypted)
    
    @text.setter
    def text(self, value):
        self.text_encrypted = encrypt_field(value)
    
    def __repr__(self):
        return f'<Comment {self.id} on Issue {self.issue_id}>'

class Attachment(db.Model):
    """Attachment model for issue files"""
    __tablename__ = 'attachment'
    
    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey('issue.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='attachments')
    
    def __repr__(self):
        return f'<Attachment {self.filename}>'

class IssueWatcher(db.Model):
    """Users watching an issue for notifications"""
    __tablename__ = 'issue_watcher'
    
    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey('issue.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='watched_issues')
    
    def __repr__(self):
        return f'<IssueWatcher user:{self.user_id} issue:{self.issue_id}>'

class WorkflowTransition(db.Model):
    """Track workflow state transitions for audit"""
    __tablename__ = 'workflow_transition'
    
    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey('issue.id', ondelete='CASCADE'), nullable=False)
    from_status = db.Column(db.String(20), nullable=False)
    to_status = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comment = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    issue = db.relationship('Issue', backref='transitions')
    user = db.relationship('User', backref='transitions')
    
    def __repr__(self):
        return f'<WorkflowTransition {self.from_status} -> {self.to_status}>'

class ProjectUpdate(db.Model):
    """Project update model with status and progress tracking"""
    __tablename__ = 'project_update'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    update_text_encrypted = db.Column(db.Text, nullable=False)
    hours_worked = db.Column(db.Float, default=0)
    
    # Status tracking fields
    status = db.Column(db.String(50), default='on_track')  # on_track, at_risk, blocked
    progress_percentage = db.Column(db.Integer, default=0)  # 0-100
    blockers_encrypted = db.Column(db.Text)  # Encrypted blockers/impediments
    completion_notes_encrypted = db.Column(db.Text)  # Encrypted notes
    
    # Reporting period
    reporting_period = db.Column(db.String(20), default='daily')  # daily, weekly, monthly
    
    # Resource tracking
    team_members_count = db.Column(db.Integer)
    estimated_completion_days = db.Column(db.Float)
    
    date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    user = db.relationship('User', backref='project_updates')
    
    @property
    def update_text(self):
        return decrypt_field(self.update_text_encrypted)
    
    @update_text.setter
    def update_text(self, value):
        self.update_text_encrypted = encrypt_field(value)
    
    @property
    def blockers(self):
        return decrypt_field(self.blockers_encrypted)
    
    @blockers.setter
    def blockers(self, value):
        self.blockers_encrypted = encrypt_field(value)
    
    @property
    def completion_notes(self):
        return decrypt_field(self.completion_notes_encrypted)
    
    @completion_notes.setter
    def completion_notes(self, value):
        self.completion_notes_encrypted = encrypt_field(value)
    
    def __repr__(self):
        return f'<ProjectUpdate {self.id} - {self.status}>'

class AuditLog(db.Model):
    """Audit log for security tracking"""
    __tablename__ = 'audit_log'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'))
    action = db.Column(db.String(100), nullable=False)
    details_encrypted = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    @property
    def details(self):
        return decrypt_field(self.details_encrypted)
    
    @details.setter
    def details(self, value):
        if value:
            self.details_encrypted = encrypt_field(value)
    
    def __repr__(self):
        return f'<AuditLog {self.action}>'

class RecentItem(db.Model):
    """Track recently viewed items for quick access"""
    __tablename__ = 'recent_item'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    item_type = db.Column(db.String(20), nullable=False)  # 'issue', 'project', 'board', 'sprint', 'epic'
    item_id = db.Column(db.Integer, nullable=False)
    item_title = db.Column(db.String(200), nullable=False)
    item_key = db.Column(db.String(50))  # For issues (e.g., PROJ-123)
    viewed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Composite unique constraint to prevent duplicates
    __table_args__ = (
        db.UniqueConstraint('user_id', 'item_type', 'item_id', name='uq_user_item'),
    )
    
    def __repr__(self):
        return f'<RecentItem {self.item_type}:{self.item_id}>'
class Notification(db.Model):
    """User notifications for activities and updates"""
    __tablename__ = 'notification'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    type = db.Column(db.String(50), nullable=False)  # 'issue_assigned', 'comment', 'mention', 'status_change', etc.
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text)
    link = db.Column(db.String(500))  # URL to navigate to
    icon = db.Column(db.String(50), default='bell')  # Lucide icon name
    is_read = db.Column(db.Boolean, default=False, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    read_at = db.Column(db.DateTime)
    
    # Optional reference to related items
    related_type = db.Column(db.String(20))  # 'issue', 'project', 'comment'
    related_id = db.Column(db.Integer)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('notifications', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Notification {self.id}: {self.type}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'title': self.title,
            'message': self.message,
            'link': self.link,
            'icon': self.icon,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'related_type': self.related_type,
            'related_id': self.related_id,
        }
class StarredItem(db.Model):
    """Track starred/favorite items for quick access"""
    __tablename__ = 'starred_item'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    item_type = db.Column(db.String(20), nullable=False)  # 'issue', 'project', 'board', 'filter'
    item_id = db.Column(db.Integer, nullable=False)
    item_title = db.Column(db.String(200), nullable=False)
    item_key = db.Column(db.String(50))  # For issues
    starred_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Composite unique constraint to prevent duplicates
    __table_args__ = (
        db.UniqueConstraint('user_id', 'item_type', 'item_id', name='uq_user_starred'),
    )
    
    def __repr__(self):
        return f'<StarredItem {self.item_type}:{self.item_id}>'


class FacialIDData(db.Model):
    """Store facial recognition data for admin biometric authentication"""
    __tablename__ = 'facial_id_data'
    
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), 
                         nullable=False, index=True)
    
    # Encrypted facial encoding (128-dimensional vector)
    facial_encoding = db.Column(db.Text, nullable=False)
    
    # Face preview image (base64 encoded for display)
    face_preview = db.Column(db.Text, nullable=True)
    
    # Label for this encoding (e.g., "phone", "laptop", "office")
    encoding_label = db.Column(db.String(100), default='default')
    
    # Hash of encoding for quick comparison
    encoding_hash = db.Column(db.String(255), unique=True, nullable=False)
    
    # Verification status
    is_verified = db.Column(db.Boolean, default=False, index=True)
    
    # Enrollment and verification timestamps
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    verified_at = db.Column(db.DateTime, nullable=True)
    
    # Security tracking
    successful_unlocks = db.Column(db.Integer, default=0)  # Successful authentications
    failed_attempts = db.Column(db.Integer, default=0)     # Failed authentications
    last_unlock_at = db.Column(db.DateTime, nullable=True)  # Last successful unlock
    last_failed_attempt_at = db.Column(db.DateTime, nullable=True)  # Last failed attempt
    
    # Metadata
    device_info = db.Column(db.String(255), nullable=True)  # Device where face was captured
    camera_type = db.Column(db.String(100), nullable=True)  # Type of camera used
    capture_quality = db.Column(db.Float, nullable=True)    # Quality score 0-1
    
    # Composite index for performance
    __table_args__ = (
        db.Index('ix_admin_verified', 'admin_id', 'is_verified'),
        db.Index('ix_admin_enrolled', 'admin_id', 'enrolled_at'),
    )
    
    def __repr__(self):
        return f'<FacialIDData admin_id={self.admin_id} verified={self.is_verified}>'
    
    def to_dict(self):
        """Convert to dictionary representation"""
        return {
            'id': self.id,
            'admin_id': self.admin_id,
            'encoding_label': self.encoding_label,
            'is_verified': self.is_verified,
            'enrolled_at': self.enrolled_at.isoformat() if self.enrolled_at else None,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
            'successful_unlocks': self.successful_unlocks,
            'failed_attempts': self.failed_attempts,
            'last_unlock_at': self.last_unlock_at.isoformat() if self.last_unlock_at else None,
            'last_failed_attempt_at': self.last_failed_attempt_at.isoformat() if self.last_failed_attempt_at else None,
            'device_info': self.device_info,
            'camera_type': self.camera_type,
            'capture_quality': self.capture_quality,
        }