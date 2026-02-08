# app/testing/qa_module.py
"""
QA & Testing Module
Test case management, execution tracking, and coverage reporting.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional
from datetime import datetime


class TestStatus(Enum):
    """Test status."""
    DRAFT = "draft"
    READY = "ready"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    BLOCKED = "blocked"


class TestType(Enum):
    """Test types."""
    UNIT = "unit"
    INTEGRATION = "integration"
    FUNCTIONAL = "functional"
    PERFORMANCE = "performance"
    SECURITY = "security"
    REGRESSION = "regression"


class SeverityLevel(Enum):
    """Bug severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    TRIVIAL = "trivial"


@dataclass
class TestCase:
    """Test case."""
    id: str
    name: str
    description: str = ""
    test_type: TestType = TestType.FUNCTIONAL
    status: TestStatus = TestStatus.DRAFT
    steps: List[str] = field(default_factory=list)
    expected_results: str = ""
    actual_results: str = ""
    preconditions: str = ""
    postconditions: str = ""
    estimated_duration_minutes: int = 10
    author: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'test_type': self.test_type.value,
            'status': self.status.value,
            'steps': self.steps,
            'expected_results': self.expected_results,
            'actual_results': self.actual_results,
            'preconditions': self.preconditions,
            'postconditions': self.postconditions,
            'estimated_duration_minutes': self.estimated_duration_minutes,
            'author': self.author,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


@dataclass
class TestExecution:
    """Test execution record."""
    id: str
    test_case_id: str
    status: TestStatus
    executed_by: str
    execution_environment: str = ""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: int = 0
    notes: str = ""
    attachments: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'test_case_id': self.test_case_id,
            'status': self.status.value,
            'executed_by': self.executed_by,
            'execution_environment': self.execution_environment,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': self.duration_seconds,
            'notes': self.notes,
            'attachments': self.attachments,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class BugReport:
    """Bug report."""
    id: str
    title: str
    description: str = ""
    test_case_id: str = ""
    severity: SeverityLevel = SeverityLevel.MEDIUM
    status: str = "open"  # open, assigned, in_progress, resolved, closed
    assigned_to: str = ""
    reported_by: str = ""
    reproduction_steps: str = ""
    attachments: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'test_case_id': self.test_case_id,
            'severity': self.severity.value,
            'status': self.status,
            'assigned_to': self.assigned_to,
            'reported_by': self.reported_by,
            'reproduction_steps': self.reproduction_steps,
            'attachments': self.attachments,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


@dataclass
class TestSuite:
    """Test suite grouping."""
    id: str
    name: str
    description: str = ""
    test_case_ids: List[str] = field(default_factory=list)
    automation_script: str = ""
    is_automated: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'test_case_ids': self.test_case_ids,
            'total_tests': len(self.test_case_ids),
            'automation_script': self.automation_script,
            'is_automated': self.is_automated,
            'created_at': self.created_at.isoformat()
        }


