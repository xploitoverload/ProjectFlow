"""
WebSocket integration for real-time features.
"""

from .realtime import (
    init_websocket,
    emit_event,
    broadcast_event,
    get_connected_users,
)

__all__ = [
    'init_websocket',
    'emit_event',
    'broadcast_event',
    'get_connected_users',
]
