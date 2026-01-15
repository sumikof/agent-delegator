#!/usr/bin/env python3
"""
Test script for monitoring system integration.
"""

import sys
import os
import time

# Add the workspace to Python path
sys.path.insert(0, '/workspace')

from orchestrator.monitoring.metrics_collector import MetricsCollector
from orchestrator.monitoring.resource_monitor import ResourceMonitor
from orchestrator.monitoring.stability_tracker import StabilityTracker


def test_monitoring_system():
    """Test the monitoring system components."""
    print("Testing monitoring system...")
    
    # Initialize monitoring components
    print("1. Initializing monitoring components...")
    metrics_collector = MetricsCollector()
    resource_monitor = ResourceMonitor(interval=5)  # Faster interval for testing
    stability_tracker = StabilityTracker()
    
    # Test metrics collector
    print("2. Testing metrics collector...")
    with metrics_collector.start_agent_monitoring("test_agent", "test_task") as monitor:
        time.sleep(0.1)  # Simulate work
    
    metrics = metrics_collector.get_metrics()
    print(f"   Collected {len(metrics)} metrics")
    if metrics:
        metric = metrics[0]
        print(f"   Agent: {metric.agent_name}")
        print(f"   Task: {metric.task_name}")
        print(f"   Duration: {metric.duration_seconds:.3f}s")
        print(f"   Success: {metric.success}")
    
    # Test resource monitor
    print("3. Testing resource monitor...")
    time.sleep(2.0)  # Wait for a few snapshots
    snapshots = resource_monitor.get_snapshots()
    print(f"   Collected {len(snapshots)} resource snapshots")
    if snapshots:
        snapshot = snapshots[-1]
        print(f"   CPU Usage: {snapshot.cpu_usage_percent:.1f}%")
        print(f"   Memory Usage: {snapshot.memory_usage_mb:.1f}MB")
        print(f"   Memory Percent: {snapshot.memory_percent:.1f}%")
    
    # Test stability tracker
    print("4. Testing stability tracker...")
    stability_tracker.record_error("test_agent", "test_task", "Test error message")
    stability_tracker.record_warning("test_agent", "test_task", "Test warning message")
    
    events = stability_tracker.get_events()
    print(f"   Recorded {len(events)} stability events")
    
    # Test aggregated stats
    print("5. Testing aggregated statistics...")
    
    metrics_stats = metrics_collector.get_aggregated_stats()
    print(f"   Metrics - Total executions: {metrics_stats['total_executions']}")
    print(f"   Metrics - Success rate: {metrics_stats['success_rate']:.2f}")
    
    resource_stats = resource_monitor.get_aggregated_stats()
    print(f"   Resources - Avg CPU: {resource_stats['avg_cpu_usage_percent']:.1f}%")
    print(f"   Resources - Avg Memory: {resource_stats['avg_memory_usage_mb']:.1f}MB")
    
    stability_stats = stability_tracker.get_aggregated_stats()
    print(f"   Stability - Total events: {stability_stats['total_events']}")
    print(f"   Stability - Error rate: {stability_stats['error_rate']:.2f}")
    print(f"   Stability - Score: {stability_stats['stability_score']:.1f}")
    
    # Shutdown monitoring system
    print("6. Shutting down monitoring system...")
    metrics_collector.shutdown()
    resource_monitor.shutdown()
    stability_tracker.shutdown()
    
    print("✅ Monitoring system test completed successfully!")


if __name__ == "__main__":
    test_monitoring_system()