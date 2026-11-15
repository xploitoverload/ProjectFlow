# models.py - Complete Jira-style Database Models with Ring 0 Hardened Security
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, date, timedelta, timezone
from cryptography.fernet import Fernet
from werkzeug.security import generate_password_hash, check_password_hash
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import hashlib
import json
import os

db = SQLAlchemy()
_hasher = PasswordHasher()

# Encryption key management
def get_encryption_key():
    """Get or create encryption key for database fields"""
    env_key = os.environ.get('SECRET_ENCRYPTION_KEY')
    if env_key:
        return env_key.encode() if isinstance(env_key, str) else env_key
    key_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'encryption.key')
    if os.path.exists(key_file):
        try:
            with open(key_file, 'rb') as f:
                key = f.read().strip()
                if len(key) == 44:
                    return key
        except Exception:
            pass
    # Deterministic fallback key for development / testing (valid 32-byte url-safe base64, 44 chars)
    return b'SSPcxXLWjHXEAw4EvOOkBQ9bxocTd8m1O-0VaHe8bRc='

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
    except (ValueError, TypeError, Exception):
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
    team_id = db.Column(db.Integer, db.ForeignKey('team.id', ondelete='SET NULL'), index=True)  # Core team assignment
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
        """Hash password using memory-hard Argon2id (OWASP standard)"""
        self.password = _hasher.hash(password)
    
    def check_password(self, password):
        """Verify password with Argon2id; supports transparent migration from legacy PBKDF2"""
        if not self.password:
            return False
        if self.password.startswith('$argon2'):
            try:
                return _hasher.verify(self.password, password)
            except VerifyMismatchError:
                return False
            except Exception:
                return False
        # Fallback verification for legacy hashes
        legacy_valid = check_password_hash(self.password, password)
        if legacy_valid:
            try:
                self.password = _hasher.hash(password)
                db.session.commit()
            except Exception:
                pass
        return legacy_valid
    
    @classmethod
    def find_by_email(cls, email):
        """Find user by email address safely decrypting encrypted emails."""
        if not email:
            return None
        clean_email = email.strip().lower()
        for u in cls.query.all():
            try:
                if u.email and u.email.strip().lower() == clean_email:
                    return u
            except Exception:
                continue
        return None
    
    def get_id(self):
        return str(self.id)
    
    def to_dict(self):
        """Serialize user to dictionary (safe fields only)"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'team_id': self.team_id,
            'team': self.team.name if self.team else None,
            'department': self.department,
            'is_active': getattr(self, 'is_active', True),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
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

    @property
    def progress(self):
        """Calculate completion percentage based on closed/done issues."""
        if not self.issues:
            return 0
        total = len(self.issues)
        done = sum(1 for i in self.issues if i.status in ['done', 'closed'])
        return int((done / total) * 100) if total > 0 else 0
    
    def get_members(self):
        """Get all active users eligible as members (from primary team and assigned teams)."""
        from app.models import User
        team_ids = set()
        if self.team_id:
            team_ids.add(self.team_id)
        if hasattr(self, 'teams') and self.teams:
            team_ids.update(t.id for t in self.teams)
        if not team_ids:
            return []
        return User.query.filter(User.team_id.in_(team_ids), User.is_active.is_(True)).all()
    
    def to_dict(self):
        """Serialize project to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'key': self.key,
            'description': self.description,
            'status': self.status,
            'workflow_type': self.workflow_type,
            'lead_id': self.lead_id,
            'lead': self.lead.username if self.lead else None,
            'team_id': self.team_id,
            'team': self.team.name if self.team else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'issues_count': len(self.issues) if self.issues else 0
        }
    
    def __repr__(self):
        return f'<Project {self.name}>'

