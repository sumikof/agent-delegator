"""Log Aggregation and Analysis System.

This module implements a comprehensive log aggregation and analysis system for collecting,
storing, analyzing, and visualizing logs from distributed components in the orchestrator.
"""

from __future__ import annotations

import time
import threading
import logging
import json
import re
from typing import Any, Dict, List, Optional, Callable, Pattern
from enum import Enum
from dataclasses import dataclass
from collections import defaultdict, deque
import hashlib
import os
from datetime import datetime

logger = logging.getLogger(__name__)


class LogLevel(str, Enum):
    """Standard log levels."""
    DEBUG = "debug"
    INFO = "info" 
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LogSource(str, Enum):
    """Sources of logs."""
    AGENT = "agent"
    ORCHESTRATOR = "orchestrator"
    WORKFLOW = "workflow"
    SYSTEM = "system"
    API = "api"
    PLUGIN = "plugin"


@dataclass
class LogEntry:
    """Represents a single log entry."""
    log_id: str
    timestamp: float
    level: LogLevel
    source: LogSource
    component: str
    message: str
    context: Dict[str, Any]
    tags: Dict[str, str]
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert log entry to dictionary."""
        return {
            "log_id": self.log_id,
            "timestamp": self.timestamp,
            "level": self.level,
            "source": self.source,
            "component": self.component,
            "message": self.message,
            "context": self.context,
            "tags": self.tags,
            "trace_id": self.trace_id,
            "span_id": self.span_id
        }


class LogFilter:
    """Filter for log entries."""
    
    def __init__(self, 
                 min_level: Optional[LogLevel] = None,
                 sources: Optional[List[LogSource]] = None,
                 components: Optional[List[str]] = None,
                 text_pattern: Optional[str] = None,
                 time_range: Optional[tuple[float, float]] = None):
        self.min_level = min_level
        self.sources = sources or []
        self.components = components or []
        self.text_pattern = text_pattern
        self.time_range = time_range
        self._compiled_pattern: Optional[Pattern] = None
        
        if self.text_pattern:
            try:
                self._compiled_pattern = re.compile(text_pattern, re.IGNORECASE)
            except re.error:
                logger.warning(f"Invalid regex pattern: {text_pattern}")
                self._compiled_pattern = None
    
    def matches(self, log_entry: LogEntry) -> bool:
        """Check if a log entry matches the filter."""
        # Check time range
        if self.time_range:
            start_time, end_time = self.time_range
            if not (start_time <= log_entry.timestamp <= end_time):
                return False
        
        # Check minimum level
        if self.min_level:
            level_priority = {
                LogLevel.DEBUG: 1,
                LogLevel.INFO: 2,
                LogLevel.WARNING: 3,
                LogLevel.ERROR: 4,
                LogLevel.CRITICAL: 5
            }
            if level_priority[log_entry.level] < level_priority[self.min_level]:
                return False
        
        # Check sources
        if self.sources and log_entry.source not in self.sources:
            return False
            
        # Check components
        if self.components and log_entry.component not in self.components:
            return False
        
        # Check text pattern
        if self._compiled_pattern:
            if not self._compiled_pattern.search(log_entry.message):
                return False
        
        return True


class LogAggregator:
    """Aggregates logs from multiple sources."""
    
    def __init__(self, max_logs: int = 10000):
        self.max_logs = max_logs
        self._logs: deque[LogEntry] = deque(maxlen=max_logs)
        self._lock = threading.Lock()
        self._indexes = {
            "level": defaultdict(list),
            "source": defaultdict(list),
            "component": defaultdict(list),
            "time": []
        }
    
    def add_log(self, log_entry: LogEntry) -> None:
        """Add a log entry to the aggregator."""
        with self._lock:
            self._logs.append(log_entry)
            
            # Update indexes
            self._indexes["level"][log_entry.level].append(len(self._logs) - 1)
            self._indexes["source"][log_entry.source].append(len(self._logs) - 1)
            self._indexes["component"][log_entry.component].append(len(self._logs) - 1)
            self._indexes["time"].append((log_entry.timestamp, len(self._logs) - 1))
    
    def get_logs(self, log_filter: Optional[LogFilter] = None) -> List[LogEntry]:
        """Get logs matching the filter."""
        with self._lock:
            if log_filter is None:
                return list(self._logs)
            
            # Use indexes for efficient filtering
            candidate_indices = set()
            
            # Filter by level
            if log_filter.min_level:
                level_priority = {
                    LogLevel.DEBUG: 1,
                    LogLevel.INFO: 2,
                    LogLevel.WARNING: 3,
                    LogLevel.ERROR: 4,
                    LogLevel.CRITICAL: 5
                }
                min_priority = level_priority[log_filter.min_level]
                for level, indices in self._indexes["level"].items():
                    if level_priority[level] >= min_priority:
                        candidate_indices.update(indices)
            else:
                candidate_indices = set(range(len(self._logs)))
            
            # Filter by source
            if log_filter.sources:
                source_indices = set()
                for source in log_filter.sources:
                    source_indices.update(self._indexes["source"][source])
                candidate_indices.intersection_update(source_indices)
            
            # Filter by component
            if log_filter.components:
                component_indices = set()
                for component in log_filter.components:
                    component_indices.update(self._indexes["component"][component])
                candidate_indices.intersection_update(component_indices)
            
            # Filter by time range
            if log_filter.time_range:
                start_time, end_time = log_filter.time_range
                time_filtered = []
                for timestamp, idx in self._indexes["time"]:
                    if start_time <= timestamp <= end_time:
                        time_filtered.append(idx)
                candidate_indices.intersection_update(time_filtered)
            
            # Apply text pattern filter
            result = []
            for idx in sorted(candidate_indices):
                log_entry = self._logs[idx]
                if log_filter._compiled_pattern:
                    if log_filter._compiled_pattern.search(log_entry.message):
                        result.append(log_entry)
                else:
                    result.append(log_entry)
            
            return result
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the logs."""
        with self._lock:
            level_counts = {level: len(indices) for level, indices in self._indexes["level"].items()}
            source_counts = {source: len(indices) for source, indices in self._indexes["source"].items()}
            component_counts = {component: len(indices) for component, indices in self._indexes["component"].items()}
            
            return {
                "total_logs": len(self._logs),
                "level_counts": level_counts,
                "source_counts": source_counts,
                "component_counts": component_counts,
                "time_range": {
                    "start": self._indexes["time"][0][0] if self._indexes["time"] else None,
                    "end": self._indexes["time"][-1][0] if self._indexes["time"] else None
                } if self._indexes["time"] else None
            }
    
    def clear(self) -> None:
        """Clear all logs."""
        with self._lock:
            self._logs.clear()
            self._indexes = {
                "level": defaultdict(list),
                "source": defaultdict(list),
                "component": defaultdict(list),
                "time": []
            }


