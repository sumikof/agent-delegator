"""
Example Plugin - Demonstrates the plugin system functionality.

This is a sample plugin that shows how to create custom agents that can be
dynamically loaded by the orchestration system.
"""

from orchestrator.agents.base import Agent as BaseAgent
import json
from datetime import datetime
from typing import Any
import logging

# Set up logging
logger = logging.getLogger(__name__)


def create_response(status: str, summary: str, findings: list = None, 
                   artifacts: list = None, next_actions: list = None, 
                   trace_id: str = None) -> dict:
    """Create a standard response conforming to the common response schema."""
    return {
        "status": status,
        "summary": summary,
        "findings": findings or [],
        "artifacts": artifacts or [],
        "next_actions": next_actions or [],
        "context": {},
        "trace_id": trace_id or f"trace-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "execution_time_ms": 0
    }


class ExamplePlugin(BaseAgent):
    """
    Example plugin that demonstrates basic plugin functionality.
    
    This plugin can be used as a template for creating custom agents.
    """
    
    def __init__(self, name: str = "ExamplePlugin", **kwargs):
        super().__init__(agent_id="example_plugin", name=name, **kwargs)
        self.config = kwargs.get('config', {})
        self.initialized = False
        
    def initialize(self):
        """Initialize the plugin."""
        self.initialized = True
        logger.info(f"{self.name} initialized with config: {self.config}")
        
    def execute(self, task: dict) -> dict:
        """Execute the plugin with a specific task.
        
        Args:
            task: Task dictionary containing execution parameters
            
        Returns:
            Result of the plugin execution
        """
        if not self.initialized:
            self.initialize()
            
        logger.info(f"{self.name} executing task: {task.get('task_id', 'unknown')}")
        
        # Process the task
        result = {
            'status': 'completed',
            'task_id': task.get('task_id', 'unknown'),
            'message': f"Task executed by {self.name}",
            'data': {
                'input': task.get('data', {}),
                'processed_by': self.name,
                'plugin_version': '1.0.0'
            }
        }
        
        return create_response(
            status="OK",
            summary=f"Example plugin executed task {task.get('task_id', 'unknown')}",
            findings=[],
            artifacts=[],
            next_actions=[],
            trace_id=task.get('trace_id', 'example-trace-001')
        )
        
    def cleanup(self):
        """Clean up the plugin."""
        logger.info(f"{self.name} cleaning up")
        self.initialized = False
        
    def configure(self, config: dict):
        """Configure the plugin.
        
        Args:
            config: Configuration dictionary
        """
        self.config.update(config)
        logger.info(f"{self.name} configured with: {config}")
        
    def get_status(self) -> dict:
        """Get the current status of the plugin.
        
        Returns:
            Dictionary containing plugin status information
        """
        return {
            'initialized': self.initialized,
            'config': self.config,
            'status': 'ready' if self.initialized else 'not_initialized'
        }


class AdvancedExamplePlugin(BaseAgent):
    """
    Advanced example plugin with more complex functionality.
    
    This plugin demonstrates more advanced features like state management
    and complex task processing.
    """
    
    def __init__(self, name: str = "AdvancedExamplePlugin", **kwargs):
        super().__init__(agent_id="advanced_example_plugin", name=name, **kwargs)
        self.state = {
            'task_count': 0,
            'last_task': None,
            'performance_metrics': {}
        }
        self.config = kwargs.get('config', {})
        
    def get_current_timestamp(self) -> float:
        """Get current timestamp in seconds since epoch."""
        import time
        return time.time()
        
    def initialize(self):
        """Initialize the advanced plugin."""
        logger.info(f"{self.name} initialized with config: {self.config}")
        self.state['initialized_at'] = self.get_current_timestamp()
        
    def execute(self, task: dict) -> dict:
        """Execute the advanced plugin with a specific task.
        
        Args:
            task: Task dictionary containing execution parameters
            
        Returns:
            Result of the plugin execution
        """
        self.state['task_count'] += 1
        self.state['last_task'] = task.get('task_id', 'unknown')
        
        # Simulate complex processing
        start_time = self.get_current_timestamp()
        
        # Process task data
        processed_data = self._process_task_data(task.get('data', {}))
        
        end_time = self.get_current_timestamp()
        processing_time = end_time - start_time
        
        # Update performance metrics
        self.state['performance_metrics'][task.get('task_id', 'unknown')] = {
            'processing_time': processing_time,
            'data_size': len(str(task.get('data', {})))
        }
        
        result = create_response(
            status="OK",
            summary=f"Advanced plugin processed task {task.get('task_id', 'unknown')}",
            findings=[{
                'severity': 'INFO',
                'message': f"Task processed in {processing_time} seconds",
                'ref': 'performance'
            }],
            artifacts=[{
                'path': f"task_{task.get('task_id', 'unknown')}_output.json",
                'type': 'data',
                'desc': 'Processed task output'
            }],
            next_actions=[],
            trace_id=task.get('trace_id', 'advanced-trace-001')
        )
        
        return result
        
    def _process_task_data(self, data: dict) -> dict:
        """Process task data with advanced logic.
        
        Args:
            data: Input data to process
            
        Returns:
            Processed data
        """
        # Simulate complex data processing
        processed = {}
        
        for key, value in data.items():
            if isinstance(value, dict):
                processed[key] = self._process_task_data(value)
            elif isinstance(value, list):
                processed[key] = [self._process_item(item) for item in value]
            else:
                processed[key] = self._process_item(value)
        
        return processed
        
    def _process_item(self, item: Any) -> Any:
        """Process a single data item."""
        if isinstance(item, str):
            return item.upper()
        elif isinstance(item, (int, float)):
            return item * 2
        else:
            return str(item)
        
    def get_status(self) -> dict:
        """Get the current status of the advanced plugin.
        
        Returns:
            Dictionary containing plugin status information
        """
        return {
            'state': self.state,
            'config': self.config,
            'status': 'active'
        }
        
    def cleanup(self):
        """Clean up the advanced plugin."""
        logger.info(f"{self.name} cleaning up")
        self.state = {'task_count': 0, 'last_task': None, 'performance_metrics': {}}


class SampleDataProcessorPlugin(BaseAgent):
    """
    Sample data processor plugin.
    
    This plugin demonstrates data processing capabilities.
    """
    
    def __init__(self, name: str = "SampleDataProcessor", **kwargs):
        super().__init__(agent_id="sample_data_processor", name=name, **kwargs)
        self.processed_count = 0
        
    def execute(self, task: dict) -> dict:
        """Process data from the task.
        
        Args:
            task: Task dictionary containing data to process
            
        Returns:
            Result of the data processing
        """
        data = task.get('data', {})
        
        # Simple data processing
        processed_data = {
            'original_size': len(str(data)),
            'processed_size': len(str(data)) * 2,  # Simulate processing overhead
            'items_processed': len(data) if isinstance(data, dict) else 1,
            'timestamp': self.get_current_timestamp()
        }
        
        self.processed_count += 1
        
        return create_response(
            status="OK",
            summary=f"Processed {processed_data['items_processed']} items",
            findings=[],
            artifacts=[{
                'path': f"processed_data_{self.processed_count}.json",
                'type': 'data',
                'desc': 'Processed data output'
            }],
            next_actions=[],
            trace_id=task.get('trace_id', 'data-processor-trace-001')
        )