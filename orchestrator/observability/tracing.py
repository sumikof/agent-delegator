"""Distributed Tracing System.

This module implements a distributed tracing system for tracking requests and operations
across multiple services and nodes in the distributed orchestrator.
"""

from __future__ import annotations

import time
import uuid
import threading
from typing import Any, Dict, List, Optional
from enum import Enum
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


class TraceStatus(str, Enum):
    """Status of a trace span."""
    CREATED = "created"
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class TraceSpan:
    """Represents a single span in a distributed trace."""
    span_id: str
    trace_id: str
    parent_span_id: Optional[str]
    name: str
    service: str
    start_time: float
    end_time: Optional[float]
    status: TraceStatus
    tags: Dict[str, str]
    logs: List[Dict[str, Any]]
    metrics: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert span to dictionary."""
        return {
            "span_id": self.span_id,
            "trace_id": self.trace_id,
            "parent_span_id": self.parent_span_id,
            "name": self.name,
            "service": self.service,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "status": self.status,
            "tags": self.tags,
            "logs": self.logs,
            "metrics": self.metrics
        }

    def duration(self) -> Optional[float]:
        """Calculate the duration of the span."""
        if self.end_time is not None:
            return self.end_time - self.start_time
        return None

    def add_tag(self, key: str, value: str) -> None:
        """Add a tag to the span."""
        self.tags[key] = value

    def add_log(self, message: str, timestamp: Optional[float] = None, 
                fields: Optional[Dict[str, Any]] = None) -> None:
        """Add a log entry to the span."""
        log_entry = {
            "timestamp": timestamp or time.time(),
            "message": message,
            "fields": fields or {}
        }
        self.logs.append(log_entry)

    def add_metric(self, key: str, value: Any) -> None:
        """Add a metric to the span."""
        self.metrics[key] = value

    def complete(self, status: TraceStatus = TraceStatus.COMPLETED) -> None:
        """Complete the span."""
        self.end_time = time.time()
        self.status = status


@dataclass
class TraceContext:
    """Context for distributed tracing."""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    baggage: Dict[str, str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert trace context to dictionary."""
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "baggage": self.baggage
        }


class DistributedTracer:
    """Distributed tracer for tracking operations across services."""

    def __init__(self, service_name: str):
        self.service_name = service_name
        self._spans: Dict[str, TraceSpan] = {}
        self._traces: Dict[str, List[TraceSpan]] = {}
        self._lock = threading.Lock()

    def create_span(self, name: str, parent_span_id: Optional[str] = None,
                   trace_id: Optional[str] = None) -> TraceSpan:
        """Create a new trace span."""
        span_id = str(uuid.uuid4())
        trace_id = trace_id or str(uuid.uuid4())
        
        span = TraceSpan(
            span_id=span_id,
            trace_id=trace_id,
            parent_span_id=parent_span_id,
            name=name,
            service=self.service_name,
            start_time=time.time(),
            end_time=None,
            status=TraceStatus.CREATED,
            tags={},
            logs=[],
            metrics={}
        )
        
        with self._lock:
            self._spans[span_id] = span
            
            if trace_id not in self._traces:
                self._traces[trace_id] = []
            self._traces[trace_id].append(span)
        
        return span

    def start_span(self, span_id: str) -> bool:
        """Start a trace span."""
        with self._lock:
            span = self._spans.get(span_id)
            if span:
                span.status = TraceStatus.STARTED
                return True
            return False

    def complete_span(self, span_id: str, status: TraceStatus = TraceStatus.COMPLETED) -> bool:
        """Complete a trace span."""
        with self._lock:
            span = self._spans.get(span_id)
            if span:
                span.complete(status)
                return True
            return False

    def get_span(self, span_id: str) -> Optional[TraceSpan]:
        """Get a span by ID."""
        with self._lock:
            return self._spans.get(span_id)

    def get_trace(self, trace_id: str) -> List[TraceSpan]:
        """Get all spans for a trace."""
        with self._lock:
            return self._traces.get(trace_id, [])

    def get_spans_by_service(self, service: str) -> List[TraceSpan]:
        """Get spans for a specific service."""
        with self._lock:
            return [span for span in self._spans.values() if span.service == service]

    def get_spans_by_status(self, status: TraceStatus) -> List[TraceSpan]:
        """Get spans by status."""
        with self._lock:
            return [span for span in self._spans.values() if span.status == status]

    def create_trace_context(self, span: TraceSpan) -> TraceContext:
        """Create a trace context for propagation."""
        return TraceContext(
            trace_id=span.trace_id,
            span_id=span.span_id,
            parent_span_id=span.parent_span_id,
            baggage={}
        )

    def extract_trace_context(self, context_data: Dict[str, Any]) -> Optional[TraceContext]:
        """Extract trace context from data."""
        try:
            return TraceContext(
                trace_id=context_data["trace_id"],
                span_id=context_data["span_id"],
                parent_span_id=context_data.get("parent_span_id"),
                baggage=context_data.get("baggage", {})
            )
        except KeyError:
            return None

    def inject_trace_context(self, context: TraceContext) -> Dict[str, Any]:
        """Inject trace context into data for propagation."""
        return context.to_dict()

    def get_trace_statistics(self) -> Dict[str, Any]:
        """Get statistics about traces."""
        with self._lock:
            total_spans = len(self._spans)
            total_traces = len(self._traces)
            
            status_counts = {}
            for status in TraceStatus:
                status_counts[status] = len(self.get_spans_by_status(status))
            
            return {
                "total_spans": total_spans,
                "total_traces": total_traces,
                "status_counts": status_counts,
                "services": list(set(span.service for span in self._spans.values()))
            }

    def export_traces(self) -> Dict[str, List[Dict[str, Any]]]:
        """Export all traces as dictionaries."""
        with self._lock:
            return {
                trace_id: [span.to_dict() for span in spans]
                for trace_id, spans in self._traces.items()
            }


# Global tracer instance
distributed_tracer = DistributedTracer("orchestrator")


def get_distributed_tracer(service_name: str = "orchestrator") -> DistributedTracer:
    """Get or create a distributed tracer instance."""
    global distributed_tracer
    
    if distributed_tracer.service_name != service_name:
        distributed_tracer = DistributedTracer(service_name)
    
    return distributed_tracer