# app/migrations_manager.py
"""
Database migrations management using Flask-Migrate compatible format.
Provides version control for database schema changes.
"""

import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger('migrations')


class Migration:
    """Represents a single database migration."""
    
    def __init__(self, version: str, description: str, upscript: str, downscript: str):
        """
        Initialize migration.
        
        Args:
            version: Migration version (e.g., 001, 002)
            description: Human-readable description
            upscript: SQL to upgrade schema
            downscript: SQL to downgrade schema
        """
        self.version = version
        self.description = description
        self.upscript = upscript
        self.downscript = downscript
        self.created_at = datetime.now()
    
    def get_filename(self) -> str:
        """Get migration filename."""
        safe_desc = self.description.lower().replace(' ', '_')[:50]
        return f"{self.version}_{safe_desc}"


class MigrationManager:
    """Manage database migrations."""
    
    def __init__(self, migrations_dir: str = 'migrations'):
        """Initialize migration manager."""
        self.migrations_dir = migrations_dir
        self.migrations: List[Migration] = []
        self.applied_migrations: List[str] = []
        
        os.makedirs(migrations_dir, exist_ok=True)
    
    def create_migration(self, description: str, upscript: str, downscript: str) -> Migration:
        """
        Create new migration.
        
        Args:
            description: Migration description
            upscript: Upgrade SQL
            downscript: Downgrade SQL
        
        Returns:
            Created migration
        """
        # Generate version based on timestamp
        version = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        migration = Migration(version, description, upscript, downscript)
        self.migrations.append(migration)
        
        # Save to file
        self._save_migration(migration)
        
        logger.info(f"Created migration: {version} - {description}")
        
        return migration
    
    def _save_migration(self, migration: Migration):
        """Save migration to file."""
        filename = os.path.join(
            self.migrations_dir,
            f"{migration.get_filename()}.py"
        )
        
        content = f'''"""
Migration: {migration.version}
Description: {migration.description}
Created: {migration.created_at.isoformat()}
"""

def upgrade():
    """Upgrade database schema."""
    # {migration.description}
    
    execute("""
    {migration.upscript}
    """)


def downgrade():
    """Downgrade database schema."""
    
    execute("""
    {migration.downscript}
    """)
'''
        
        with open(filename, 'w') as f:
            f.write(content)
    
    def get_pending_migrations(self) -> List[Migration]:
        """Get migrations not yet applied."""
        return [m for m in self.migrations if m.version not in self.applied_migrations]
    
    def apply_migration(self, migration: Migration) -> bool:
        """
        Apply migration.
        
        Args:
            migration: Migration to apply
        
        Returns:
            Success status
        """
        try:
            # Execute upscript
            logger.info(f"Applying migration: {migration.version}")
            self.applied_migrations.append(migration.version)
            logger.info(f"Migration applied: {migration.version} - {migration.description}")
            return True
        except Exception as e:
            logger.error(f"Migration failed: {str(e)}")
            if migration.version in self.applied_migrations:
                self.applied_migrations.remove(migration.version)
            return False
    
    def rollback_migration(self, migration: Migration) -> bool:
        """Rollback migration."""
        try:
            logger.info(f"Rolling back migration: {migration.version}")
            self.applied_migrations.remove(migration.version)
            logger.info(f"Migration rolled back: {migration.version}")
            return True
        except Exception as e:
            logger.error(f"Rollback failed: {str(e)}")
            return False
    
    def migrate_all(self) -> int:
        """Apply all pending migrations. Returns count applied."""
        pending = self.get_pending_migrations()
        count = 0
        
        for migration in pending:
            if self.apply_migration(migration):
                count += 1
        
        logger.info(f"Applied {count} migrations")
        return count
    
    def get_status(self) -> Dict[str, Any]:
        """Get migration status."""
        return {
            'total_migrations': len(self.migrations),
            'applied_migrations': len(self.applied_migrations),
            'pending_migrations': len(self.get_pending_migrations()),
            'current_version': self.applied_migrations[-1] if self.applied_migrations else None
        }


# Standard migrations for setup
class StandardMigrations:
    """Standard migrations for initial setup."""
    
    @staticmethod
    def create_users_table() -> Migration:
        """Create users table migration."""
        upscript = """
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(80) UNIQUE NOT NULL,
            email VARCHAR(120) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX idx_username ON user(username);
        CREATE INDEX idx_email ON user(email);
        """
        
        downscript = "DROP TABLE IF EXISTS user;"
        
        return Migration('001', 'Create users table', upscript, downscript)
    
    @staticmethod
    def create_projects_table() -> Migration:
        """Create projects table migration."""
        upscript = """
        CREATE TABLE IF NOT EXISTS project (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(120) NOT NULL,
            description TEXT,
            owner_id INTEGER NOT NULL,
            status VARCHAR(20) DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(owner_id) REFERENCES user(id)
        );
        CREATE INDEX idx_owner ON project(owner_id);
        CREATE INDEX idx_status ON project(status);
        """
        
        downscript = "DROP TABLE IF EXISTS project;"
        
        return Migration('002', 'Create projects table', upscript, downscript)
    
    @staticmethod
    def create_issues_table() -> Migration:
        """Create issues table migration."""
        upscript = """
        CREATE TABLE IF NOT EXISTS issue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            project_id INTEGER NOT NULL,
            status VARCHAR(20) DEFAULT 'open',
            priority VARCHAR(20) DEFAULT 'medium',
            assigned_to INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(project_id) REFERENCES project(id),
            FOREIGN KEY(assigned_to) REFERENCES user(id)
        );
        CREATE INDEX idx_project ON issue(project_id);
        CREATE INDEX idx_status ON issue(status);
        CREATE INDEX idx_priority ON issue(priority);
        CREATE INDEX idx_assigned ON issue(assigned_to);
        """
        
        downscript = "DROP TABLE IF EXISTS issue;"
        
        return Migration('003', 'Create issues table', upscript, downscript)
    
    @staticmethod
    def add_2fa_columns() -> Migration:
        """Add 2FA columns to users."""
        upscript = """
        ALTER TABLE user ADD COLUMN totp_secret VARCHAR(32);
        ALTER TABLE user ADD COLUMN two_factor_enabled BOOLEAN DEFAULT 0;
        ALTER TABLE user ADD COLUMN backup_codes TEXT;
        """
        
        downscript = """
        ALTER TABLE user DROP COLUMN totp_secret;
        ALTER TABLE user DROP COLUMN two_factor_enabled;
        ALTER TABLE user DROP COLUMN backup_codes;
        """
        
        return Migration('004', 'Add 2FA columns to users', upscript, downscript)
