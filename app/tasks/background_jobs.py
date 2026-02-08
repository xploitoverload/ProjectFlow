# app/tasks/background_jobs.py
"""
Background jobs for async tasks.
Provides job scheduling, email notifications, and report generation.
Uses in-memory queue for demo (production: use Celery + Redis).
"""

import threading
import queue
import time
import logging
from datetime import datetime
from typing import Callable, Any, Dict
from functools import wraps

logger = logging.getLogger('tasks')


class JobQueue:
    """Thread-safe job queue for background tasks."""
    
    def __init__(self, max_workers: int = 4):
        """
        Initialize job queue.
        
        Args:
            max_workers: Number of worker threads
        """
        self.queue = queue.Queue(maxsize=1000)
        self.max_workers = max_workers
        self.workers = []
        self.running = False
        self.stats = {
            'total_jobs': 0,
            'completed_jobs': 0,
            'failed_jobs': 0,
            'active_jobs': 0
        }
    
    def start(self):
        """Start worker threads."""
        if self.running:
            return
        
        self.running = True
        logger.info(f"Starting job queue with {self.max_workers} workers")
        
        for i in range(self.max_workers):
            worker = threading.Thread(
                target=self._worker_loop,
                name=f"JobWorker-{i}",
                daemon=True
            )
            worker.start()
            self.workers.append(worker)
    
    def stop(self):
        """Stop worker threads."""
        self.running = False
        logger.info("Stopping job queue")
        
        # Wait for queue to empty
        self.queue.join()
    
    def _worker_loop(self):
        """Worker thread main loop."""
        while self.running:
            try:
                # Get job with timeout to allow checking running flag
                job = self.queue.get(timeout=1)
            except queue.Empty:
                continue
            
            try:
                self.stats['active_jobs'] += 1
                self._execute_job(job)
                self.stats['completed_jobs'] += 1
            except Exception as e:
                logger.error(f"Job failed: {str(e)}", exc_info=True)
                self.stats['failed_jobs'] += 1
            finally:
                self.stats['active_jobs'] -= 1
                self.queue.task_done()
    
    def _execute_job(self, job: Dict[str, Any]):
        """Execute a single job."""
        job_id = job['id']
        func = job['func']
        args = job.get('args', ())
        kwargs = job.get('kwargs', {})
        
        logger.debug(f"Executing job {job_id}: {func.__name__}")
        
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start_time
        
        logger.debug(f"Job {job_id} completed in {elapsed:.2f}s")
        
        # Call result callback if provided
        if 'callback' in job and job['callback']:
            job['callback'](result)
    
    def enqueue(self, func: Callable, *args, callback: Callable = None, **kwargs) -> str:
        """
        Enqueue a job.
        
        Args:
            func: Function to execute
            *args: Positional arguments
            callback: Optional callback on completion
            **kwargs: Keyword arguments
        
        Returns:
            Job ID
        """
        job_id = f"job_{time.time()}_{self.stats['total_jobs']}"
        
        job = {
            'id': job_id,
            'func': func,
            'args': args,
            'kwargs': kwargs,
            'callback': callback,
            'created_at': datetime.now(),
            'status': 'queued'
        }
        
        self.queue.put(job)
        self.stats['total_jobs'] += 1
        
        logger.debug(f"Enqueued job {job_id}: {func.__name__}")
        
        return job_id
    
    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        return {
            **self.stats,
            'queue_size': self.queue.qsize(),
            'workers': self.max_workers,
            'running': self.running
        }


def async_task(func: Callable) -> Callable:
    """
    Decorator to run function as background task.
    
    Usage:
        @async_task
        def send_email(user_id, subject):
            # Task implementation
            pass
        
        # Call and execute in background
        send_email.delay(user_id=123, subject="Hello")
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Synchronous call (for testing)
        return func(*args, **kwargs)
    
    def delay(*args, **kwargs):
        # Async call
        if hasattr(async_task, '_queue') and async_task._queue:
            return async_task._queue.enqueue(func, *args, **kwargs)
        else:
            logger.warning(f"Job queue not initialized, executing {func.__name__} synchronously")
            return func(*args, **kwargs)
    
    wrapper.delay = delay
    return wrapper


# Global job queue instance
_queue_instance: JobQueue = None


def init_tasks(app):
    """Initialize background job system."""
    global _queue_instance
    
    max_workers = app.config.get('JOB_QUEUE_WORKERS', 4)
    _queue_instance = JobQueue(max_workers=max_workers)
    _queue_instance.start()
    
    # Store on app for access
    app.job_queue = _queue_instance
    
    # Store reference for decorator
    async_task._queue = _queue_instance
    
    logger.info(f"✓ Background job queue initialized with {max_workers} workers")
    
    return _queue_instance


def get_job_queue() -> JobQueue:
    """Get global job queue instance."""
    return _queue_instance


# Pre-built async tasks
@async_task
def send_email_async(to_email: str, subject: str, body: str):
    """Send email asynchronously."""
    logger.info(f"Sending email to {to_email}: {subject}")
    # Implementation would use Flask-Mail
    time.sleep(0.5)  # Simulate email sending
    return f"Email sent to {to_email}"


@async_task
def generate_report_async(project_id: int, report_type: str = 'summary'):
    """Generate project report asynchronously."""
    logger.info(f"Generating {report_type} report for project {project_id}")
    # Implementation would generate actual report
    time.sleep(1)  # Simulate report generation
    return f"Report generated for project {project_id}"


@async_task
def cleanup_old_data_async(days: int = 30):
    """Cleanup old data asynchronously."""
    logger.info(f"Cleaning up data older than {days} days")
    # Implementation would delete old data
    time.sleep(0.5)
    return f"Cleanup complete"


@async_task
def send_notification_async(user_id: int, message: str, notification_type: str = 'info'):
    """Send user notification asynchronously."""
    logger.info(f"Sending {notification_type} notification to user {user_id}: {message}")
    # Implementation would store notification
    return f"Notification sent to user {user_id}"


# Job status tracker
class JobStatus:
    """Track job execution status."""
    
    QUEUED = 'queued'
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'
    
    @staticmethod
    def get_status(job_id: str) -> str:
        """Get job status."""
        # In production, would query persistent store
        return JobStatus.QUEUED
    
    @staticmethod
    def get_result(job_id: str) -> Any:
        """Get job result."""
        # In production, would query persistent store
        return None
