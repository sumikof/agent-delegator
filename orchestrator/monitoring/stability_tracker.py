"""
Stability Tracker

Tracks system stability, error rates, and reliability metrics
for the agent orchestration system.
"""

import time
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import json
import os


@dataclass
class StabilityEvent:
    """Stability event record."""
    event_type: str  # "error", "warning", "crash", "recovery"
    timestamp: float
    agent_name: Optional[str] = None
    task_name: Optional[str] = None
    error_message: Optional[str] = None
    severity: str = "info"  # "info", "warning", "error", "critical"
    additional_data: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp,
            "agent_name": self.agent_name,
            "task_name": self.task_name,
            "error_message": self.error_message,
            "severity": self.severity,
            "additional_data": self.additional_data,
            "datetime": datetime.fromtimestamp(self.timestamp).isoformat(),
        }


class StabilityTracker:
    """Tracks system stability and reliability metrics."""

    def __init__(self, storage_dir: str = "/tmp/stability_events"):
        """Initialize stability tracker.
        
        Args:
            storage_dir: Directory to store stability data
        """
        self.storage_dir = storage_dir
        self.events: List[StabilityEvent] = []
        self.lock = threading.Lock()
        
        # Create storage directory if it doesn't exist
        os.makedirs(self.storage_dir, exist_ok=True)

    def record_event(self, event: StabilityEvent):
        """Record a stability event.
        
        Args:
            event: StabilityEvent to record
        """
        persist_needed = False
        
        with self.lock:
            self.events.append(event)
            
            # Check if persistence is needed for critical events
            if event.severity in ["error", "critical"]:
                persist_needed = True
        
        # Persist outside of lock to avoid deadlock
        if persist_needed:
            self.persist_events()

    def record_error(self, agent_name: str, task_name: str, error_message: str, 
                    severity: str = "error", additional_data: Optional[Dict] = None):
        """Record an error event."""
        event = StabilityEvent(
            event_type="error",
            timestamp=time.time(),
            agent_name=agent_name,
            task_name=task_name,
            error_message=error_message,
            severity=severity,
            additional_data=additional_data,
        )
        self.record_event(event)

    def record_warning(self, agent_name: str, task_name: str, warning_message: str,
                      additional_data: Optional[Dict] = None):
        """Record a warning event."""
        event = StabilityEvent(
            event_type="warning",
            timestamp=time.time(),
            agent_name=agent_name,
            task_name=task_name,
            error_message=warning_message,
            severity="warning",
            additional_data=additional_data,
        )
        self.record_event(event)

    def record_crash(self, agent_name: str, task_name: str, error_message: str,
                    additional_data: Optional[Dict] = None):
        """Record a crash event."""
        event = StabilityEvent(
            event_type="crash",
            timestamp=time.time(),
            agent_name=agent_name,
            task_name=task_name,
            error_message=error_message,
            severity="critical",
            additional_data=additional_data,
        )
        self.record_event(event)

    def record_recovery(self, agent_name: str, task_name: str, 
                       message: str = "Agent recovered successfully"):
        """Record a recovery event."""
        event = StabilityEvent(
            event_type="recovery",
            timestamp=time.time(),
            agent_name=agent_name,
            task_name=task_name,
            error_message=message,
            severity="info",
        )
        self.record_event(event)

    def get_events(self, event_type: Optional[str] = None, 
                  severity: Optional[str] = None) -> List[StabilityEvent]:
        """Get recorded events, optionally filtered."""
        with self.lock:
            events = self.events.copy()
            
            if event_type:
                events = [e for e in events if e.event_type == event_type]
            
            if severity:
                events = [e for e in events if e.severity == severity]
            
            return events

    def get_error_rate(self, window_seconds: int = 3600) -> float:
        """Calculate error rate within a time window."""
        # Copy events to avoid holding lock during computation
        with self.lock:
            events_copy = self.events.copy()
        
        current_time = time.time()
        window_start = current_time - window_seconds
        
        total_events = sum(1 for e in events_copy if e.timestamp >= window_start)
        error_events = sum(1 for e in events_copy 
                         if e.timestamp >= window_start and e.event_type == "error")
        
        return error_events / total_events if total_events > 0 else 0.0

    def get_stability_score(self) -> float:
        """Calculate overall stability score (0-100, higher is better)."""
        # Copy events to avoid holding lock during computation
        with self.lock:
            events_copy = self.events.copy()
        
        if not events_copy:
            return 100.0
        
        # Count events by severity
        critical_count = sum(1 for e in events_copy if e.severity == "critical")
        error_count = sum(1 for e in events_copy if e.severity == "error")
        warning_count = sum(1 for e in events_copy if e.severity == "warning")
        info_count = sum(1 for e in events_copy if e.severity == "info")
        
        total_events = len(events_copy)
        
        # Calculate stability score (weighted by severity)
        # Critical events have highest negative impact
        stability_score = 100.0
        stability_score -= critical_count * 20
        stability_score -= error_count * 10
        stability_score -= warning_count * 2
        stability_score += info_count * 0.5  # Recovery events improve score
        
        # Ensure score is within bounds
        return max(0.0, min(100.0, stability_score))

    def get_aggregated_stats(self) -> Dict[str, Any]:
        """Get aggregated stability statistics."""
        # Copy events to avoid holding lock during computation
        with self.lock:
            events_copy = self.events.copy()
        
        if not events_copy:
            return {
                "total_events": 0,
                "error_rate": 0.0,
                "stability_score": 100.0,
                "events_by_type": {},
                "events_by_severity": {},
            }
        
        # Count events by type
        events_by_type = {}
        for event in events_copy:
            if event.event_type not in events_by_type:
                events_by_type[event.event_type] = 0
            events_by_type[event.event_type] += 1
        
        # Count events by severity
        events_by_severity = {}
        for event in events_copy:
            if event.severity not in events_by_severity:
                events_by_severity[event.severity] = 0
            events_by_severity[event.severity] += 1
        
        return {
            "total_events": len(events_copy),
            "error_rate": self.get_error_rate(),
            "stability_score": self.get_stability_score(),
            "events_by_type": events_by_type,
            "events_by_severity": events_by_severity,
            "timestamp": datetime.now().isoformat(),
        }

    def persist_events(self):
        """Persist current events to disk."""
        events_to_persist = []
        
        # Copy events to persist (minimize lock time)
        with self.lock:
            if not self.events:
                return
            events_to_persist = self.events.copy()
            # Clear events after copying
            self.events = self.events[-1000:] if len(self.events) > 1000 else []
        
        # Create timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"stability_{timestamp}.json"
        filepath = os.path.join(self.storage_dir, filename)
        
        # Convert events to serializable format
        events_data = [event.to_dict() for event in events_to_persist]
        
        try:
            with open(filepath, "w") as f:
                json.dump(events_data, f, indent=2)
        except Exception as e:
            print(f"Error persisting stability events: {e}")

    def shutdown(self):
        """Shutdown the stability tracker."""
        self.persist_events()  # Final persistence


