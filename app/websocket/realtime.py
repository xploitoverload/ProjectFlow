# app/websocket/realtime.py
"""
Real-time WebSocket system for live updates and collaboration.
Note: Optional flask-socketio integration. Can work without it.
"""

import logging
import json
import threading
from typing import Dict, Set, List, Any, Optional, Callable
from datetime import datetime
from functools import wraps

logger = logging.getLogger('websocket')

# Try importing SocketIO (optional)
try:
    from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
    SOCKETIO_AVAILABLE = True
except ImportError:
    SOCKETIO_AVAILABLE = False
    logger.warning('flask-socketio not installed. WebSocket features disabled.')
    
    # Provide no-op replacements
    def emit(*args, **kwargs):
        pass
    
    def join_room(*args, **kwargs):
        pass
    
    def leave_room(*args, **kwargs):
        pass


class WebSocketEvent:
    """Represents a WebSocket event."""
    
    def __init__(self, event_type: str, data: Dict[str, Any], user_id: Optional[str] = None):
        """
        Initialize WebSocket event.
        
        Args:
            event_type: Type of event (e.g., 'issue_updated', 'comment_added')
            data: Event payload
            user_id: User who triggered the event
        """
        self.event_type = event_type
        self.data = data
        self.user_id = user_id
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'event_type': self.event_type,
            'data': self.data,
            'user_id': self.user_id,
            'timestamp': self.timestamp.isoformat()
        }


class ConnectionManager:
    """Manages WebSocket connections and rooms."""
    
    def __init__(self):
        """Initialize connection manager."""
        self.active_connections: Dict[str, Set[str]] = {}  # user_id -> session_ids
        self.room_members: Dict[str, Set[str]] = {}  # room_id -> user_ids
        self.user_metadata: Dict[str, Dict[str, Any]] = {}  # user_id -> metadata
        self.event_handlers: Dict[str, List[Callable]] = {}  # event_type -> handlers
        self.lock = threading.RLock()
    
    def register_connection(self, user_id: str, session_id: str):
        """Register a user connection."""
        with self.lock:
            if user_id not in self.active_connections:
                self.active_connections[user_id] = set()
            
            self.active_connections[user_id].add(session_id)
            logger.info(f"User {user_id} connected (sessions: {len(self.active_connections[user_id])})")
    
    def unregister_connection(self, user_id: str, session_id: str):
        """Unregister a user connection."""
        with self.lock:
            if user_id in self.active_connections:
                self.active_connections[user_id].discard(session_id)
                
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
                    self.user_metadata.pop(user_id, None)
                    logger.info(f"User {user_id} disconnected")
    
    def is_user_online(self, user_id: str) -> bool:
        """Check if user is online."""
        return user_id in self.active_connections
    
    def get_online_users(self) -> List[str]:
        """Get list of online users."""
        return list(self.active_connections.keys())
    
    def join_room(self, user_id: str, room_id: str):
        """Add user to room."""
        with self.lock:
            if room_id not in self.room_members:
                self.room_members[room_id] = set()
            
            self.room_members[room_id].add(user_id)
            logger.debug(f"User {user_id} joined room {room_id}")
    
    def leave_room(self, user_id: str, room_id: str):
        """Remove user from room."""
        with self.lock:
            if room_id in self.room_members:
                self.room_members[room_id].discard(user_id)
                
                if not self.room_members[room_id]:
                    del self.room_members[room_id]
                
                logger.debug(f"User {user_id} left room {room_id}")
    
    def get_room_members(self, room_id: str) -> List[str]:
        """Get members in room."""
        return list(self.room_members.get(room_id, set()))
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """Register handler for event type."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append(handler)
    
    def trigger_event_handlers(self, event: WebSocketEvent):
        """Trigger handlers for event."""
        if event.event_type in self.event_handlers:
            for handler in self.event_handlers[event.event_type]:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"Event handler error: {e}")
    
    def set_user_metadata(self, user_id: str, metadata: Dict[str, Any]):
        """Set user metadata."""
        with self.lock:
            self.user_metadata[user_id] = metadata
    
    def get_user_metadata(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user metadata."""
        return self.user_metadata.get(user_id)


# Global instances
_socketio: Optional[SocketIO] = None
_connection_manager: Optional[ConnectionManager] = None


