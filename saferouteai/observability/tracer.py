"""Tracing for SafeRouteAI agent operations."""
import time
from contextlib import contextmanager
from typing import Dict, Any, Optional
from datetime import datetime
import saferouteai.config as config


class Tracer:
    """Simple tracer for agent operation timing and context."""
    
    def __init__(self):
        self.traces: Dict[str, Dict[str, Any]] = {}
        self.enabled = config.ENABLE_TRACING
    
    @contextmanager
    def trace(self, operation_name: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Context manager for tracing operations.
        
        Args:
            operation_name: Name of the operation
            metadata: Optional metadata to include
        """
        if not self.enabled:
            yield
            return
        
        trace_id = f"{operation_name}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        start_time = time.time()
        
        trace_data = {
            "operation": operation_name,
            "start_time": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        try:
            yield trace_data
        finally:
            end_time = time.time()
            duration = end_time - start_time
            
            trace_data.update({
                "end_time": datetime.now().isoformat(),
                "duration_seconds": round(duration, 4),
                "status": "success"
            })
            
            self.traces[trace_id] = trace_data
    
    def get_traces(self, operation_name: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        Get trace data.
        
        Args:
            operation_name: Optional filter by operation name
        
        Returns:
            Dictionary of traces
        """
        if operation_name:
            return {
                k: v for k, v in self.traces.items()
                if v.get("operation") == operation_name
            }
        return self.traces
    
    def get_operation_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for each operation type."""
        stats = {}
        
        for trace in self.traces.values():
            op_name = trace.get("operation")
            if op_name not in stats:
                stats[op_name] = {
                    "count": 0,
                    "total_duration": 0.0,
                    "avg_duration": 0.0,
                    "min_duration": float('inf'),
                    "max_duration": 0.0
                }
            
            duration = trace.get("duration_seconds", 0)
            stats[op_name]["count"] += 1
            stats[op_name]["total_duration"] += duration
            stats[op_name]["min_duration"] = min(stats[op_name]["min_duration"], duration)
            stats[op_name]["max_duration"] = max(stats[op_name]["max_duration"], duration)
        
        # Calculate averages
        for op_stats in stats.values():
            if op_stats["count"] > 0:
                op_stats["avg_duration"] = op_stats["total_duration"] / op_stats["count"]
        
        return stats