class QAAndTestingManager:
    """Manage QA and testing operations."""
    
    def __init__(self):
        self.test_cases: Dict[str, TestCase] = {}
        self.executions: Dict[str, TestExecution] = {}
        self.bugs: Dict[str, BugReport] = {}
        self.suites: Dict[str, TestSuite] = {}
        self.case_counter = 0
        self.exec_counter = 0
        self.bug_counter = 0
    
    def create_test_case(self, name: str, description: str = "", 
                        test_type: str = "functional"):
        """Create test case."""
        self.case_counter += 1
        case_id = f"tc_{self.case_counter}"
        
        test_case = TestCase(case_id, name, description, TestType(test_type))
        self.test_cases[case_id] = test_case
        return test_case
    
    def get_test_case(self, case_id: str):
        """Get test case."""
        return self.test_cases.get(case_id)
    
    def add_test_steps(self, case_id: str, steps: List[str]):
        """Add test steps."""
        case = self.test_cases.get(case_id)
        if not case:
            return False
        
        case.steps = steps
        case.status = TestStatus.READY
        return True
    
    def execute_test(self, case_id: str, executed_by: str):
        """Execute test case."""
        case = self.test_cases.get(case_id)
        if not case:
            return None
        
        self.exec_counter += 1
        exec_id = f"exec_{self.exec_counter}"
        
        execution = TestExecution(exec_id, case_id, TestStatus.RUNNING, executed_by)
        execution.start_time = datetime.utcnow()
        self.executions[exec_id] = execution
        return execution
    
    def complete_execution(self, exec_id: str, status: str, notes: str = ""):
        """Complete test execution."""
        execution = self.executions.get(exec_id)
        if not execution:
            return False
        
        execution.status = TestStatus(status)
        execution.end_time = datetime.utcnow()
        execution.notes = notes
        
        if execution.start_time and execution.end_time:
            execution.duration_seconds = int((execution.end_time - execution.start_time).total_seconds())
        
        return True
    
    def create_bug(self, title: str, description: str = "", 
                  severity: str = "medium", reported_by: str = ""):
        """Create bug report."""
        self.bug_counter += 1
        bug_id = f"bug_{self.bug_counter}"
        
        bug = BugReport(bug_id, title, description, severity=SeverityLevel(severity), 
                       reported_by=reported_by)
        self.bugs[bug_id] = bug
        return bug
    
    def get_bug(self, bug_id: str):
        """Get bug report."""
        return self.bugs.get(bug_id)
    
    def assign_bug(self, bug_id: str, assigned_to: str):
        """Assign bug to developer."""
        bug = self.bugs.get(bug_id)
        if not bug:
            return False
        
        bug.assigned_to = assigned_to
        bug.status = "assigned"
        return True
    
    def close_bug(self, bug_id: str):
        """Close bug."""
        bug = self.bugs.get(bug_id)
        if not bug:
            return False
        
        bug.status = "closed"
        bug.updated_at = datetime.utcnow()
        return True
    
    def create_test_suite(self, name: str, description: str = ""):
        """Create test suite."""
        suite_id = f"suite_{len(self.suites) + 1}"
        suite = TestSuite(suite_id, name, description)
        self.suites[suite_id] = suite
        return suite
    
    def add_test_to_suite(self, suite_id: str, test_case_id: str):
        """Add test to suite."""
        suite = self.suites.get(suite_id)
        if not suite:
            return False
        
        suite.test_case_ids.append(test_case_id)
        return True
    
    def get_test_coverage(self):
        """Get test coverage metrics."""
        total_cases = len(self.test_cases)
        executed = len([e for e in self.executions.values()])
        passed = len([e for e in self.executions.values() if e.status == TestStatus.PASSED])
        failed = len([e for e in self.executions.values() if e.status == TestStatus.FAILED])
        
        return {
            'total_test_cases': total_cases,
            'total_executions': executed,
            'passed': passed,
            'failed': failed,
            'pass_rate': (passed / executed * 100) if executed > 0 else 0,
            'coverage_percent': (executed / total_cases * 100) if total_cases > 0 else 0
        }
    
    def get_bug_metrics(self):
        """Get bug metrics."""
        critical = len([b for b in self.bugs.values() if b.severity == SeverityLevel.CRITICAL])
        high = len([b for b in self.bugs.values() if b.severity == SeverityLevel.HIGH])
        open_bugs = len([b for b in self.bugs.values() if b.status == "open"])
        closed_bugs = len([b for b in self.bugs.values() if b.status == "closed"])
        
        return {
            'total_bugs': len(self.bugs),
            'critical_bugs': critical,
            'high_priority_bugs': high,
            'open_bugs': open_bugs,
            'closed_bugs': closed_bugs,
            'resolution_rate': (closed_bugs / len(self.bugs) * 100) if len(self.bugs) > 0 else 0
        }


# Global instance
qa_manager = QAAndTestingManager()