def init_websocket(app, socketio: Optional[Any] = None) -> Optional[Any]:
    """
    Initialize WebSocket system.
    
    Usage in app.py:
        from flask_socketio import SocketIO
        
        socketio = SocketIO(app, cors_allowed_origins="*")
        init_websocket(app, socketio)
    """
    if not SOCKETIO_AVAILABLE:
        logger.warning('WebSocket not available - flask-socketio not installed')
        return None
    
    global _socketio, _connection_manager
    
    _socketio = socketio
    _connection_manager = ConnectionManager()
    
    if not SOCKETIO_AVAILABLE:
        logger.warning('WebSocket not available - flask-socketio not installed')
        return None
    
    # Register event handlers
    @_socketio.on('connect')
    def handle_connect():
        from flask import request
        user_id = request.sid
        session_id = request.sid
        _connection_manager.register_connection(user_id, session_id)
        emit('connection_response', {
            'connected': True,
            'online_users': get_connected_users()
        })
        broadcast_event('user_online', {'user_id': user_id})
        logger.info(f"Client {user_id} connected")
    
    @_socketio.on('disconnect')
    def handle_disconnect():
        from flask import request
        user_id = request.sid
        _connection_manager.unregister_connection(user_id, user_id)
        broadcast_event('user_offline', {'user_id': user_id})
        logger.info(f"Client {user_id} disconnected")
    
    @_socketio.on('join')
    def on_join(data):
        from flask import request
        room_id = data.get('room_id')
        user_id = request.sid
        
        if room_id:
            join_room(room_id)
            _connection_manager.join_room(user_id, room_id)
            emit('join_response', {
                'room': room_id,
                'members': _connection_manager.get_room_members(room_id)
            })
            broadcast_event('user_joined_room', {
                'user_id': user_id,
                'room_id': room_id
            }, room=room_id)
    
    @_socketio.on('leave')
    def on_leave(data):
        from flask import request
        room_id = data.get('room_id')
        user_id = request.sid
        
        if room_id:
            leave_room(room_id)
            _connection_manager.leave_room(user_id, room_id)
            broadcast_event('user_left_room', {
                'user_id': user_id,
                'room_id': room_id
            }, room=room_id)
    
    logger.info("✓ WebSocket system initialized")
    return socketio


def emit_event(user_id: str, event_type: str, data: Dict[str, Any]):
    """
    Emit event to specific user.
    
    Usage:
        emit_event('user123', 'issue_updated', {
            'issue_id': 42,
            'title': 'Updated Title'
        })
    """
    if not _socketio:
        logger.warning("WebSocket not initialized")
        return
    
    event = WebSocketEvent(event_type, data, user_id)
    _connection_manager.trigger_event_handlers(event)
    
    try:
        _socketio.emit(event_type, event.to_dict(), to=user_id)
        logger.debug(f"Event emitted to {user_id}: {event_type}")
    except Exception as e:
        logger.error(f"Failed to emit event: {e}")


def broadcast_event(event_type: str, data: Dict[str, Any], room: Optional[str] = None):
    """
    Broadcast event to all users or specific room.
    
    Usage:
        # Broadcast to all
        broadcast_event('notification', {'message': 'System update'})
        
        # Broadcast to room
        broadcast_event('issue_commented', {
            'issue_id': 42,
            'comment': 'New comment'
        }, room='issue_42')
    """
    if not _socketio:
        logger.warning("WebSocket not initialized")
        return
    
    event = WebSocketEvent(event_type, data)
    _connection_manager.trigger_event_handlers(event)
    
    try:
        _socketio.emit(event_type, event.to_dict(), to=room if room else None)
        logger.debug(f"Event broadcasted: {event_type}" + (f" to room {room}" if room else ""))
    except Exception as e:
        logger.error(f"Failed to broadcast event: {e}")


def get_connected_users() -> List[str]:
    """Get list of connected users."""
    if not _connection_manager:
        return []
    return _connection_manager.get_online_users()


def register_event_handler(event_type: str, handler: Callable):
    """Register custom event handler."""
    if _connection_manager:
        _connection_manager.register_event_handler(event_type, handler)


class WebSocketNamespace:
    """Base class for custom WebSocket namespaces."""
    
    def __init__(self, namespace: str):
        """Initialize namespace."""
        self.namespace = namespace
        self.events: Dict[str, Callable] = {}
    
    def on(self, event_name: str):
        """Decorator for event handler registration."""
        def decorator(func):
            self.events[event_name] = func
            return func
        return decorator
    
    def emit(self, event_name: str, data: Dict[str, Any], **kwargs):
        """Emit event in this namespace."""
        if _socketio:
            _socketio.emit(event_name, data, **kwargs, namespace=self.namespace)
    
    def broadcast(self, event_name: str, data: Dict[str, Any], **kwargs):
        """Broadcast event in this namespace."""
        if _socketio:
            _socketio.emit(event_name, data, skip_sid=request.sid, **kwargs, namespace=self.namespace)


# Example custom namespace for project collaboration
class ProjectNamespace(WebSocketNamespace):
    """Namespace for project-related real-time events."""
    
    def __init__(self):
        super().__init__('/projects')
    
    def init_handlers(self, socketio: SocketIO):
        """Initialize event handlers."""
        
        @socketio.on('project_update', namespace='/projects')
        def on_project_update(data):
            project_id = data.get('project_id')
            update = data.get('update')
            
            # Broadcast to all users in project
            broadcast_event('project_updated', {
                'project_id': project_id,
                'update': update
            }, room=f'project_{project_id}')
        
        @socketio.on('task_created', namespace='/projects')
        def on_task_created(data):
            project_id = data.get('project_id')
            task = data.get('task')
            
            broadcast_event('task_created', {
                'project_id': project_id,
                'task': task
            }, room=f'project_{project_id}')


class NotificationNamespace(WebSocketNamespace):
    """Namespace for real-time notifications."""
    
    def __init__(self):
        super().__init__('/notifications')
    
    def init_handlers(self, socketio: SocketIO):
        """Initialize event handlers."""
        
        @socketio.on('notification', namespace='/notifications')
        def on_notification(data):
            user_id = data.get('user_id')
            notification = data.get('notification')
            
            emit_event(user_id, 'notification_received', {
                'notification': notification,
                'timestamp': datetime.utcnow().isoformat()
            })
