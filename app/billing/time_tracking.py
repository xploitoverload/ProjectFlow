# app/billing/time_tracking.py
"""
Time Tracking and Billing System
Track time spent on projects/tasks, generate invoices, and manage billing.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum
import uuid


class TimeEntryStatus(Enum):
    """Time entry status."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    INVOICED = "invoiced"


class BillingStatus(Enum):
    """Invoice status."""
    DRAFT = "draft"
    ISSUED = "issued"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"


@dataclass
class TimeEntry:
    """Time tracking entry."""
    entry_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    project_id: str = ""
    task_id: str = ""
    date: datetime = field(default_factory=datetime.utcnow)
    hours: float = 0.0
    minutes: int = 0
    description: str = ""
    status: TimeEntryStatus = TimeEntryStatus.DRAFT
    hourly_rate: float = 0.0
    
    @property
    def total_time_minutes(self) -> int:
        return int(self.hours * 60) + self.minutes
    
    @property
    def cost(self) -> float:
        total_hours = self.hours + (self.minutes / 60)
        return total_hours * self.hourly_rate
    
    def to_dict(self) -> Dict:
        return {
            'entry_id': self.entry_id,
            'user_id': self.user_id,
            'project_id': self.project_id,
            'task_id': self.task_id,
            'date': self.date.isoformat(),
            'hours': round(self.hours, 2),
            'minutes': self.minutes,
            'description': self.description,
            'status': self.status.value,
            'cost': round(self.cost, 2)
        }


@dataclass
class BillingCycle:
    """Billing cycle."""
    cycle_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str = ""
    start_date: datetime = field(default_factory=datetime.utcnow)
    end_date: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(days=30))
    status: str = "open"  # open, closed, invoiced
    total_hours: float = 0.0
    total_cost: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            'cycle_id': self.cycle_id,
            'project_id': self.project_id,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'status': self.status,
            'total_hours': round(self.total_hours, 2),
            'total_cost': round(self.total_cost, 2)
        }


@dataclass
class BillingInvoice:
    """Billing invoice."""
    invoice_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str = ""
    client_id: str = ""
    cycle_id: str = ""
    amount: float = 0.0
    tax_amount: float = 0.0
    total_amount: float = 0.0
    status: BillingStatus = BillingStatus.DRAFT
    issued_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    paid_date: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        return {
            'invoice_id': self.invoice_id,
            'project_id': self.project_id,
            'amount': round(self.amount, 2),
            'tax_amount': round(self.tax_amount, 2),
            'total_amount': round(self.total_amount, 2),
            'status': self.status.value,
            'issued_date': self.issued_date.isoformat() if self.issued_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'paid_date': self.paid_date.isoformat() if self.paid_date else None
        }


@dataclass
class ExpenseReport:
    """Expense report."""
    report_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    project_id: str = ""
    submitted_date: datetime = field(default_factory=datetime.utcnow)
    status: str = "draft"  # draft, submitted, approved, reimbursed
    total_amount: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            'report_id': self.report_id,
            'user_id': self.user_id,
            'status': self.status,
            'total_amount': round(self.total_amount, 2),
            'submitted_date': self.submitted_date.isoformat()
        }