class StabilityAnalyzer:
    """Analyzes stability patterns and trends."""

    def __init__(self, tracker: StabilityTracker):
        self.tracker = tracker

    def analyze_trends(self, window_seconds: int = 3600) -> Dict[str, Any]:
        """Analyze stability trends over time."""
        events = self.tracker.get_events()
        current_time = time.time()
        window_start = current_time - window_seconds
        
        # Filter events within time window
        recent_events = [e for e in events if e.timestamp >= window_start]
        
        if not recent_events:
            return {
                "trend": "stable",
                "error_rate_trend": "stable",
                "stability_score_trend": "stable",
                "recent_events": 0,
            }
        
        # Calculate error rate trend
        error_rate = self.tracker.get_error_rate(window_seconds)
        
        # Simple trend analysis
        error_events = sum(1 for e in recent_events if e.event_type == "error")
        total_events = len(recent_events)
        
        if error_rate > 0.3:
            error_rate_trend = "degrading"
        elif error_rate > 0.1:
            error_rate_trend = "warning"
        else:
            error_rate_trend = "stable"
        
        # Calculate stability score trend
        stability_score = self.tracker.get_stability_score()
        
        if stability_score < 50:
            stability_score_trend = "critical"
        elif stability_score < 75:
            stability_score_trend = "warning"
        else:
            stability_score_trend = "stable"
        
        # Overall trend
        if error_rate_trend == "degrading" or stability_score_trend == "critical":
            overall_trend = "degrading"
        elif error_rate_trend == "warning" or stability_score_trend == "warning":
            overall_trend = "warning"
        else:
            overall_trend = "stable"
        
        return {
            "trend": overall_trend,
            "error_rate_trend": error_rate_trend,
            "stability_score_trend": stability_score_trend,
            "recent_events": total_events,
            "error_rate": error_rate,
            "stability_score": stability_score,
            "timestamp": datetime.now().isoformat(),
        }