"""Advanced Error Handler.

This module implements advanced error handling and recovery mechanisms
for the distributed orchestrator system.
"""

from __future__ import annotations

import time
import threading
from typing import Any, Dict, List, Optional, Callable
from enum import Enum
from dataclasses import dataclass
import logging
import traceback

logger = logging.getLogger(__name__)


class ErrorSeverity(str, Enum):
    """Severity levels for errors."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ErrorType(str, Enum):
    """Types of errors."""
    SYSTEM = "system"
    NETWORK = "network"
    RESOURCE = "resource"
    TIMEOUT = "timeout"
    VALIDATION = "validation"
    CONFIGURATION = "configuration"
    UNKNOWN = "unknown"


@dataclass
class ErrorRecord:
    """Represents an error record."""
    error_id: str
    timestamp: float
    severity: ErrorSeverity
    error_type: ErrorType
    message: str
    details: Dict[str, Any]
    stack_trace: str
    context: Dict[str, Any]
    status: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert error record to dictionary."""
        return {
            "error_id": self.error_id,
            "timestamp": self.timestamp,
            "severity": self.severity,
            "error_type": self.error_type,
            "message": self.message,
            "details": self.details,
            "stack_trace": self.stack_trace,
            "context": self.context,
            "status": self.status
        }


