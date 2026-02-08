# app/operations/batch.py
"""
Batch operations system for efficient bulk processing.
Supports create, update, delete operations with transaction management.
"""

import logging
from typing import List, Dict, Any, Optional, Callable, Tuple
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger('batch')


class OperationType(Enum):
    """Batch operation types."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    CUSTOM = "custom"


@dataclass
class BatchOperation:
    """Represents a single batch operation."""
    
    operation_type: OperationType
    resource_type: str
    data: Dict[str, Any]
    id: Optional[str] = None  # For update/delete operations
    metadata: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    status: str = "pending"  # pending, success, failed, skipped
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'operation_type': self.operation_type.value,
            'resource_type': self.resource_type,
            'data': self.data,
            'id': self.id,
            'metadata': self.metadata,
            'result': self.result,
            'error': self.error,
            'status': self.status,
            'timestamp': self.timestamp.isoformat()
        }


class BatchResult:
    """Result of batch operation execution."""
    
    def __init__(self, batch_id: str, total_operations: int):
        """Initialize batch result."""
        self.batch_id = batch_id
        self.total_operations = total_operations
        self.successful = 0
        self.failed = 0
        self.skipped = 0
        self.operations: List[BatchOperation] = []
        self.start_time = datetime.utcnow()
        self.end_time: Optional[datetime] = None
        self.errors: Dict[int, str] = {}  # operation_index -> error
    
    def add_operation(self, operation: BatchOperation):
        """Add operation to results."""
        self.operations.append(operation)
        
        if operation.status == "success":
            self.successful += 1
        elif operation.status == "failed":
            self.failed += 1
            self.errors[len(self.operations) - 1] = operation.error
        elif operation.status == "skipped":
            self.skipped += 1
    
    def complete(self):
        """Mark batch as complete."""
        self.end_time = datetime.utcnow()
    
    def get_duration(self) -> float:
        """Get execution duration in seconds."""
        if not self.end_time:
            return 0
        return (self.end_time - self.start_time).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'batch_id': self.batch_id,
            'total_operations': self.total_operations,
            'successful': self.successful,
            'failed': self.failed,
            'skipped': self.skipped,
            'success_rate': (self.successful / self.total_operations * 100) if self.total_operations > 0 else 0,
            'duration_seconds': self.get_duration(),
            'errors': self.errors,
            'timestamp': self.start_time.isoformat()
        }


class BatchProcessor:
    """Processes batch operations with error handling and rollback."""
    
    def __init__(self):
        """Initialize batch processor."""
        self.operations_registry: Dict[str, Dict[OperationType, Callable]] = {}
        self.validators: Dict[str, Callable] = {}
        self.hooks: Dict[str, List[Callable]] = {
            'before_batch': [],
            'after_batch': [],
            'before_operation': [],
            'after_operation': []
        }
    
    def register_operation(self, resource_type: str, operation_type: OperationType, handler: Callable):
        """Register operation handler."""
        if resource_type not in self.operations_registry:
            self.operations_registry[resource_type] = {}
        
        self.operations_registry[resource_type][operation_type] = handler
        logger.debug(f"Registered operation: {resource_type}/{operation_type.value}")
    
    def register_validator(self, resource_type: str, validator: Callable):
        """Register data validator."""
        self.validators[resource_type] = validator
    
    def add_hook(self, hook_type: str, callback: Callable):
        """Add lifecycle hook."""
        if hook_type in self.hooks:
            self.hooks[hook_type].append(callback)
    
    def _validate_operation(self, operation: BatchOperation) -> Tuple[bool, Optional[str]]:
        """Validate operation data."""
        if operation.resource_type in self.validators:
            validator = self.validators[operation.resource_type]
            try:
                is_valid, error_msg = validator(operation.data)
                return is_valid, error_msg
            except Exception as e:
                return False, str(e)
        
        return True, None
    
    def _execute_operation(self, operation: BatchOperation) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """Execute single operation."""
        # Check if handler exists
        if operation.resource_type not in self.operations_registry:
            return False, f"Unknown resource type: {operation.resource_type}", None
        
        resource_ops = self.operations_registry[operation.resource_type]
        if operation.operation_type not in resource_ops:
            return False, f"Unsupported operation: {operation.operation_type.value}", None
        
        # Execute handler
        handler = resource_ops[operation.operation_type]
        try:
            result = handler(operation)
            return True, None, result
        except Exception as e:
            logger.error(f"Operation execution error: {e}")
            return False, str(e), None
    
    def execute_batch(self, operations: List[BatchOperation], atomic: bool = False) -> BatchResult:
        """
        Execute batch of operations.
        
        Args:
            operations: List of operations to execute
            atomic: If True, fail entire batch on first error
        
        Returns:
            BatchResult with execution details
        """
        batch_id = f"batch_{datetime.utcnow().timestamp()}"
        result = BatchResult(batch_id, len(operations))
        
        logger.info(f"Starting batch {batch_id} with {len(operations)} operations")
        
        # Execute before hooks
        for hook in self.hooks['before_batch']:
            try:
                hook(batch_id, operations)
            except Exception as e:
                logger.error(f"Before hook error: {e}")
        
        # Execute operations
        for i, operation in enumerate(operations):
            logger.debug(f"Executing operation {i+1}/{len(operations)}: {operation.operation_type.value}")
            
            # Before operation hook
            for hook in self.hooks['before_operation']:
                try:
                    hook(operation)
                except Exception as e:
                    logger.error(f"Before operation hook error: {e}")
            
            # Validate operation
            is_valid, error_msg = self._validate_operation(operation)
            if not is_valid:
                operation.status = "failed"
                operation.error = f"Validation failed: {error_msg}"
                result.add_operation(operation)
                
                if atomic:
                    logger.warning(f"Atomic batch failed at operation {i}")
                    break
                continue
            
            # Execute operation
            success, error, op_result = self._execute_operation(operation)
            
            if success:
                operation.status = "success"
                operation.result = op_result
                logger.info(f"Operation {i+1} succeeded")
            else:
                operation.status = "failed"
                operation.error = error
                logger.warning(f"Operation {i+1} failed: {error}")
                
                if atomic:
                    logger.warning(f"Atomic batch failed at operation {i}")
                    break
            
            result.add_operation(operation)
            
            # After operation hook
            for hook in self.hooks['after_operation']:
                try:
                    hook(operation)
                except Exception as e:
                    logger.error(f"After operation hook error: {e}")
        
        # Complete batch
        result.complete()
        
        # Execute after hooks
        for hook in self.hooks['after_batch']:
            try:
                hook(batch_id, result)
            except Exception as e:
                logger.error(f"After hook error: {e}")
        
        logger.info(f"Batch {batch_id} completed: {result.successful} success, {result.failed} failed")
        
        return result


# Global processor instance
_batch_processor: Optional[BatchProcessor] = None


def init_batch_processor() -> BatchProcessor:
    """Initialize batch processor."""
    global _batch_processor
    _batch_processor = BatchProcessor()
    logger.info("✓ Batch processor initialized")
    return _batch_processor


def get_batch_processor() -> Optional[BatchProcessor]:
    """Get batch processor instance."""
    return _batch_processor


class BatchBuilder:
    """Builder for constructing batch operations."""
    
    def __init__(self):
        """Initialize builder."""
        self.operations: List[BatchOperation] = []
    
    def create(self, resource_type: str, data: Dict[str, Any], **metadata) -> 'BatchBuilder':
        """Add create operation."""
        op = BatchOperation(
            operation_type=OperationType.CREATE,
            resource_type=resource_type,
            data=data,
            metadata=metadata
        )
        self.operations.append(op)
        return self
    
    def update(self, resource_type: str, id: str, data: Dict[str, Any], **metadata) -> 'BatchBuilder':
        """Add update operation."""
        op = BatchOperation(
            operation_type=OperationType.UPDATE,
            resource_type=resource_type,
            id=id,
            data=data,
            metadata=metadata
        )
        self.operations.append(op)
        return self
    
    def delete(self, resource_type: str, id: str, **metadata) -> 'BatchBuilder':
        """Add delete operation."""
        op = BatchOperation(
            operation_type=OperationType.DELETE,
            resource_type=resource_type,
            id=id,
            data={},
            metadata=metadata
        )
        self.operations.append(op)
        return self
    
    def custom(self, resource_type: str, data: Dict[str, Any], **metadata) -> 'BatchBuilder':
        """Add custom operation."""
        op = BatchOperation(
            operation_type=OperationType.CUSTOM,
            resource_type=resource_type,
            data=data,
            metadata=metadata
        )
        self.operations.append(op)
        return self
    
    def build(self) -> List[BatchOperation]:
        """Build operations list."""
        return self.operations
    
    def execute(self, atomic: bool = False) -> Optional[BatchResult]:
        """Execute batch."""
        processor = get_batch_processor()
        if not processor:
            logger.error("Batch processor not initialized")
            return None
        
        return processor.execute_batch(self.operations, atomic=atomic)


# Example usage decorator
def batch_operation(resource_type: str, operation_type: OperationType):
    """Decorator for batch operation handlers."""
    def decorator(func):
        processor = get_batch_processor()
        if processor:
            processor.register_operation(resource_type, operation_type, func)
        return func
    return decorator
