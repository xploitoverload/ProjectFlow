"""
Database Connection Management Module
Supports multiple database types with connection pooling, health checks, and failover
"""

import os
import json
from typing import Optional, Dict, Any
from sqlalchemy import create_engine, event, pool, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import OperationalError
import logging
from datetime import datetime
import pymongo
import redis

logger = logging.getLogger(__name__)


class DatabaseConnectionPool:
    """Manages connections to multiple database backends"""
    
    def __init__(self, config):
        self.config = config
        self.engines = {}
        self.sessions = {}
        self.connections = {}
        self.health_status = {}
        
    def get_engine(self, db_type: str = 'primary'):
        """Get or create SQLAlchemy engine for specified database"""
        
        if db_type in self.engines:
            return self.engines[db_type]
        
        db_config = self.config.get(db_type, {})
        if not db_config.get('url'):
            raise ValueError(f"No database URL configured for {db_type}")
        
        # Create engine with pooling configuration
        engine = create_engine(
            db_config['url'],
            poolclass=pool.QueuePool,
            pool_size=db_config.get('pool_size', 20),
            max_overflow=db_config.get('max_overflow', 10),
            pool_timeout=db_config.get('pool_timeout', 30),
            pool_recycle=db_config.get('pool_recycle', 3600),
            pool_pre_ping=db_config.get('pool_pre_ping', True),
            echo=db_config.get('echo', False),
            connect_args=db_config.get('connect_args', {})
        )
        
        # Add connection event listeners for monitoring
        self._setup_event_listeners(engine, db_type)
        
        self.engines[db_type] = engine
        self.health_status[db_type] = {
            'status': 'unknown',
            'last_check': None,
            'error': None
        }
        
        logger.info(f"Created database engine for {db_type}: {db_config.get('name', 'unknown')}")
        return engine
    
    def get_session(self, db_type: str = 'primary'):
        """Get thread-local SQLAlchemy session"""
        
        if db_type not in self.sessions:
            engine = self.get_engine(db_type)
            session_factory = sessionmaker(bind=engine)
            self.sessions[db_type] = scoped_session(session_factory)
        
        return self.sessions[db_type]
    
    def get_mongodb(self, db_type: str = 'mongodb'):
        """Get MongoDB connection"""
        
        if db_type in self.connections:
            return self.connections[db_type]
        
        db_config = self.config.get(db_type, {})
        if not db_config.get('url'):
            raise ValueError(f"No MongoDB URL configured for {db_type}")
        
        try:
            client = pymongo.MongoClient(
                db_config['url'],
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                retryWrites=True,
                w='majority'
            )
            # Test connection
            client.server_info()
            
            db = client[db_config.get('database', 'project_mgmt')]
            self.connections[db_type] = db
            self.health_status[db_type] = {
                'status': 'healthy',
                'last_check': datetime.utcnow(),
                'error': None
            }
            
            logger.info(f"Connected to MongoDB: {db_config.get('name', 'unknown')}")
            return db
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB {db_type}: {str(e)}")
            self.health_status[db_type] = {
                'status': 'unhealthy',
                'last_check': datetime.utcnow(),
                'error': str(e)
            }
            raise
    
    def get_redis(self, db_type: str = 'cache'):
        """Get Redis connection"""
        
        if db_type in self.connections:
            return self.connections[db_type]
        
        db_config = self.config.get(db_type, {})
        if not db_config.get('url'):
            raise ValueError(f"No Redis URL configured for {db_type}")
        
        try:
            client = redis.from_url(
                db_config['url'],
                socket_connect_timeout=5,
                socket_keepalive=True,
                health_check_interval=30,
                decode_responses=True
            )
            # Test connection
            client.ping()
            
            self.connections[db_type] = client
            self.health_status[db_type] = {
                'status': 'healthy',
                'last_check': datetime.utcnow(),
                'error': None
            }
            
            logger.info(f"Connected to Redis: {db_config.get('name', 'unknown')}")
            return client
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis {db_type}: {str(e)}")
            self.health_status[db_type] = {
                'status': 'unhealthy',
                'last_check': datetime.utcnow(),
                'error': str(e)
            }
            raise
    
    def _setup_event_listeners(self, engine, db_type: str):
        """Setup event listeners for connection monitoring"""
        
        @event.listens_for(engine, "connect")
        def receive_connect(dbapi_conn, connection_record):
            # Log successful connections
            logger.debug(f"Connection established to {db_type}")
            self.health_status[db_type]['last_check'] = datetime.utcnow()
            self.health_status[db_type]['status'] = 'healthy'
        
        @event.listens_for(engine, "checkout")
        def receive_checkout(dbapi_conn, connection_record, connection_proxy):
            # Execute pre-ping query to verify connection health
            try:
                dbapi_conn.scalar(text("SELECT 1"))
            except Exception as e:
                logger.warning(f"Connection health check failed for {db_type}: {str(e)}")
                raise
        
        @event.listens_for(engine, "close")
        def receive_close(dbapi_conn, connection_record):
            logger.debug(f"Connection closed for {db_type}")
    
    def check_health(self, db_type: str = None) -> Dict[str, Any]:
        """Check health of database connections"""
        
        if db_type:
            return self._check_single_health(db_type)
        else:
            return {db: self._check_single_health(db) for db in self.engines.keys()}
    
    def _check_single_health(self, db_type: str) -> Dict[str, Any]:
        """Check health of single database"""
        
        try:
            if db_type in self.engines:
                with self.engines[db_type].connect() as conn:
                    conn.execute(text("SELECT 1"))
                    self.health_status[db_type] = {
                        'status': 'healthy',
                        'last_check': datetime.utcnow(),
                        'error': None
                    }
            elif db_type.startswith('mongodb'):
                self.get_mongodb(db_type)
            elif db_type.startswith('redis'):
                client = self.get_redis(db_type)
                client.ping()
                
            return self.health_status.get(db_type, {'status': 'unknown'})
            
        except Exception as e:
            logger.error(f"Health check failed for {db_type}: {str(e)}")
            self.health_status[db_type] = {
                'status': 'unhealthy',
                'last_check': datetime.utcnow(),
                'error': str(e)
            }
            return self.health_status[db_type]
    
    def failover_to_replica(self, primary_type: str, replica_type: str) -> bool:
        """Failover from primary to replica database"""
        
        try:
            logger.warning(f"Attempting failover from {primary_type} to {replica_type}")
            
            # Verify replica is healthy
            replica_health = self._check_single_health(replica_type)
            if replica_health['status'] != 'healthy':
                logger.error(f"Cannot failover: replica {replica_type} is not healthy")
                return False
            
            # Update primary reference to replica
            if primary_type in self.engines:
                del self.engines[primary_type]
            if primary_type in self.sessions:
                del self.sessions[primary_type]
            
            # Use replica as primary
            self.engines[primary_type] = self.engines[replica_type]
            self.sessions[primary_type] = self.sessions[replica_type]
            
            logger.info(f"Failover successful: {primary_type} → {replica_type}")
            return True
            
        except Exception as e:
            logger.error(f"Failover failed: {str(e)}")
            return False
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        
        stats = {}
        for db_type, engine in self.engines.items():
            pool_obj = engine.pool
            stats[db_type] = {
                'pool_size': pool_obj.size(),
                'checked_in': pool_obj.checkedin(),
                'checked_out': pool_obj.checkedout(),
                'overflow': pool_obj.overflow(),
                'health': self.health_status.get(db_type, {})
            }
        return stats
    
    def close_all(self):
        """Close all database connections"""
        
        for db_type, engine in self.engines.items():
            try:
                engine.dispose()
                logger.info(f"Closed connection pool for {db_type}")
            except Exception as e:
                logger.error(f"Error closing {db_type}: {str(e)}")
        
        for db_type, client in self.connections.items():
            try:
                if hasattr(client, 'close'):
                    client.close()
                    logger.info(f"Closed connection for {db_type}")
            except Exception as e:
                logger.error(f"Error closing {db_type}: {str(e)}")


