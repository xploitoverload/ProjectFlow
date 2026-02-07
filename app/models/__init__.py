# app/models/__init__.py
"""Database models - re-exports from main models.py for compatibility."""

# Import from the root models.py for backward compatibility
# This allows both `from app.models import User` and `from models import User`

from models import (
    db,
    User,
    Team,
    Project,
    Sprint,
    Epic,
    Label,
    Issue,
    IssueLink,
    Comment,
    Attachment,
    IssueWatcher,
    WorkflowTransition,
    ProjectUpdate,
    AuditLog,
    RecentItem,
    StarredItem,
    FacialIDData,
    encrypt_field,
    decrypt_field
)

__all__ = [
    'db',
    'User',
    'Team', 
    'Project',
    'Sprint',
    'Epic',
    'Label',
    'Issue',
    'IssueLink',
    'Comment',
    'Attachment',
    'IssueWatcher',
    'WorkflowTransition',
    'ProjectUpdate',
    'AuditLog',
    'RecentItem',
    'StarredItem',
    'FacialIDData',
    'encrypt_field',
    'decrypt_field'
]

