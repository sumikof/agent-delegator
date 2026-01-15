"""Metrics Collection System.

This module implements a metrics collection and export system for monitoring
performance and health of the distributed orchestrator.
"""

from __future__ import annotations

import time
import threading
from typing import Any, Dict, List, Optional, Callable
from enum import Enum
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    """Types of metrics."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    SUMMARY = "summary"


@dataclass
class Metric:
    """Represents a single metric."""
    name: str
    metric_type: MetricType
    value: Any
    timestamp: float
    tags: Dict[str, str]
    description: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert metric to dictionary."""
        return {
            "name": self.name,
            "type": self.metric_type,
            "value": self.value,
            "timestamp": self.timestamp,
            "tags": self.tags,
            "description": self.description
        }


@dataclass
class CounterMetric:
    """Counter metric that only increases."""
    name: str
    value: float
    timestamp: float
    tags: Dict[str, str]
    description: str

    def increment(self, amount: float = 1.0) -> None:
        """Increment the counter."""
        self.value += amount
        self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Convert counter metric to dictionary."""
        return {
            "name": self.name,
            "type": "counter",
            "value": self.value,
            "timestamp": self.timestamp,
            "tags": self.tags,
            "description": self.description
        }


@dataclass
class GaugeMetric:
    """Gauge metric that can go up and down."""
    name: str
    value: float
    timestamp: float
    tags: Dict[str, str]
    description: str

    def set(self, value: float) -> None:
        """Set the gauge value."""
        self.value = value
        self.timestamp = time.time()

    def increment(self, amount: float = 1.0) -> None:
        """Increment the gauge."""
        self.value += amount
        self.timestamp = time.time()

    def decrement(self, amount: float = 1.0) -> None:
        """Decrement the gauge."""
        self.value -= amount
        self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Convert gauge metric to dictionary."""
        return {
            "name": self.name,
            "type": "gauge",
            "value": self.value,
            "timestamp": self.timestamp,
            "tags": self.tags,
            "description": self.description
        }