# Global instance
db_pool = None


def init_database_pool(app_config):
    """Initialize global database connection pool"""
    
    global db_pool
    
    # Build database configurations from environment variables
    db_configs = {
        'primary': {
            'url': os.environ.get('DATABASE_URL', 'sqlite:///project_mgmt.db'),
            'name': 'Primary Database',
            'pool_size': int(os.environ.get('DB_POOL_SIZE', '20')),
            'max_overflow': int(os.environ.get('DB_MAX_OVERFLOW', '10')),
            'pool_timeout': int(os.environ.get('DB_POOL_TIMEOUT', '30')),
            'pool_recycle': int(os.environ.get('DB_POOL_RECYCLE', '3600')),
            'pool_pre_ping': True
        }
    }
    
    # Add read replica if configured
    if os.environ.get('DATABASE_REPLICA_URL'):
        db_configs['replica'] = {
            'url': os.environ.get('DATABASE_REPLICA_URL'),
            'name': 'Read Replica',
            'pool_size': 30,
            'pool_recycle': 3600,
            'pool_pre_ping': True
        }
    
    # Add MongoDB if configured
    if os.environ.get('MONGODB_URL'):
        db_configs['mongodb'] = {
            'url': os.environ.get('MONGODB_URL'),
            'database': os.environ.get('MONGODB_DATABASE', 'project_mgmt'),
            'name': 'MongoDB'
        }
    
    # Add Redis if configured
    if os.environ.get('REDIS_URL'):
        db_configs['cache'] = {
            'url': os.environ.get('REDIS_URL'),
            'name': 'Redis Cache'
        }
    
    db_pool = DatabaseConnectionPool(db_configs)
    
    logger.info(f"Database connection pool initialized with {len(db_configs)} databases")
    return db_pool


def get_db_pool() -> DatabaseConnectionPool:
    """Get global database connection pool"""
    
    global db_pool
    if db_pool is None:
        raise RuntimeError("Database pool not initialized. Call init_database_pool first.")
    return db_pool