class Sprint(db.Model):
    """Sprint model for Agile workflow"""
    __tablename__ = 'sprint'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id', ondelete='CASCADE'), nullable=False, index=True)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    goal = db.Column(db.Text)
    status = db.Column(db.String(20), default='planned', index=True)  # planned, active, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    issues = db.relationship('Issue', backref='sprint', lazy=True)
    
    def to_dict(self):
        """Serialize sprint to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'project_id': self.project_id,
            'goal': self.goal,
            'status': self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'issues_count': len(self.issues) if self.issues else 0
        }
    
    def __repr__(self):
        return f'<Sprint {self.name}>'

class Epic(db.Model):
    """Epic model for grouping issues"""
    __tablename__ = 'epic'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description_encrypted = db.Column(db.Text)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id', ondelete='CASCADE'), nullable=False, index=True)
    color = db.Column(db.String(7), default='#0052cc')
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='active', index=True)  # active, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    issues = db.relationship('Issue', backref='epic', lazy=True)
    
    @property
    def description(self):
        return decrypt_field(self.description_encrypted)
    
    @description.setter
    def description(self, value):
        if value:
            self.description_encrypted = encrypt_field(value)
    
    def to_dict(self):
        """Serialize epic to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'project_id': self.project_id,
            'color': self.color,
            'status': self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'issues_count': len(self.issues) if self.issues else 0
        }
    
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
    
    def to_dict(self):
        """Serialize label to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'project_id': self.project_id
        }
    
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
    epic_id = db.Column(db.Integer, db.ForeignKey('epic.id', ondelete='SET NULL'), index=True)
    sprint_id = db.Column(db.Integer, db.ForeignKey('sprint.id', ondelete='SET NULL'), index=True)
    assignee_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'), index=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'), index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('issue.id', ondelete='CASCADE'), index=True)  # For subtasks
    
    # Issue details
    issue_type = db.Column(db.String(20), default='task', index=True)  # story, task, bug, epic, subtask
    status = db.Column(db.String(20), default='open', index=True)  # open, todo, in_progress, code_review, testing, ready_deploy, done, closed, reopened
    priority = db.Column(db.String(20), default='medium', index=True)  # lowest, low, medium, high, highest, critical
    
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
    position = db.Column(db.Integer, default=0, index=True)
    
    # Composite indexes for Kanban, Backlog, and User performance
    __table_args__ = (
        db.Index('ix_issue_project_status_pos', 'project_id', 'status', 'position'),
        db.Index('ix_issue_sprint_status', 'sprint_id', 'status'),
        db.Index('ix_issue_assignee_status', 'assignee_id', 'status'),
    )
    
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
    
    def to_dict(self):
        """Serialize issue to dictionary"""
        return {
            'id': self.id,
            'key': self.key,
            'title': self.title,
            'description': self.description,
            'issue_type': self.issue_type,
            'status': self.status,
            'priority': self.priority,
            'story_points': self.story_points,
            'project_id': self.project_id,
            'sprint_id': self.sprint_id,
            'epic_id': self.epic_id,
            'assignee_id': self.assignee_id,
            'assignee': self.assignee.username if self.assignee else None,
            'reporter_id': self.reporter_id,
            'reporter': self.reporter.username if self.reporter else None,
            'labels': [label.name for label in self.labels] if self.labels else [],
            'comment_count': self.comment_count,
            'attachment_count': self.attachment_count,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'parent_id': self.parent_id,
            'parent_key': self.parent.key if self.parent else None,
            'parent_title': self.parent.title if self.parent else None,
            'position': self.position if self.position is not None else 0,
            'subtask_count': len(self.subtasks),
            'subtasks': [{'id': s.id, 'key': s.key, 'title': s.title, 'status': s.status} for s in self.subtasks],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Issue {self.key}>'

class IssueLink(db.Model):
    """Issue dependencies and relationships with full Jira & Plane parity"""
    __tablename__ = 'issue_link'
    
    RELATION_TYPES = [
        'relates_to',
        'blocks',
        'is_blocked_by',
        'duplicates',
        'is_duplicated_by',
        'clones',
        'is_cloned_by',
        'implements',
        'is_implemented_by'
    ]
    
    DEPENDENCY_TYPES = [
        'finish_to_start',  # FS: Task B cannot start until Task A finishes
        'start_to_start',    # SS: Task B cannot start until Task A starts
        'finish_to_finish'   # FF: Task B cannot finish until Task A finishes
    ]
    
    INVERSE_MAP = {
        'relates_to': 'relates_to',
        'blocks': 'is_blocked_by',
        'is_blocked_by': 'blocks',
        'duplicates': 'is_duplicated_by',
        'is_duplicated_by': 'duplicates',
        'clones': 'is_cloned_by',
        'is_cloned_by': 'clones',
        'implements': 'is_implemented_by',
        'is_implemented_by': 'implements',
        'finish_to_start': 'precedes_finish_to_start',
        'start_to_start': 'precedes_start_to_start',
        'finish_to_finish': 'precedes_finish_to_finish'
    }
    
    LABELS = {
        'relates_to': 'Relates to',
        'blocks': 'Blocks',
        'is_blocked_by': 'Is blocked by',
        'duplicates': 'Duplicates',
        'is_duplicated_by': 'Is duplicated by',
        'clones': 'Clones',
        'is_cloned_by': 'Is cloned by',
        'implements': 'Implements',
        'is_implemented_by': 'Is implemented by',
        'finish_to_start': 'Finish-to-Start (FS)',
        'start_to_start': 'Start-to-Start (SS)',
        'finish_to_finish': 'Finish-to-Finish (FF)'
    }
    
    id = db.Column(db.Integer, primary_key=True)
    source_issue_id = db.Column(db.Integer, db.ForeignKey('issue.id', ondelete='CASCADE'), nullable=False, index=True)
    target_issue_id = db.Column(db.Integer, db.ForeignKey('issue.id', ondelete='CASCADE'), nullable=False, index=True)
    link_type = db.Column(db.String(35), nullable=False)
    lag_days = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    source_issue = db.relationship('Issue', foreign_keys=[source_issue_id], backref=db.backref('outgoing_links', cascade='all, delete-orphan'))
    target_issue = db.relationship('Issue', foreign_keys=[target_issue_id], backref=db.backref('incoming_links', cascade='all, delete-orphan'))
    
    __table_args__ = (
        db.UniqueConstraint('source_issue_id', 'target_issue_id', 'link_type', name='uq_issue_link'),
        db.Index('ix_issue_link_type', 'link_type'),
    )
    
    @property
    def is_dependency(self):
        """Returns True if this is a scheduling dependency (FS, SS, FF), separate from ordinary relationships."""
        return self.link_type in self.DEPENDENCY_TYPES
    
    @property
    def is_relationship(self):
        """Returns True if this is an ordinary issue relationship (relates_to, blocks, duplicates, clones)."""
        return self.link_type in self.RELATION_TYPES
    
    @property
    def inverse_type(self):
        return self.INVERSE_MAP.get(self.link_type, self.link_type)
    
    @property
    def label(self):
        return self.LABELS.get(self.link_type, self.link_type.replace('_', ' ').title())
    
    def to_dict(self):
        return {
            'id': self.id,
            'source_issue_id': self.source_issue_id,
            'target_issue_id': self.target_issue_id,
            'source_key': self.source_issue.key if self.source_issue else None,
            'target_key': self.target_issue.key if self.target_issue else None,
            'source_title': self.source_issue.title if self.source_issue else None,
            'target_title': self.target_issue.title if self.target_issue else None,
            'source_status': self.source_issue.status if self.source_issue else None,
            'target_status': self.target_issue.status if self.target_issue else None,
            'link_type': self.link_type,
            'label': self.label,
            'inverse_type': self.inverse_type,
            'is_dependency': self.is_dependency,
            'lag_days': self.lag_days or 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by
        }
    
    def __repr__(self):
        return f'<IssueLink {self.source_issue_id} -[{self.link_type}]-> {self.target_issue_id}>'

class Comment(db.Model):
    """Comment model for issue discussions"""
    __tablename__ = 'comment'
    
    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey('issue.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    text_encrypted = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    edited = db.Column(db.Boolean, default=False)
    
    user = db.relationship('User', backref='comments')
    
    @property
    def text(self):
        return decrypt_field(self.text_encrypted)
    
    @text.setter
    def text(self, value):
        self.text_encrypted = encrypt_field(value)
    
    @property
    def content(self):
        return self.text
    
    @content.setter
    def content(self, value):
        self.text = value
        
    @property
    def author_id(self):
        return self.user_id
        
    @author_id.setter
    def author_id(self, value):
        self.user_id = value
    
    def to_dict(self):
        """Serialize comment to dictionary"""
        return {
            'id': self.id,
            'issue_id': self.issue_id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else 'Unknown',
            'text': self.text,
            'edited': self.edited,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Comment {self.id} on Issue {self.issue_id}>'

class Attachment(db.Model):
    """Attachment model for issue files"""
    __tablename__ = 'attachment'
    
    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey('issue.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    user = db.relationship('User', backref='attachments')
    
    @property
    def filepath(self):
        """Alias for file_path for backwards compatibility"""
        return self.file_path
    
    def __repr__(self):
        return f'<Attachment {self.filename}>'

class IssueWatcher(db.Model):
    """Users watching an issue for notifications"""
    __tablename__ = 'issue_watcher'
    
    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey('issue.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='watched_issues')
    
    __table_args__ = (
        db.UniqueConstraint('issue_id', 'user_id', name='uq_issue_watcher'),
    )
    
    def __repr__(self):
        return f'<IssueWatcher user:{self.user_id} issue:{self.issue_id}>'

class WorkflowTransition(db.Model):
    """Track workflow state transitions for audit"""
    __tablename__ = 'workflow_transition'
    
    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey('issue.id', ondelete='CASCADE'), nullable=False, index=True)
    from_status = db.Column(db.String(20), nullable=False)
    to_status = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
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
    """Cryptographic Tamper-Evident Audit Ledger (Ring 0 Security)"""
    __tablename__ = 'audit_log'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'))
    action = db.Column(db.String(100), nullable=False)
    details_encrypted = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    # Cryptographic hash chain (blockchain/git style tamper detection)
    prev_hash = db.Column(db.String(64), nullable=True)
    record_hash = db.Column(db.String(64), nullable=True, index=True)
    
    __table_args__ = (
        db.Index('ix_audit_user_ts', 'user_id', 'timestamp'),
    )
    
    @property
    def details(self):
        return decrypt_field(self.details_encrypted)
    
    @details.setter
    def details(self, value):
        if value:
            self.details_encrypted = encrypt_field(value)
    
    def compute_hash(self, prev_hash: str = "0" * 64) -> str:
        """Compute SHA-256 hash chaining previous record and this record's payload"""
        ts_str = self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.timestamp else ""
        raw = f"{prev_hash}:{self.user_id}:{self.action}:{self.details_encrypted or ''}:{self.ip_address or ''}:{ts_str}"
        return hashlib.sha256(raw.encode('utf-8')).hexdigest()
    
    def to_dict(self):
        """Serialize audit log entry to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'details': self.details,
            'ip_address': self.ip_address,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'prev_hash': self.prev_hash,
            'record_hash': self.record_hash
        }
    
    def __repr__(self):
        return f'<AuditLog id={self.id} action={self.action} hash={self.record_hash[:8] if self.record_hash else "none"}>'

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


# ==============================================================================
# Phase 3: Project Intelligence, Working Calendars, Milestones & Baselines
# ==============================================================================

class Milestone(db.Model):
    """Milestone representing key delivery points, target deadlines, and checkpoints."""
    __tablename__ = 'milestone'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id', ondelete='CASCADE'), nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    target_date = db.Column(db.Date, nullable=False, index=True)
    status = db.Column(db.String(20), default='open', index=True)  # open, completed, missed
    completed_at = db.Column(db.DateTime, nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    project = db.relationship('Project', backref=db.backref('milestones', lazy='dynamic', cascade='all, delete-orphan'))
    owner = db.relationship('User', foreign_keys=[owner_id])

    @property
    def is_overdue(self):
        if self.status == 'completed':
            return False
        return self.target_date < date.today()

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'name': self.name,
            'description': self.description,
            'target_date': self.target_date.isoformat() if self.target_date else None,
            'status': self.status,
            'is_overdue': self.is_overdue,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'owner_id': self.owner_id,
            'owner_name': self.owner.username if self.owner else 'Unassigned',
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class WorkingCalendar(db.Model):
    """Working calendar defining working days, daily hours, and holiday exceptions."""
    __tablename__ = 'working_calendar'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id', ondelete='CASCADE'), nullable=True, index=True)
    name = db.Column(db.String(100), nullable=False, default='Standard Calendar')
    working_days = db.Column(db.String(50), default='0,1,2,3,4')  # 0=Monday .. 6=Sunday
    hours_per_day = db.Column(db.Float, default=8.0)
    holidays_json = db.Column(db.Text, default='[]')  # JSON array of "YYYY-MM-DD"
    timezone = db.Column(db.String(50), default='UTC')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    project = db.relationship('Project', backref=db.backref('working_calendar', uselist=False))

    def is_working_day(self, check_date):
        d = check_date if isinstance(check_date, date) else (check_date.date() if isinstance(check_date, datetime) else None)
        if not d:
            return False
        valid_days = [int(x.strip()) for x in self.working_days.split(',') if x.strip().isdigit()]
        if d.weekday() not in valid_days:
            return False
        try:
            hols = json.loads(self.holidays_json or '[]')
        except Exception:
            hols = []
        if d.isoformat() in hols:
            return False
        return True

    def add_working_days(self, start_d, days):
        """Add working days to a start date, skipping non-working days and holidays."""
        curr = start_d if isinstance(start_d, date) else (start_d.date() if isinstance(start_d, datetime) else None)
        if not curr:
            return None
        days = int(days)
        if days == 0:
            return curr
        step = 1 if days > 0 else -1
        remaining = abs(days)
        while remaining > 0:
            curr += timedelta(days=step)
            if self.is_working_day(curr):
                remaining -= 1
        return curr

    def working_days_between(self, start_d, end_d):
        """Count working days between start_d and end_d inclusive."""
        s = start_d if isinstance(start_d, date) else (start_d.date() if isinstance(start_d, datetime) else None)
        e = end_d if isinstance(end_d, date) else (end_d.date() if isinstance(end_d, datetime) else None)
        if not s or not e or s > e:
            return 0
        cnt = 0
        curr = s
        while curr <= e:
            if self.is_working_day(curr):
                cnt += 1
            curr += timedelta(days=1)
        return cnt

    def to_dict(self):
        try:
            hols = json.loads(self.holidays_json or '[]')
        except Exception:
            hols = []
        return {
            'id': self.id,
            'project_id': self.project_id,
            'name': self.name,
            'working_days': self.working_days,
            'hours_per_day': self.hours_per_day,
            'holidays': hols,
            'timezone': self.timezone
        }