class TimeTrackingAndBillingManager:
    """
    Manages time tracking, billing cycles, and invoicing.
    """
    
    def __init__(self):
        """Initialize time tracking and billing manager."""
        self.time_entries: Dict[str, TimeEntry] = {}
        self.billing_cycles: Dict[str, BillingCycle] = {}
        self.invoices: Dict[str, BillingInvoice] = {}
        self.expense_reports: Dict[str, ExpenseReport] = {}
        self.stats = {
            'total_hours_tracked': 0.0,
            'total_invoiced': 0.0,
            'unpaid_invoices': 0,
            'overdue_invoices': 0
        }
    
    def create_time_entry(self, user_id: str, project_id: str, task_id: str,
                         hours: float, minutes: int = 0, description: str = "",
                         hourly_rate: float = 0.0) -> TimeEntry:
        """Create time entry."""
        entry = TimeEntry(
            user_id=user_id,
            project_id=project_id,
            task_id=task_id,
            hours=hours,
            minutes=minutes,
            description=description,
            hourly_rate=hourly_rate,
            status=TimeEntryStatus.DRAFT
        )
        
        self.time_entries[entry.entry_id] = entry
        self.stats['total_hours_tracked'] += hours + (minutes / 60)
        
        return entry
    
    def get_time_entry(self, entry_id: str) -> Optional[TimeEntry]:
        """Get time entry."""
        return self.time_entries.get(entry_id)
    
    def submit_time_entry(self, entry_id: str) -> bool:
        """Submit time entry for approval."""
        if entry_id not in self.time_entries:
            return False
        
        self.time_entries[entry_id].status = TimeEntryStatus.SUBMITTED
        return True
    
    def approve_time_entry(self, entry_id: str) -> bool:
        """Approve time entry."""
        if entry_id not in self.time_entries:
            return False
        
        self.time_entries[entry_id].status = TimeEntryStatus.APPROVED
        return True
    
    def get_user_time_entries(self, user_id: str, start_date: datetime = None,
                             end_date: datetime = None) -> List[Dict]:
        """Get time entries for user."""
        entries = [e for e in self.time_entries.values() if e.user_id == user_id]
        
        if start_date:
            entries = [e for e in entries if e.date >= start_date]
        if end_date:
            entries = [e for e in entries if e.date <= end_date]
        
        return [e.to_dict() for e in entries]
    
    def get_project_time_entries(self, project_id: str) -> List[Dict]:
        """Get time entries for project."""
        entries = [e for e in self.time_entries.values() if e.project_id == project_id
                  and e.status == TimeEntryStatus.APPROVED]
        
        return [e.to_dict() for e in entries]
    
    def create_billing_cycle(self, project_id: str, start_date: datetime,
                            end_date: datetime) -> BillingCycle:
        """Create billing cycle."""
        cycle = BillingCycle(
            project_id=project_id,
            start_date=start_date,
            end_date=end_date,
            status="open"
        )
        
        # Calculate totals from approved time entries
        entries = [e for e in self.time_entries.values() 
                  if e.project_id == project_id 
                  and start_date <= e.date <= end_date
                  and e.status == TimeEntryStatus.APPROVED]
        
        for entry in entries:
            cycle.total_hours += entry.hours + (entry.minutes / 60)
            cycle.total_cost += entry.cost
        
        self.billing_cycles[cycle.cycle_id] = cycle
        return cycle
    
    def create_invoice(self, project_id: str, client_id: str, cycle_id: str,
                      amount: float, tax_rate: float = 0.0) -> BillingInvoice:
        """Create invoice from billing cycle."""
        tax_amount = amount * (tax_rate / 100)
        total = amount + tax_amount
        
        invoice = BillingInvoice(
            project_id=project_id,
            client_id=client_id,
            cycle_id=cycle_id,
            amount=amount,
            tax_amount=tax_amount,
            total_amount=total,
            status=BillingStatus.DRAFT,
            due_date=datetime.utcnow() + timedelta(days=30)
        )
        
        self.invoices[invoice.invoice_id] = invoice
        self.stats['unpaid_invoices'] += 1
        
        return invoice
    
    def issue_invoice(self, invoice_id: str) -> bool:
        """Issue invoice."""
        if invoice_id not in self.invoices:
            return False
        
        invoice = self.invoices[invoice_id]
        invoice.status = BillingStatus.ISSUED
        invoice.issued_date = datetime.utcnow()
        
        return True
    
    def mark_invoice_paid(self, invoice_id: str) -> bool:
        """Mark invoice as paid."""
        if invoice_id not in self.invoices:
            return False
        
        invoice = self.invoices[invoice_id]
        invoice.status = BillingStatus.PAID
        invoice.paid_date = datetime.utcnow()
        
        self.stats['unpaid_invoices'] = max(0, self.stats['unpaid_invoices'] - 1)
        self.stats['total_invoiced'] += invoice.total_amount
        
        return True
    
    def get_billing_summary(self, project_id: str) -> Dict:
        """Get billing summary for project."""
        cycles = [c for c in self.billing_cycles.values() if c.project_id == project_id]
        invoices = [i for i in self.invoices.values() if i.project_id == project_id]
        
        return {
            'project_id': project_id,
            'total_hours': sum(c.total_hours for c in cycles),
            'total_cost': sum(c.total_cost for c in cycles),
            'total_invoices': len(invoices),
            'paid_invoices': len([i for i in invoices if i.status == BillingStatus.PAID]),
            'unpaid_invoices': len([i for i in invoices if i.status != BillingStatus.PAID])
        }
    
    def get_stats(self) -> Dict:
        """Get time tracking and billing statistics."""
        return {
            'total_hours_tracked': round(self.stats['total_hours_tracked'], 1),
            'total_invoiced': round(self.stats['total_invoiced'], 2),
            'unpaid_invoices': self.stats['unpaid_invoices'],
            'overdue_invoices': self.stats['overdue_invoices']
        }


# Global time tracking and billing manager
time_tracking_manager = TimeTrackingAndBillingManager()