class LogAnalyzer:
    """Analyzes logs for patterns, anomalies, and insights."""
    
    def __init__(self, aggregator: LogAggregator):
        self.aggregator = aggregator
    
    def analyze_error_patterns(self, time_window: Optional[float] = None) -> Dict[str, Any]:
        """Analyze error patterns in logs."""
        logs = self.aggregator.get_logs()
        
        if time_window:
            current_time = time.time()
            start_time = current_time - time_window
            logs = [log for log in logs if log.timestamp >= start_time]
        
        error_logs = [log for log in logs if log.level in (LogLevel.ERROR, LogLevel.CRITICAL)]
        
        # Group by message pattern
        pattern_groups = defaultdict(list)
        for log in error_logs:
            # Simple pattern extraction (could be enhanced with NLP)
            pattern = log.message.split("|")[0].strip() if "|" in log.message else log.message
            pattern_groups[pattern].append(log)
        
        # Find most common patterns
        sorted_patterns = sorted(pattern_groups.items(), key=lambda x: len(x[1]), reverse=True)
        
        return {
            "total_errors": len(error_logs),
            "error_rate": len(error_logs) / len(logs) if logs else 0,
            "top_patterns": [
                {
                    "pattern": pattern,
                    "count": len(logs),
                    "first_occurrence": min(log.timestamp for log in logs),
                    "last_occurrence": max(log.timestamp for log in logs),
                    "components": list(set(log.component for log in logs))
                }
                for pattern, logs in sorted_patterns[:10]
            ]
        }
    
    def detect_anomalies(self, time_window: Optional[float] = None) -> List[Dict[str, Any]]:
        """Detect anomalies in log patterns."""
        logs = self.aggregator.get_logs()
        
        if time_window:
            current_time = time.time()
            start_time = current_time - time_window
            logs = [log for log in logs if log.timestamp >= start_time]
        
        anomalies = []
        
        # Check for sudden spikes in error rate
        if len(logs) > 100:
            error_logs = [log for log in logs if log.level in (LogLevel.ERROR, LogLevel.CRITICAL)]
            error_rate = len(error_logs) / len(logs)
            
            if error_rate > 0.1:  # More than 10% errors
                anomalies.append({
                    "type": "high_error_rate",
                    "severity": "high",
                    "description": f"High error rate detected: {error_rate:.2%}",
                    "error_count": len(error_logs),
                    "total_logs": len(logs),
                    "time_window": time_window or "all_time"
                })
        
        # Check for repeated errors from same component
        component_errors = defaultdict(list)
        for log in logs:
            if log.level in (LogLevel.ERROR, LogLevel.CRITICAL):
                component_errors[log.component].append(log)
        
        for component, errors in component_errors.items():
            if len(errors) > 5:  # More than 5 errors from same component
                time_range = max(e.timestamp for e in errors) - min(e.timestamp for e in errors)
                if time_range < 300:  # Within 5 minutes
                    anomalies.append({
                        "type": "component_error_spike",
                        "severity": "medium",
                        "description": f"Error spike from {component}: {len(errors)} errors in {time_range:.1f} seconds",
                        "component": component,
                        "error_count": len(errors),
                        "time_range": time_range
                    })
        
        return anomalies
    
    def generate_insights(self) -> Dict[str, Any]:
        """Generate insights from log analysis."""
        stats = self.aggregator.get_stats()
        error_analysis = self.analyze_error_patterns()
        anomalies = self.detect_anomalies()
        
        return {
            "stats": stats,
            "error_analysis": error_analysis,
            "anomalies": anomalies,
            "recommendations": self._generate_recommendations(error_analysis, anomalies)
        }
    
    def _generate_recommendations(self, error_analysis: Dict[str, Any], anomalies: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        if error_analysis["error_rate"] > 0.05:  # More than 5% errors
            recommendations.append("Investigate high error rate - consider adding more robust error handling")
        
        if anomalies:
            for anomaly in anomalies:
                if anomaly["type"] == "high_error_rate":
                    recommendations.append(f"Address high error rate: {anomaly['description']}")
                elif anomaly["type"] == "component_error_spike":
                    recommendations.append(f"Investigate {anomaly['component']} for potential issues")
        
        if error_analysis["top_patterns"]:
            for pattern in error_analysis["top_patterns"][:3]:
                recommendations.append(f"Review common error pattern: {pattern['pattern']}")
        
        return recommendations


class LogExporter:
    """Exports logs to various destinations."""
    
    def __init__(self, aggregator: LogAggregator):
        self.aggregator = aggregator
    
    def export_to_json(self, file_path: str, log_filter: Optional[LogFilter] = None) -> None:
        """Export logs to JSON file."""
        logs = self.aggregator.get_logs(log_filter)
        
        with open(file_path, 'w') as f:
            json.dump([log.to_dict() for log in logs], f, indent=2)
    
    def export_to_csv(self, file_path: str, log_filter: Optional[LogFilter] = None) -> None:
        """Export logs to CSV file."""
        logs = self.aggregator.get_logs(log_filter)
        
        import csv
        with open(file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "level", "source", "component", "message"])
            for log in logs:
                writer.writerow([
                    datetime.fromtimestamp(log.timestamp).isoformat(),
                    log.level,
                    log.source,
                    log.component,
                    log.message
                ])
    
    def export_to_elasticsearch(self, logs: List[LogEntry], index_name: str = "orchestrator-logs") -> None:
        """Export logs to Elasticsearch (mock implementation)."""
        # In a real implementation, this would connect to Elasticsearch
        logger.info(f"Would export {len(logs)} logs to Elasticsearch index: {index_name}")
        # Mock: print what would be exported
        for log in logs[:5]:  # Show first 5 as example
            logger.debug(f"Exporting log: {log.to_dict()}")


