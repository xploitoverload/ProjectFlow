# app/tasks/__init__.py
"""
Background task system.
"""

from .background_jobs import (
    JobQueue,
    async_task,
    init_tasks,
    get_job_queue,
    send_email_async,
    generate_report_async,
    cleanup_old_data_async,
    send_notification_async,
    JobStatus
)

__all__ = [
    'JobQueue',
    'async_task',
    'init_tasks',
    'get_job_queue',
    'send_email_async',
    'generate_report_async',
    'cleanup_old_data_async',
    'send_notification_async',
    'JobStatus'
]
