"""
Resource Monitor

Monitors system and agent resource usage, including CPU, memory,
and other system metrics for performance optimization.
"""

import time
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import psutil
import json
import os


@dataclass
class ResourceSnapshot:
    """Snapshot of system resource usage at a point in time."""
    timestamp: float
    cpu_usage_percent: float
    memory_usage_mb: float
    memory_percent: float
    disk_usage_percent: float
    network_io_bytes: Dict[str, float]
    process_count: int
    thread_count: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert snapshot to dictionary for serialization."""
        return {
            "timestamp": self.timestamp,
            "cpu_usage_percent": self.cpu_usage_percent,
            "memory_usage_mb": self.memory_usage_mb,
            "memory_percent": self.memory_percent,
            "disk_usage_percent": self.disk_usage_percent,
            "network_io_bytes": self.network_io_bytes,
            "process_count": self.process_count,
            "thread_count": self.thread_count,
            "datetime": datetime.fromtimestamp(self.timestamp).isoformat(),
        }


class ResourceMonitor:
    """Monitors system resource usage over time."""

    def __init__(self, storage_dir: str = "/tmp/resource_metrics", interval: int = 10):
        """Initialize resource monitor.
        
        Args:
            storage_dir: Directory to store resource data
            interval: Monitoring interval in seconds
        """
        self.storage_dir = storage_dir
        self.interval = interval
        self.snapshots: List[ResourceSnapshot] = []
        self.lock = threading.Lock()
        
        # Create storage directory if it doesn't exist
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Start monitoring thread
        self._stop_event = threading.Event()
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()

    def _take_snapshot(self) -> ResourceSnapshot:
        """Take a snapshot of current system resource usage."""
        try:
            # CPU usage
            cpu_usage = psutil.cpu_percent(interval=0.1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_usage_mb = memory.used / (1024 * 1024)
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_usage_percent = disk.percent
            
            # Network I/O
            net_io = psutil.net_io_counters()
            network_io_bytes = {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
            }
            
            # Process count
            process_count = len(psutil.pids())
            
            # Thread count for current process
            current_process = psutil.Process(os.getpid())
            thread_count = current_process.num_threads()
            
            return ResourceSnapshot(
                timestamp=time.time(),
                cpu_usage_percent=cpu_usage,
                memory_usage_mb=memory_usage_mb,
                memory_percent=memory_percent,
                disk_usage_percent=disk_usage_percent,
                network_io_bytes=network_io_bytes,
                process_count=process_count,
                thread_count=thread_count,
            )
        except Exception as e:
            print(f"Error taking resource snapshot: {e}")
            # Return a snapshot with default values
            return ResourceSnapshot(
                timestamp=time.time(),
                cpu_usage_percent=0.0,
                memory_usage_mb=0.0,
                memory_percent=0.0,
                disk_usage_percent=0.0,
                network_io_bytes={"bytes_sent": 0.0, "bytes_recv": 0.0},
                process_count=0,
                thread_count=0,
            )

    def _monitor_loop(self):
        """Main monitoring loop that takes snapshots at regular intervals."""
        while not self._stop_event.wait(self.interval):
            snapshot = self._take_snapshot()
            with self.lock:
                self.snapshots.append(snapshot)
            
            # Persist every 10 snapshots
            if len(self.snapshots) % 10 == 0:
                self.persist_snapshots()

    def get_current_snapshot(self) -> ResourceSnapshot:
        """Get the most recent resource snapshot."""
        with self.lock:
            if self.snapshots:
                return self.snapshots[-1]
            return self._take_snapshot()

    def get_snapshots(self, limit: Optional[int] = None) -> List[ResourceSnapshot]:
        """Get recorded snapshots, optionally limited."""
        with self.lock:
            if limit:
                return self.snapshots[-limit:]
            return self.snapshots.copy()

    def get_aggregated_stats(self) -> Dict[str, Any]:
        """Get aggregated resource usage statistics."""
        with self.lock:
            if not self.snapshots:
                return {
                    "avg_cpu_usage_percent": 0.0,
                    "avg_memory_usage_mb": 0.0,
                    "avg_memory_percent": 0.0,
                    "avg_disk_usage_percent": 0.0,
                    "total_snapshots": 0,
                }
            
            total_snapshots = len(self.snapshots)
            avg_cpu = sum(s.cpu_usage_percent for s in self.snapshots) / total_snapshots
            avg_memory_mb = sum(s.memory_usage_mb for s in self.snapshots) / total_snapshots
            avg_memory_percent = sum(s.memory_percent for s in self.snapshots) / total_snapshots
            avg_disk = sum(s.disk_usage_percent for s in self.snapshots) / total_snapshots
            
            return {
                "avg_cpu_usage_percent": avg_cpu,
                "avg_memory_usage_mb": avg_memory_mb,
                "avg_memory_percent": avg_memory_percent,
                "avg_disk_usage_percent": avg_disk,
                "total_snapshots": total_snapshots,
                "timestamp": datetime.now().isoformat(),
            }

    def persist_snapshots(self):
        """Persist current snapshots to disk."""
        snapshots_to_persist = []
        
        # Copy snapshots to persist (minimize lock time)
        with self.lock:
            if not self.snapshots:
                return
            snapshots_to_persist = self.snapshots.copy()
            # Keep only the last 100 snapshots in memory
            self.snapshots = self.snapshots[-100:] if len(self.snapshots) > 100 else []
        
        # Create timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"resources_{timestamp}.json"
        filepath = os.path.join(self.storage_dir, filename)
        
        # Convert snapshots to serializable format
        snapshots_data = [snapshot.to_dict() for snapshot in snapshots_to_persist]
        
        try:
            with open(filepath, "w") as f:
                json.dump(snapshots_data, f, indent=2)
        except Exception as e:
            print(f"Error persisting resource snapshots: {e}")

    def shutdown(self):
        """Shutdown the resource monitor."""
        self._stop_event.set()
        self._monitor_thread.join()
        self.persist_snapshots()  # Final persistence


class ResourceAlert:
    """Resource alert system for monitoring thresholds."""

    def __init__(self, monitor: ResourceMonitor):
        self.monitor = monitor
        self.thresholds = {
            "cpu_usage_percent": 80.0,
            "memory_percent": 90.0,
            "disk_usage_percent": 85.0,
        }
        self.alerts: List[Dict[str, Any]] = []

    def check_thresholds(self) -> List[Dict[str, Any]]:
        """Check if any resource thresholds are exceeded."""
        snapshot = self.monitor.get_current_snapshot()
        alerts = []
        
        if snapshot.cpu_usage_percent > self.thresholds["cpu_usage_percent"]:
            alerts.append({
                "type": "cpu",
                "value": snapshot.cpu_usage_percent,
                "threshold": self.thresholds["cpu_usage_percent"],
                "timestamp": snapshot.timestamp,
                "message": f"High CPU usage: {snapshot.cpu_usage_percent:.1f}% > {self.thresholds['cpu_usage_percent']}%",
            })
        
        if snapshot.memory_percent > self.thresholds["memory_percent"]:
            alerts.append({
                "type": "memory",
                "value": snapshot.memory_percent,
                "threshold": self.thresholds["memory_percent"],
                "timestamp": snapshot.timestamp,
                "message": f"High memory usage: {snapshot.memory_percent:.1f}% > {self.thresholds['memory_percent']}%",
            })
        
        if snapshot.disk_usage_percent > self.thresholds["disk_usage_percent"]:
            alerts.append({
                "type": "disk",
                "value": snapshot.disk_usage_percent,
                "threshold": self.thresholds["disk_usage_percent"],
                "timestamp": snapshot.timestamp,
                "message": f"High disk usage: {snapshot.disk_usage_percent:.1f}% > {self.thresholds['disk_usage_percent']}%",
            })
        
        if alerts:
            self.alerts.extend(alerts)
        
        return alerts

    def get_alerts(self) -> List[Dict[str, Any]]:
        """Get all recorded alerts."""
        return self.alerts.copy()

    def clear_alerts(self):
        """Clear all alerts."""
        self.alerts.clear()