class AdvancedLogger:
    """Advanced logging interface that integrates with the log aggregation system."""
    
    def __init__(self, log_manager: LogManager, component: str):
        self.log_manager = log_manager
        self.component = component
    
    def debug(self, message: str, context: Optional[Dict[str, Any]] = None, **kwargs) -> LogEntry:
        """Log a debug message."""
        return self.log_manager.log(
            level=LogLevel.DEBUG,
            source=LogSource.SYSTEM,
            component=self.component,
            message=message,
            context=context or {},
            tags=kwargs
        )
    
    def info(self, message: str, context: Optional[Dict[str, Any]] = None, **kwargs) -> LogEntry:
        """Log an info message."""
        return self.log_manager.log(
            level=LogLevel.INFO,
            source=LogSource.SYSTEM,
            component=self.component,
            message=message,
            context=context or {},
            tags=kwargs
        )
    
    def warning(self, message: str, context: Optional[Dict[str, Any]] = None, **kwargs) -> LogEntry:
        """Log a warning message."""
        return self.log_manager.log(
            level=LogLevel.WARNING,
            source=LogSource.SYSTEM,
            component=self.component,
            message=message,
            context=context or {},
            tags=kwargs
        )
    
    def error(self, message: str, context: Optional[Dict[str, Any]] = None, **kwargs) -> LogEntry:
        """Log an error message."""
        return self.log_manager.log(
            level=LogLevel.ERROR,
            source=LogSource.SYSTEM,
            component=self.component,
            message=message,
            context=context or {},
            tags=kwargs
        )
    
    def critical(self, message: str, context: Optional[Dict[str, Any]] = None, **kwargs) -> LogEntry:
        """Log a critical message."""
        return self.log_manager.log(
            level=LogLevel.CRITICAL,
            source=LogSource.SYSTEM,
            component=self.component,
            message=message,
            context=context or {},
            tags=kwargs
        )


