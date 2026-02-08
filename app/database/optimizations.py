# app/database/optimizations.py
"""
Database optimization strategies including indexing, query optimization, and caching.
"""

from app.models import db, User, Project, Issue, ProgressUpdate
from sqlalchemy import Index, event
import logging

logger = logging.getLogger('database')


def create_database_indexes():
    """Create all necessary database indexes for performance."""
    
    # User indexes
    User.__table__.indexes.add(
        Index('idx_user_email', User.email, unique=True)
    )
    User.__table__.indexes.add(
        Index('idx_user_role', User.role)
    )
    User.__table__.indexes.add(
        Index('idx_user_created', User.created_at)
    )
    User.__table__.indexes.add(
        Index('idx_user_active', User.is_active)
    )
    
    # Project indexes
    Project.__table__.indexes.add(
        Index('idx_project_owner', Project.owner_id)
    )
    Project.__table__.indexes.add(
        Index('idx_project_status', Project.status)
    )
    Project.__table__.indexes.add(
        Index('idx_project_created', Project.created_at)
    )
    Project.__table__.indexes.add(
        Index('idx_project_owner_status', Project.owner_id, Project.status)
    )
    
    # Issue indexes
    Issue.__table__.indexes.add(
        Index('idx_issue_project', Issue.project_id)
    )
    Issue.__table__.indexes.add(
        Index('idx_issue_assignee', Issue.assignee_id)
    )
    Issue.__table__.indexes.add(
        Index('idx_issue_status', Issue.status)
    )
    Issue.__table__.indexes.add(
        Index('idx_issue_priority', Issue.priority)
    )
    Issue.__table__.indexes.add(
        Index('idx_issue_created', Issue.created_at)
    )
    Issue.__table__.indexes.add(
        Index('idx_issue_project_status', Issue.project_id, Issue.status)
    )
    Issue.__table__.indexes.add(
        Index('idx_issue_assignee_status', Issue.assignee_id, Issue.status)
    )
    
    # ProgressUpdate indexes
    ProgressUpdate.__table__.indexes.add(
        Index('idx_progress_user', ProgressUpdate.user_id)
    )
    ProgressUpdate.__table__.indexes.add(
        Index('idx_progress_project', ProgressUpdate.project_id)
    )
    ProgressUpdate.__table__.indexes.add(
        Index('idx_progress_created', ProgressUpdate.created_at)
    )
    ProgressUpdate.__table__.indexes.add(
        Index('idx_progress_status', ProgressUpdate.status)
    )
    ProgressUpdate.__table__.indexes.add(
        Index('idx_progress_user_created', ProgressUpdate.user_id, ProgressUpdate.created_at)
    )
    
    logger.info("Database indexes created successfully")


def optimize_query_loading():
    """Configure eager loading to prevent N+1 query problems."""
    
    # Configure relationship loading strategies
    from sqlalchemy.orm import selectinload, joinedload
    
    # Eager load user relationships
    User.projects = db.relationship(
        'Project',
        lazy='select',  # Use regular select, will be optimized with selectinload
        cascade='all, delete-orphan'
    )
    
    # Eager load project relationships
    Project.issues = db.relationship(
        'Issue',
        lazy='select',
        cascade='all, delete-orphan'
    )
    
    Project.team = db.relationship(
        'User',
        secondary='project_team',
        lazy='select'
    )
    
    # Eager load issue relationships
    Issue.assignee = db.relationship(
        'User',
        lazy='select',
        uselist=False
    )
    
    logger.info("Query loading optimizations applied")


class QueryOptimizer:
    """Utility class for optimized queries."""
    
    @staticmethod
    def get_user_with_projects(user_id, limit=100):
        """Get user with their projects (optimized)."""
        from sqlalchemy.orm import selectinload
        
        return User.query.options(
            selectinload(User.projects)
        ).filter_by(id=user_id).first()
    
    @staticmethod
    def get_project_with_issues(project_id):
        """Get project with all issues (optimized)."""
        from sqlalchemy.orm import selectinload
        
        return Project.query.options(
            selectinload(Project.issues).selectinload(Issue.assignee)
        ).filter_by(id=project_id).first()
    
    @staticmethod
    def get_issues_by_assignee(user_id, status=None):
        """Get issues assigned to user (optimized)."""
        from sqlalchemy.orm import selectinload
        
        query = Issue.query.options(
            selectinload(Issue.assignee),
            selectinload(Issue.project)
        ).filter_by(assignee_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        return query.all()
    
    @staticmethod
    def get_recent_progress_updates(limit=20):
        """Get recent progress updates (optimized)."""
        from sqlalchemy.orm import selectinload
        
        return ProgressUpdate.query.options(
            selectinload(ProgressUpdate.user),
            selectinload(ProgressUpdate.project)
        ).order_by(
            ProgressUpdate.created_at.desc()
        ).limit(limit).all()
    
    @staticmethod
    def get_user_stats(user_id):
        """Get user statistics in single query."""
        from sqlalchemy import func
        
        stats = {
            'total_issues_assigned': Issue.query.filter_by(assignee_id=user_id).count(),
            'total_issues_created': Issue.query.filter_by(created_by=user_id).count(),
            'total_projects': Project.query.filter_by(owner_id=user_id).count(),
            'total_updates': ProgressUpdate.query.filter_by(user_id=user_id).count(),
            'completed_issues': Issue.query.filter_by(
                assignee_id=user_id, 
                status='completed'
            ).count(),
        }
        return stats
    
    @staticmethod
    def get_project_stats(project_id):
        """Get project statistics in optimized query."""
        from sqlalchemy import func
        
        issues = Issue.query.filter_by(project_id=project_id).all()
        
        stats = {
            'total_issues': len(issues),
            'completed_issues': len([i for i in issues if i.status == 'completed']),
            'pending_issues': len([i for i in issues if i.status == 'pending']),
            'in_progress': len([i for i in issues if i.status == 'in_progress']),
            'total_team': Project.query.get(project_id).team.__len__(),
        }
        return stats


class DatabaseConnectionPool:
    """Manage database connection pooling for efficiency."""
    
    @staticmethod
    def configure_pooling(app):
        """Configure connection pooling in Flask app."""
        from sqlalchemy.pool import QueuePool
        
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'poolclass': QueuePool,
            'pool_size': 10,  # Number of connections to keep in pool
            'max_overflow': 20,  # Number of additional connections allowed
            'pool_pre_ping': True,  # Test connections before using
            'pool_recycle': 3600,  # Recycle connections after 1 hour
        }
        
        logger.info("Database connection pooling configured")
    
    @staticmethod
    def monitor_pool_health(app):
        """Monitor database connection pool health."""
        
        @app.route('/admin/db-pool-health')
        def pool_health():
            from flask import jsonify
            pool = db.engine.pool
            
            return jsonify({
                'checked_in': pool.checkedout() if hasattr(pool, 'checkedout') else 'N/A',
                'total_connections': pool.size() if hasattr(pool, 'size') else 'N/A',
                'overflow': pool.overflow() if hasattr(pool, 'overflow') else 'N/A',
            })


# Register slow query logging
def setup_slow_query_logging(app):
    """Log queries that take longer than 500ms."""
    
    @event.listens_for(db.engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        conn.info.setdefault('query_start_time', []).append(time.time())
    
    @event.listens_for(db.engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        import time
        total_time = time.time() - conn.info['query_start_time'].pop(-1)
        
        if total_time > 0.5:  # Log queries longer than 500ms
            logger.warning(f"SLOW QUERY ({total_time:.2f}s): {statement}")
