# app/portal/customer_portal.py
"""
Customer Portal System
White-label customer-facing portal with ticketing, knowledge base, and analytics.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
import uuid


class TicketStatus(Enum):
    """Ticket status."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING_CUSTOMER = "waiting_customer"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketPriority(Enum):
    """Ticket priority."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SupportTicket:
    """Customer support ticket."""
    ticket_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str = ""
    tenant_id: str = ""
    title: str = ""
    description: str = ""
    status: TicketStatus = TicketStatus.OPEN
    priority: TicketPriority = TicketPriority.MEDIUM
    category: str = ""
    assigned_to: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        return {
            'ticket_id': self.ticket_id,
            'title': self.title,
            'description': self.description,
            'status': self.status.value,
            'priority': self.priority.value,
            'category': self.category,
            'assigned_to': self.assigned_to,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }


@dataclass
class TicketComment:
    """Comment on support ticket."""
    comment_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    ticket_id: str = ""
    author_id: str = ""
    author_type: str = ""  # customer, support, system
    content: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        return {
            'comment_id': self.comment_id,
            'ticket_id': self.ticket_id,
            'author_type': self.author_type,
            'content': self.content,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class PortalBranding:
    """Customer portal branding customization."""
    tenant_id: str = ""
    logo_url: str = ""
    primary_color: str = "#007bff"
    secondary_color: str = "#6c757d"
    company_name: str = ""
    company_website: str = ""
    support_email: str = ""
    terms_url: str = ""
    privacy_url: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'logo_url': self.logo_url,
            'primary_color': self.primary_color,
            'secondary_color': self.secondary_color,
            'company_name': self.company_name,
            'support_email': self.support_email
        }


@dataclass
class PortalInvoice:
    """Customer invoice."""
    invoice_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str = ""
    customer_id: str = ""
    amount: float = 0.0
    currency: str = "USD"
    status: str = "unpaid"  # unpaid, paid, overdue
    issued_date: datetime = field(default_factory=datetime.utcnow)
    due_date: Optional[datetime] = None
    paid_date: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        return {
            'invoice_id': self.invoice_id,
            'amount': self.amount,
            'currency': self.currency,
            'status': self.status,
            'issued_date': self.issued_date.isoformat(),
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'paid_date': self.paid_date.isoformat() if self.paid_date else None
        }


class CustomerPortalManager:
    """
    Manages customer-facing portal.
    """
    
    def __init__(self):
        """Initialize customer portal manager."""
        self.tickets: Dict[str, SupportTicket] = {}
        self.comments: Dict[str, TicketComment] = {}
        self.branding: Dict[str, PortalBranding] = {}
        self.invoices: Dict[str, PortalInvoice] = {}
        self.ticket_comments: Dict[str, List[str]] = {}  # ticket_id -> comment_ids
        self.stats = {
            'total_tickets': 0,
            'open_tickets': 0,
            'resolved_tickets': 0,
            'avg_resolution_time': 0.0
        }
    
    def create_ticket(self, customer_id: str, tenant_id: str, title: str,
                     description: str, category: str = "general",
                     priority: str = "medium") -> SupportTicket:
        """Create support ticket."""
        try:
            priority_enum = TicketPriority[priority.upper()]
        except KeyError:
            priority_enum = TicketPriority.MEDIUM
        
        ticket = SupportTicket(
            customer_id=customer_id,
            tenant_id=tenant_id,
            title=title,
            description=description,
            category=category,
            priority=priority_enum,
            status=TicketStatus.OPEN
        )
        
        self.tickets[ticket.ticket_id] = ticket
        self.ticket_comments[ticket.ticket_id] = []
        
        self.stats['total_tickets'] += 1
        self.stats['open_tickets'] += 1
        
        return ticket
    
    def get_ticket(self, ticket_id: str) -> Optional[SupportTicket]:
        """Get ticket by ID."""
        return self.tickets.get(ticket_id)
    
    def get_customer_tickets(self, customer_id: str) -> List[Dict]:
        """Get all tickets for customer."""
        tickets = []
        
        for ticket in self.tickets.values():
            if ticket.customer_id == customer_id:
                tickets.append(ticket.to_dict())
        
        return tickets
    
    def add_comment(self, ticket_id: str, author_id: str, author_type: str,
                   content: str) -> Optional[TicketComment]:
        """Add comment to ticket."""
        if ticket_id not in self.tickets:
            return None
        
        comment = TicketComment(
            ticket_id=ticket_id,
            author_id=author_id,
            author_type=author_type,
            content=content
        )
        
        self.comments[comment.comment_id] = comment
        if ticket_id not in self.ticket_comments:
            self.ticket_comments[ticket_id] = []
        
        self.ticket_comments[ticket_id].append(comment.comment_id)
        
        # Update ticket timestamp
        self.tickets[ticket_id].updated_at = datetime.utcnow()
        
        return comment
    
    def get_ticket_comments(self, ticket_id: str) -> List[Dict]:
        """Get all comments on ticket."""
        if ticket_id not in self.ticket_comments:
            return []
        
        return [self.comments[cid].to_dict() for cid in self.ticket_comments[ticket_id]
               if cid in self.comments]
    
    def update_ticket_status(self, ticket_id: str, status: str) -> bool:
        """Update ticket status."""
        if ticket_id not in self.tickets:
            return False
        
        ticket = self.tickets[ticket_id]
        
        try:
            status_enum = TicketStatus[status.upper()]
        except KeyError:
            return False
        
        old_status = ticket.status
        ticket.status = status_enum
        ticket.updated_at = datetime.utcnow()
        
        # Update resolved/closed tracking
        if status_enum in [TicketStatus.RESOLVED, TicketStatus.CLOSED]:
            if old_status == TicketStatus.OPEN:
                self.stats['open_tickets'] = max(0, self.stats['open_tickets'] - 1)
            ticket.resolved_at = datetime.utcnow()
            self.stats['resolved_tickets'] += 1
        
        return True
    
    def set_portal_branding(self, tenant_id: str, branding_data: Dict) -> PortalBranding:
        """Set portal branding for tenant."""
        branding = PortalBranding(
            tenant_id=tenant_id,
            logo_url=branding_data.get('logo_url', ''),
            primary_color=branding_data.get('primary_color', '#007bff'),
            secondary_color=branding_data.get('secondary_color', '#6c757d'),
            company_name=branding_data.get('company_name', ''),
            company_website=branding_data.get('company_website', ''),
            support_email=branding_data.get('support_email', ''),
            terms_url=branding_data.get('terms_url', ''),
            privacy_url=branding_data.get('privacy_url', '')
        )
        
        self.branding[tenant_id] = branding
        return branding
    
    def get_portal_branding(self, tenant_id: str) -> Optional[Dict]:
        """Get portal branding for tenant."""
        if tenant_id not in self.branding:
            return None
        
        return self.branding[tenant_id].to_dict()
    
    def create_invoice(self, tenant_id: str, customer_id: str, amount: float,
                      currency: str = "USD") -> PortalInvoice:
        """Create invoice."""
        from datetime import timedelta
        
        invoice = PortalInvoice(
            tenant_id=tenant_id,
            customer_id=customer_id,
            amount=amount,
            currency=currency,
            status="unpaid",
            due_date=datetime.utcnow() + timedelta(days=30)
        )
        
        self.invoices[invoice.invoice_id] = invoice
        return invoice
    
    def get_customer_invoices(self, customer_id: str) -> List[Dict]:
        """Get invoices for customer."""
        invoices = []
        
        for invoice in self.invoices.values():
            if invoice.customer_id == customer_id:
                invoices.append(invoice.to_dict())
        
        return invoices
    
    def mark_invoice_paid(self, invoice_id: str) -> bool:
        """Mark invoice as paid."""
        if invoice_id not in self.invoices:
            return False
        
        invoice = self.invoices[invoice_id]
        invoice.status = "paid"
        invoice.paid_date = datetime.utcnow()
        
        return True
    
    def get_portal_analytics(self, tenant_id: str) -> Dict:
        """Get analytics for portal."""
        tenant_tickets = [t for t in self.tickets.values() if t.tenant_id == tenant_id]
        
        return {
            'total_tickets': len(tenant_tickets),
            'open_tickets': len([t for t in tenant_tickets if t.status == TicketStatus.OPEN]),
            'resolved_tickets': len([t for t in tenant_tickets if t.status in [TicketStatus.RESOLVED, TicketStatus.CLOSED]]),
            'avg_priority': 'medium'  # Simplified
        }
    
    def get_stats(self) -> Dict:
        """Get portal statistics."""
        return {
            'total_tickets': self.stats['total_tickets'],
            'open_tickets': self.stats['open_tickets'],
            'resolved_tickets': self.stats['resolved_tickets'],
            'avg_resolution_time_hours': round(self.stats['avg_resolution_time'], 1)
        }


# Global customer portal manager
customer_portal_manager = CustomerPortalManager()