class LogManager:
    """Main log management system that coordinates aggregation, analysis, and export."""
    
    def __init__(self):
        self.aggregator = LogAggregator()
        self.analyzer = LogAnalyzer(self.aggregator)
        self.exporter = LogExporter(self.aggregator)
        self._log_producers = []
        self._component_loggers = {}
    
    def get_logger(self, component: str) -> AdvancedLogger:
        """Get an AdvancedLogger for a specific component."""
        if component not in self._component_loggers:
            self._component_loggers[component] = AdvancedLogger(self, component)
        return self._component_loggers[component]
    
    def log(self, 
            level: LogLevel,
            source: LogSource,
            component: str,
            message: str,
            context: Optional[Dict[str, Any]] = None,
            tags: Optional[Dict[str, str]] = None,
            trace_id: Optional[str] = None,
            span_id: Optional[str] = None) -> LogEntry:
        """Create and store a log entry."""
        log_entry = LogEntry(
            log_id=self._generate_log_id(),
            timestamp=time.time(),
            level=level,
            source=source,
            component=component,
            message=message,
            context=context or {},
            tags=tags or {},
            trace_id=trace_id,
            span_id=span_id
        )
        
        self.aggregator.add_log(log_entry)
        
        # Notify producers
        for producer in self._log_producers:
            try:
                producer(log_entry)
            except Exception as e:
                logger.error(f"Log producer failed: {e}")
        
        return log_entry
    
    def _generate_log_id(self) -> str:
        """Generate a unique log ID."""
        return hashlib.md5(f"{time.time()}-{os.urandom(8)}".encode()).hexdigest()
    
    def get_aggregator(self) -> LogAggregator:
        """Get the log aggregator."""
        return self.aggregator
    
    def get_analyzer(self) -> LogAnalyzer:
        """Get the log analyzer."""
        return self.analyzer
    
    def get_exporter(self) -> LogExporter:
        """Get the log exporter."""
        return self.exporter
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for a log dashboard."""
        stats = self.aggregator.get_stats()
        analysis = self.analyzer.analyze_error_patterns(3600)  # Last hour
        anomalies = self.analyzer.detect_anomalies(3600)  # Last hour
        
        return {
            "stats": stats,
            "recent_errors": analysis,
            "anomalies": anomalies,
            "timestamp": time.time()
        }


# Convenience functions for common logging operations

def create_log_manager() -> LogManager:
    """Create a new LogManager instance."""
    return LogManager()


def setup_log_aggregation(log_manager: LogManager, components: List[str]) -> None:
    """Setup log aggregation for specific components."""
    for component in components:
        # This would typically integrate with existing logging systems
        logger.info(f"Setting up log aggregation for component: {component}")