@dataclass
class ErrorRecoveryStrategy:
    """Represents an error recovery strategy."""
    strategy_id: str
    name: str
    error_type: ErrorType
    severity: ErrorSeverity
    recovery_function: Callable
    max_retries: int
    retry_delay: float
    description: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert recovery strategy to dictionary."""
        return {
            "strategy_id": self.strategy_id,
            "name": self.name,
            "error_type": self.error_type,
            "severity": self.severity,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "description": self.description
        }


class AdvancedErrorHandler:
    """Advanced error handler for the distributed orchestrator."""

    def __init__(self):
        self._error_records: Dict[str, ErrorRecord] = {}
        self._recovery_strategies: Dict[str, ErrorRecoveryStrategy] = {}
        self._lock = threading.Lock()
        self._error_queue: List[ErrorRecord] = []
        self._processing_thread = None
        self._running = False

    def record_error(self, error_type: ErrorType, message: str,
                    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                    details: Optional[Dict[str, Any]] = None,
                    context: Optional[Dict[str, Any]] = None,
                    exception: Optional[Exception] = None) -> str:
        """Record an error."""
        import uuid
        error_id = str(uuid.uuid4())
        
        stack_trace = ""
        if exception:
            stack_trace = "".join(traceback.format_exception(type(exception), exception, exception.__traceback__))
        
        error_record = ErrorRecord(
            error_id=error_id,
            timestamp=time.time(),
            severity=severity,
            error_type=error_type,
            message=message,
            details=details or {},
            stack_trace=stack_trace,
            context=context or {},
            status="recorded"
        )
        
        with self._lock:
            self._error_records[error_id] = error_record
            self._error_queue.append(error_record)
        
        logger.error(f"Error recorded: {message} (ID: {error_id})")
        
        return error_id

    def add_recovery_strategy(self, strategy: ErrorRecoveryStrategy) -> None:
        """Add an error recovery strategy."""
        with self._lock:
            self._recovery_strategies[strategy.strategy_id] = strategy
        
        logger.info(f"Added recovery strategy: {strategy.name}")

    def start_error_processing(self) -> None:
        """Start the error processing thread."""
        self._running = True
        
        self._processing_thread = threading.Thread(
            target=self._process_errors, daemon=True
        )
        self._processing_thread.start()
        
        logger.info("Started error processing thread")

    def stop_error_processing(self) -> None:
        """Stop the error processing thread."""
        self._running = False
        if self._processing_thread:
            self._processing_thread.join(timeout=5.0)
        
        logger.info("Stopped error processing thread")

    def _process_errors(self) -> None:
        """Process errors from the queue."""
        while self._running:
            try:
                with self._lock:
                    if self._error_queue:
                        error = self._error_queue.pop(0)
                        self._handle_error(error)
                
                time.sleep(0.1)  # Small delay to prevent busy waiting
            except Exception as e:
                logger.error(f"Error in error processing loop: {e}")
                time.sleep(1.0)

    def _handle_error(self, error: ErrorRecord) -> None:
        """Handle an error with appropriate recovery strategy."""
        error.status = "processing"
        
        # Find matching recovery strategies
        matching_strategies = []
        
        with self._lock:
            for strategy in self._recovery_strategies.values():
                if (strategy.error_type == error.error_type and
                    strategy.severity.value <= error.severity.value):
                    matching_strategies.append(strategy)
        
        # Sort by priority (lower priority number = higher priority)
        matching_strategies.sort(key=lambda s: s.max_retries, reverse=True)
        
        if matching_strategies:
            # Use the highest priority strategy
            strategy = matching_strategies[0]
            self._execute_recovery_strategy(error, strategy)
        else:
            # No specific recovery strategy, use default handling
            self._default_error_handling(error)

    def _execute_recovery_strategy(self, error: ErrorRecord, 
                                  strategy: ErrorRecoveryStrategy) -> None:
        """Execute a recovery strategy."""
        logger.info(f"Executing recovery strategy {strategy.name} for error {error.error_id}")
        
        try:
            # Execute the recovery function
            result = strategy.recovery_function(error)
            
            if result:
                error.status = "recovered"
                logger.info(f"Error {error.error_id} recovered successfully")
            else:
                error.status = "recovery_failed"
                logger.warning(f"Recovery failed for error {error.error_id}")
        except Exception as e:
            error.status = "recovery_error"
            logger.error(f"Error during recovery for {error.error_id}: {e}")

    def _default_error_handling(self, error: ErrorRecord) -> None:
        """Default error handling when no specific strategy is available."""
        logger.warning(f"No recovery strategy for error {error.error_id}, using default handling")
        
        # Simple retry logic for certain error types
        if error.error_type in [ErrorType.NETWORK, ErrorType.TIMEOUT]:
            error.status = "retry_scheduled"
            logger.info(f"Scheduled retry for error {error.error_id}")
        else:
            error.status = "handled"
            logger.info(f"Error {error.error_id} handled with default strategy")

    def get_error(self, error_id: str) -> Optional[ErrorRecord]:
        """Get an error record by ID."""
        with self._lock:
            return self._error_records.get(error_id)

    def get_errors_by_type(self, error_type: ErrorType) -> List[ErrorRecord]:
        """Get errors by type."""
        with self._lock:
            return [error for error in self._error_records.values() 
                   if error.error_type == error_type]

    def get_errors_by_severity(self, severity: ErrorSeverity) -> List[ErrorRecord]:
        """Get errors by severity."""
        with self._lock:
            return [error for error in self._error_records.values() 
                   if error.severity == severity]

    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics."""
        with self._lock:
            severity_counts = {}
            for severity in ErrorSeverity:
                severity_counts[severity] = len(self.get_errors_by_severity(severity))
            
            type_counts = {}
            for error_type in ErrorType:
                type_counts[error_type] = len(self.get_errors_by_type(error_type))
            
            return {
                "total_errors": len(self._error_records),
                "severity_counts": severity_counts,
                "type_counts": type_counts,
                "recovery_strategies": len(self._recovery_strategies),
                "pending_errors": len([e for e in self._error_records.values() if e.status == "recorded"]),
                "recovered_errors": len([e for e in self._error_records.values() if e.status == "recovered"])
            }

    def create_default_recovery_strategies(self) -> None:
        """Create default error recovery strategies."""
        import uuid
        
        # Network error recovery
        def network_recovery(error: ErrorRecord) -> bool:
            logger.info(f"Attempting network recovery for error {error.error_id}")
            # Simulate network recovery
            time.sleep(1)
            return True
        
        network_strategy = ErrorRecoveryStrategy(
            strategy_id=str(uuid.uuid4()),
            name="network_error_recovery",
            error_type=ErrorType.NETWORK,
            severity=ErrorSeverity.MEDIUM,
            recovery_function=network_recovery,
            max_retries=3,
            retry_delay=5.0,
            description="Recovery strategy for network errors"
        )
        
        # Timeout error recovery
        def timeout_recovery(error: ErrorRecord) -> bool:
            logger.info(f"Attempting timeout recovery for error {error.error_id}")
            # Simulate timeout recovery
            time.sleep(1)
            return True
        
        timeout_strategy = ErrorRecoveryStrategy(
            strategy_id=str(uuid.uuid4()),
            name="timeout_error_recovery",
            error_type=ErrorType.TIMEOUT,
            severity=ErrorSeverity.MEDIUM,
            recovery_function=timeout_recovery,
            max_retries=2,
            retry_delay=3.0,
            description="Recovery strategy for timeout errors"
        )
        
        # Resource error recovery
        def resource_recovery(error: ErrorRecord) -> bool:
            logger.info(f"Attempting resource recovery for error {error.error_id}")
            # Simulate resource recovery
            time.sleep(2)
            return True
        
        resource_strategy = ErrorRecoveryStrategy(
            strategy_id=str(uuid.uuid4()),
            name="resource_error_recovery",
            error_type=ErrorType.RESOURCE,
            severity=ErrorSeverity.HIGH,
            recovery_function=resource_recovery,
            max_retries=5,
            retry_delay=10.0,
            description="Recovery strategy for resource errors"
        )
        
        with self._lock:
            self._recovery_strategies[network_strategy.strategy_id] = network_strategy
            self._recovery_strategies[timeout_strategy.strategy_id] = timeout_strategy
            self._recovery_strategies[resource_strategy.strategy_id] = resource_strategy
        
        logger.info("Created default error recovery strategies")


# Global error handler instance
error_handler = AdvancedErrorHandler()


def get_error_handler() -> AdvancedErrorHandler:
    """Get the global error handler instance."""
    global error_handler
    return error_handler