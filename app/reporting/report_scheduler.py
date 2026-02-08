"""Report scheduling and delivery."""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class ScheduleFrequency(Enum):
    """Schedule frequency."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


class DeliveryMethod(Enum):
    """Delivery methods."""
    EMAIL = "email"
    SLACK = "slack"
    TEAMS = "teams"
    DASHBOARD = "dashboard"


@dataclass
class Schedule:
    """Report schedule."""
    id: str
    report_config_id: str
    frequency: ScheduleFrequency
    day_of_week: Optional[int] = None  # 0=Monday, 6=Sunday
    day_of_month: Optional[int] = None
    hour: int = 9
    minute: int = 0
    enabled: bool = True
    next_run: str = None
    last_run: Optional[str] = None
    delivery_methods: List[DeliveryMethod] = None
    recipients: List[str] = None
    
    def __post_init__(self):
        if self.delivery_methods is None:
            self.delivery_methods = [DeliveryMethod.EMAIL]
        if self.recipients is None:
            self.recipients = []


class ReportScheduler:
    """Report scheduling and delivery."""
    
    def __init__(self):
        """Initialize report scheduler."""
        self.schedules: Dict[str, Schedule] = {}
        self.delivery_log: List[Dict] = []
    
    def create_schedule(self, report_config_id: str, frequency: ScheduleFrequency,
                       hour: int = 9, minute: int = 0,
                       delivery_methods: List[DeliveryMethod] = None,
                       recipients: List[str] = None,
                       day_of_week: int = None,
                       day_of_month: int = None) -> Schedule:
        """
        Create a report schedule.
        
        Args:
            report_config_id: Report configuration ID
            frequency: Schedule frequency
            hour: Hour to run (0-23)
            minute: Minute to run (0-59)
            delivery_methods: Methods to deliver report
            recipients: List of recipient emails
            day_of_week: Day for weekly (0=Monday)
            day_of_month: Day for monthly (1-31)
            
        Returns:
            Schedule instance
        """
        schedule_id = f"sched_{int(datetime.now().timestamp() * 1000)}"
        
        schedule = Schedule(
            id=schedule_id,
            report_config_id=report_config_id,
            frequency=frequency,
            day_of_week=day_of_week,
            day_of_month=day_of_month,
            hour=hour,
            minute=minute,
            delivery_methods=delivery_methods or [DeliveryMethod.EMAIL],
            recipients=recipients or []
        )
        
        # Calculate next run
        schedule.next_run = self._calculate_next_run(schedule).isoformat()
        
        self.schedules[schedule_id] = schedule
        logger.info(f"Schedule created: {schedule_id}")
        
        return schedule
    
    def _calculate_next_run(self, schedule: Schedule) -> datetime:
        """Calculate next run time."""
        now = datetime.now()
        
        if schedule.frequency == ScheduleFrequency.DAILY:
            next_run = now.replace(hour=schedule.hour, minute=schedule.minute, second=0)
            if next_run <= now:
                next_run += timedelta(days=1)
        
        elif schedule.frequency == ScheduleFrequency.WEEKLY:
            next_run = now.replace(hour=schedule.hour, minute=schedule.minute, second=0)
            days_ahead = (schedule.day_of_week or 0) - now.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            next_run += timedelta(days=days_ahead)
        
        elif schedule.frequency == ScheduleFrequency.MONTHLY:
            day = schedule.day_of_month or 1
            next_run = now.replace(day=day, hour=schedule.hour, minute=schedule.minute, second=0)
            if next_run <= now:
                # Move to next month
                if next_run.month == 12:
                    next_run = next_run.replace(year=next_run.year + 1, month=1)
                else:
                    next_run = next_run.replace(month=next_run.month + 1)
        
        elif schedule.frequency == ScheduleFrequency.QUARTERLY:
            current_quarter = (now.month - 1) // 3
            next_quarter_month = (current_quarter + 1) * 3 + 1
            next_run = now.replace(month=next_quarter_month, day=1, 
                                  hour=schedule.hour, minute=schedule.minute, second=0)
        
        else:
            next_run = now + timedelta(days=1)
        
        return next_run
    
    def get_due_schedules(self) -> List[Schedule]:
        """
        Get schedules due to run.
        
        Returns:
            List of due schedules
        """
        now = datetime.now()
        due = []
        
        for schedule in self.schedules.values():
            if not schedule.enabled:
                continue
            
            next_run = datetime.fromisoformat(schedule.next_run)
            if next_run <= now:
                due.append(schedule)
        
        return due
    
    def mark_as_executed(self, schedule_id: str) -> None:
        """
        Mark schedule as executed.
        
        Args:
            schedule_id: Schedule ID
        """
        if schedule_id in self.schedules:
            schedule = self.schedules[schedule_id]
            schedule.last_run = datetime.now().isoformat()
            schedule.next_run = self._calculate_next_run(schedule).isoformat()
            logger.info(f"Schedule executed: {schedule_id}")
    
    def deliver_report(self, schedule_id: str, report_data: Dict) -> Dict:
        """
        Deliver a report via configured methods.
        
        Args:
            schedule_id: Schedule ID
            report_data: Report data to deliver
            
        Returns:
            Delivery result
        """
        if schedule_id not in self.schedules:
            return {'status': 'error', 'message': 'Schedule not found'}
        
        schedule = self.schedules[schedule_id]
        results = {}
        
        for method in schedule.delivery_methods:
            result = self._deliver_by_method(method, report_data, schedule.recipients)
            results[method.value] = result
        
        delivery_log = {
            'schedule_id': schedule_id,
            'timestamp': datetime.now().isoformat(),
            'report_id': report_data.get('id'),
            'methods': results,
            'recipients': len(schedule.recipients)
        }
        
        self.delivery_log.append(delivery_log)
        logger.info(f"Report delivered: {schedule_id}")
        
        return {'status': 'success', 'results': results}
    
    def _deliver_by_method(self, method: DeliveryMethod, report_data: Dict,
                          recipients: List[str]) -> Dict:
        """Deliver report via specific method."""
        if method == DeliveryMethod.EMAIL:
            return {
                'status': 'queued',
                'method': 'email',
                'recipients': recipients
            }
        elif method == DeliveryMethod.SLACK:
            return {
                'status': 'queued',
                'method': 'slack',
                'channels': recipients
            }
        elif method == DeliveryMethod.TEAMS:
            return {
                'status': 'queued',
                'method': 'teams',
                'channels': recipients
            }
        else:
            return {'status': 'success', 'method': 'dashboard'}
    
    def enable_schedule(self, schedule_id: str) -> bool:
        """Enable a schedule."""
        if schedule_id in self.schedules:
            self.schedules[schedule_id].enabled = True
            return True
        return False
    
    def disable_schedule(self, schedule_id: str) -> bool:
        """Disable a schedule."""
        if schedule_id in self.schedules:
            self.schedules[schedule_id].enabled = False
            return True
        return False
    
    def delete_schedule(self, schedule_id: str) -> bool:
        """Delete a schedule."""
        if schedule_id in self.schedules:
            del self.schedules[schedule_id]
            return True
        return False
    
    def get_stats(self) -> Dict:
        """Get scheduler statistics."""
        return {
            'total_schedules': len(self.schedules),
            'enabled_schedules': sum(1 for s in self.schedules.values() if s.enabled),
            'deliveries': len(self.delivery_log),
            'delivery_methods': [m.value for m in DeliveryMethod]
        }
