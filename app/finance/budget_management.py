# app/finance/budget_management.py
"""
Finance and Budget Management
Budget planning, expense tracking, cost analysis, and financial reporting.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
import uuid


class BudgetStatus(Enum):
    """Budget status."""
    PLANNING = "planning"
    APPROVED = "approved"
    ACTIVE = "active"
    CLOSED = "closed"


class ExpenseCategory(Enum):
    """Expense categories."""
    PERSONNEL = "personnel"
    EQUIPMENT = "equipment"
    TOOLS = "tools"
    TRAVEL = "travel"
    OPERATIONS = "operations"
    MARKETING = "marketing"
    OTHER = "other"


@dataclass
class Budget:
    """Project or organizational budget."""
    budget_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    project_id: str = ""
    fiscal_year: int = datetime.utcnow().year
    total_allocation: float = 0.0
    allocated: float = 0.0
    spent: float = 0.0
    status: BudgetStatus = BudgetStatus.PLANNING
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def remaining(self) -> float:
        return self.total_allocation - self.spent
    
    @property
    def utilization_percent(self) -> float:
        return (self.spent / self.total_allocation * 100) if self.total_allocation > 0 else 0
    
    def to_dict(self) -> Dict:
        return {
            'budget_id': self.budget_id,
            'name': self.name,
            'project_id': self.project_id,
            'fiscal_year': self.fiscal_year,
            'total_allocation': round(self.total_allocation, 2),
            'spent': round(self.spent, 2),
            'remaining': round(self.remaining, 2),
            'utilization_percent': round(self.utilization_percent, 1),
            'status': self.status.value
        }


@dataclass
class BudgetLine:
    """Budget line item."""
    line_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    budget_id: str = ""
    category: ExpenseCategory = ExpenseCategory.OTHER
    description: str = ""
    allocated_amount: float = 0.0
    spent_amount: float = 0.0
    
    @property
    def remaining(self) -> float:
        return self.allocated_amount - self.spent_amount
    
    def to_dict(self) -> Dict:
        return {
            'line_id': self.line_id,
            'category': self.category.value,
            'description': self.description,
            'allocated': round(self.allocated_amount, 2),
            'spent': round(self.spent_amount, 2),
            'remaining': round(self.remaining, 2)
        }


@dataclass
class FinancialReport:
    """Financial report."""
    report_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    report_type: str = ""  # monthly, quarterly, annual
    period_start: datetime = field(default_factory=datetime.utcnow)
    period_end: datetime = field(default_factory=datetime.utcnow)
    total_revenue: float = 0.0
    total_expenses: float = 0.0
    profit_loss: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            'report_id': self.report_id,
            'report_type': self.report_type,
            'period_start': self.period_start.isoformat(),
            'period_end': self.period_end.isoformat(),
            'total_revenue': round(self.total_revenue, 2),
            'total_expenses': round(self.total_expenses, 2),
            'profit_loss': round(self.profit_loss, 2)
        }


class FinanceAndBudgetManager:
    """
    Manages budgets, expenses, and financial reporting.
    """
    
    def __init__(self):
        """Initialize finance manager."""
        self.budgets: Dict[str, Budget] = {}
        self.budget_lines: Dict[str, BudgetLine] = {}
        self.budget_items: Dict[str, List[str]] = {}  # budget_id -> line_ids
        self.financial_reports: Dict[str, FinancialReport] = {}
        self.stats = {
            'total_budgets': 0,
            'total_allocation': 0.0,
            'total_spent': 0.0,
            'active_budgets': 0
        }
    
    def create_budget(self, name: str, project_id: str, total_allocation: float,
                     fiscal_year: int = None) -> Budget:
        """Create budget."""
        budget = Budget(
            name=name,
            project_id=project_id,
            total_allocation=total_allocation,
            fiscal_year=fiscal_year or datetime.utcnow().year,
            status=BudgetStatus.PLANNING
        )
        
        self.budgets[budget.budget_id] = budget
        self.budget_items[budget.budget_id] = []
        
        self.stats['total_budgets'] += 1
        self.stats['total_allocation'] += total_allocation
        
        return budget
    
    def get_budget(self, budget_id: str) -> Optional[Budget]:
        """Get budget."""
        return self.budgets.get(budget_id)
    
    def add_budget_line(self, budget_id: str, category: str, description: str,
                       allocated_amount: float) -> Optional[BudgetLine]:
        """Add budget line item."""
        if budget_id not in self.budgets:
            return None
        
        try:
            cat_enum = ExpenseCategory[category.upper()]
        except KeyError:
            cat_enum = ExpenseCategory.OTHER
        
        line = BudgetLine(
            budget_id=budget_id,
            category=cat_enum,
            description=description,
            allocated_amount=allocated_amount
        )
        
        self.budget_lines[line.line_id] = line
        self.budget_items[budget_id].append(line.line_id)
        
        # Update budget allocated
        budget = self.budgets[budget_id]
        budget.allocated += allocated_amount
        
        return line
    
    def get_budget_lines(self, budget_id: str) -> List[Dict]:
        """Get budget line items."""
        if budget_id not in self.budget_items:
            return []
        
        return [self.budget_lines[lid].to_dict() for lid in self.budget_items[budget_id]
               if lid in self.budget_lines]
    
    def record_expense(self, budget_id: str, line_id: str, amount: float) -> bool:
        """Record expense against budget line."""
        if budget_id not in self.budgets or line_id not in self.budget_lines:
            return False
        
        budget = self.budgets[budget_id]
        line = self.budget_lines[line_id]
        
        # Check if within limit
        if line.spent_amount + amount > line.allocated_amount:
            return False
        
        line.spent_amount += amount
        budget.spent += amount
        self.stats['total_spent'] += amount
        
        return True
    
    def approve_budget(self, budget_id: str) -> bool:
        """Approve budget."""
        if budget_id not in self.budgets:
            return False
        
        budget = self.budgets[budget_id]
        budget.status = BudgetStatus.APPROVED
        self.stats['active_budgets'] += 1
        
        return True
    
    def activate_budget(self, budget_id: str) -> bool:
        """Activate budget."""
        if budget_id not in self.budgets:
            return False
        
        budget = self.budgets[budget_id]
        if budget.status != BudgetStatus.APPROVED:
            return False
        
        budget.status = BudgetStatus.ACTIVE
        return True
    
    def close_budget(self, budget_id: str) -> bool:
        """Close budget."""
        if budget_id not in self.budgets:
            return False
        
        budget = self.budgets[budget_id]
        budget.status = BudgetStatus.CLOSED
        self.stats['active_budgets'] = max(0, self.stats['active_budgets'] - 1)
        
        return True
    
    def get_budget_status(self, budget_id: str) -> Dict:
        """Get budget status and analysis."""
        if budget_id not in self.budgets:
            return {'error': 'Budget not found'}
        
        budget = self.budgets[budget_id]
        lines = self.get_budget_lines(budget_id)
        
        at_risk = sum(1 for l in lines if l['spent'] > l['allocated'] * 0.8)
        
        return {
            'budget_id': budget_id,
            'status': budget.status.value,
            'total_allocation': round(budget.total_allocation, 2),
            'total_spent': round(budget.spent, 2),
            'remaining': round(budget.remaining, 2),
            'utilization_percent': round(budget.utilization_percent, 1),
            'lines_at_risk': at_risk
        }
    
    def generate_financial_report(self, report_type: str = 'monthly') -> FinancialReport:
        """Generate financial report."""
        report = FinancialReport(
            report_type=report_type,
            total_revenue=0.0,  # Would be calculated from actual data
            total_expenses=self.stats['total_spent'],
            profit_loss=0.0
        )
        
        self.financial_reports[report.report_id] = report
        return report
    
    def get_stats(self) -> Dict:
        """Get finance statistics."""
        return {
            'total_budgets': self.stats['total_budgets'],
            'active_budgets': self.stats['active_budgets'],
            'total_allocation': round(self.stats['total_allocation'], 2),
            'total_spent': round(self.stats['total_spent'], 2),
            'remaining': round(self.stats['total_allocation'] - self.stats['total_spent'], 2),
            'utilization_percent': round(
                (self.stats['total_spent'] / self.stats['total_allocation'] * 100)
                if self.stats['total_allocation'] > 0 else 0, 1
            )
        }


# Global finance and budget manager
finance_manager = FinanceAndBudgetManager()