@dataclass
class HistogramMetric:
    """Histogram metric for measuring distributions."""
    name: str
    buckets: Dict[float, int]
    count: int
    sum: float
    timestamp: float
    tags: Dict[str, str]
    description: str

    def record(self, value: float) -> None:
        """Record a value in the histogram."""
        self.count += 1
        self.sum += value
        
        # Find the appropriate bucket
        for bucket in sorted(self.buckets.keys()):
            if value <= bucket:
                self.buckets[bucket] += 1
                break
        
        self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Convert histogram metric to dictionary."""
        return {
            "name": self.name,
            "type": "histogram",
            "buckets": self.buckets,
            "count": self.count,
            "sum": self.sum,
            "timestamp": self.timestamp,
            "tags": self.tags,
            "description": self.description
        }


class MetricsCollector:
    """Collects and manages metrics."""

    def __init__(self):
        self._counters: Dict[str, CounterMetric] = {}
        self._gauges: Dict[str, GaugeMetric] = {}
        self._histograms: Dict[str, HistogramMetric] = {}
        self._lock = threading.Lock()

    def create_counter(self, name: str, description: str = "", 
                      tags: Optional[Dict[str, str]] = None) -> CounterMetric:
        """Create a new counter metric."""
        counter = CounterMetric(
            name=name,
            value=0.0,
            timestamp=time.time(),
            tags=tags or {},
            description=description
        )
        
        with self._lock:
            self._counters[name] = counter
        
        return counter

    def create_gauge(self, name: str, initial_value: float = 0.0,
                    description: str = "", tags: Optional[Dict[str, str]] = None) -> GaugeMetric:
        """Create a new gauge metric."""
        gauge = GaugeMetric(
            name=name,
            value=initial_value,
            timestamp=time.time(),
            tags=tags or {},
            description=description
        )
        
        with self._lock:
            self._gauges[name] = gauge
        
        return gauge

    def create_histogram(self, name: str, buckets: List[float],
                        description: str = "", tags: Optional[Dict[str, str]] = None) -> HistogramMetric:
        """Create a new histogram metric."""
        bucket_dict = {bucket: 0 for bucket in buckets}
        
        histogram = HistogramMetric(
            name=name,
            buckets=bucket_dict,
            count=0,
            sum=0.0,
            timestamp=time.time(),
            tags=tags or {},
            description=description
        )
        
        with self._lock:
            self._histograms[name] = histogram
        
        return histogram

    def get_counter(self, name: str) -> Optional[CounterMetric]:
        """Get a counter metric by name."""
        with self._lock:
            return self._counters.get(name)

    def get_gauge(self, name: str) -> Optional[GaugeMetric]:
        """Get a gauge metric by name."""
        with self._lock:
            return self._gauges.get(name)

    def get_histogram(self, name: str) -> Optional[HistogramMetric]:
        """Get a histogram metric by name."""
        with self._lock:
            return self._histograms.get(name)

    def increment_counter(self, name: str, amount: float = 1.0) -> bool:
        """Increment a counter metric."""
        with self._lock:
            counter = self._counters.get(name)
            if counter:
                counter.increment(amount)
                return True
            return False

    def set_gauge(self, name: str, value: float) -> bool:
        """Set a gauge metric value."""
        with self._lock:
            gauge = self._gauges.get(name)
            if gauge:
                gauge.set(value)
                return True
            return False

    def record_histogram(self, name: str, value: float) -> bool:
        """Record a value in a histogram."""
        with self._lock:
            histogram = self._histograms.get(name)
            if histogram:
                histogram.record(value)
                return True
            return False

    def get_all_metrics(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all metrics as dictionaries."""
        with self._lock:
            return {
                "counters": [counter.to_dict() for counter in self._counters.values()],
                "gauges": [gauge.to_dict() for gauge in self._gauges.values()],
                "histograms": [histogram.to_dict() for histogram in self._histograms.values()]
            }

    def get_metrics_by_type(self, metric_type: MetricType) -> List[Dict[str, Any]]:
        """Get metrics by type."""
        with self._lock:
            if metric_type == MetricType.COUNTER:
                return [counter.to_dict() for counter in self._counters.values()]
            elif metric_type == MetricType.GAUGE:
                return [gauge.to_dict() for gauge in self._gauges.values()]
            elif metric_type == MetricType.HISTOGRAM:
                return [histogram.to_dict() for histogram in self._histograms.values()]
            else:
                return []

    def reset(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()


class MetricsExporter:
    """Exports metrics to external systems."""

    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self._export_interval = 60.0  # seconds
        self._running = False
        self._export_thread = None

    def start(self, interval: float = 60.0) -> None:
        """Start the metrics exporter."""
        self._export_interval = interval
        self._running = True
        
        self._export_thread = threading.Thread(
            target=self._export_loop, daemon=True
        )
        self._export_thread.start()
        
        logger.info(f"Started metrics exporter with interval {interval} seconds")

    def stop(self) -> None:
        """Stop the metrics exporter."""
        self._running = False
        if self._export_thread:
            self._export_thread.join(timeout=5.0)
        
        logger.info("Stopped metrics exporter")

    def _export_loop(self) -> None:
        """Main export loop."""
        while self._running:
            try:
                self.export_metrics()
                time.sleep(self._export_interval)
            except Exception as e:
                logger.error(f"Error in metrics export loop: {e}")
                time.sleep(5.0)  # Wait before retrying

    def export_metrics(self) -> None:
        """Export metrics to external systems."""
        metrics = self.metrics_collector.get_all_metrics()
        
        # In a real implementation, this would send to Prometheus, Datadog, etc.
        logger.info(f"Exporting {len(metrics['counters']) + len(metrics['gauges']) + len(metrics['histograms'])} metrics")
        
        # Simulate export to different systems
        self._export_to_prometheus(metrics)
        self._export_to_datadog(metrics)
        self._export_to_cloud_monitoring(metrics)

    def _export_to_prometheus(self, metrics: Dict[str, List[Dict[str, Any]]]) -> None:
        """Export metrics to Prometheus."""
        # Simulate Prometheus export
        logger.debug(f"Exporting {len(metrics['counters']) + len(metrics['gauges']) + len(metrics['histograms'])} metrics to Prometheus")

    def _export_to_datadog(self, metrics: Dict[str, List[Dict[str, Any]]]) -> None:
        """Export metrics to Datadog."""
        # Simulate Datadog export
        logger.debug(f"Exporting {len(metrics['counters']) + len(metrics['gauges']) + len(metrics['histograms'])} metrics to Datadog")

    def _export_to_cloud_monitoring(self, metrics: Dict[str, List[Dict[str, Any]]]) -> None:
        """Export metrics to cloud monitoring."""
        # Simulate cloud monitoring export
        logger.debug(f"Exporting {len(metrics['counters']) + len(metrics['gauges']) + len(metrics['histograms'])} metrics to Cloud Monitoring")

    def add_custom_exporter(self, exporter_func: Callable[[Dict[str, List[Dict[str, Any]]]], None]) -> None:
        """Add a custom metrics exporter."""
        # Store the custom exporter and call it during export
        self._custom_exporters.append(exporter_func)


# Global metrics collector instance
metrics_collector = MetricsCollector()


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance."""
    global metrics_collector
    return metrics_collector