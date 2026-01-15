"""
Plugin Manager - Manages the lifecycle of loaded plugins.

The PluginManager handles the instantiation, configuration, and lifecycle
management of plugins, including initialization, execution, and cleanup.
"""

import logging
from typing import Dict, List, Optional, Type, Any
import inspect

from orchestrator.agents.base import Agent as BaseAgent
from orchestrator.context import ContextManager
from .registry import PluginRegistry

logger = logging.getLogger(__name__)


class PluginManager:
    """Manages the lifecycle of plugin instances."""
    
    def __init__(self, registry: PluginRegistry, context_manager: ContextManager):
        self.registry = registry
        self.context_manager = context_manager
        self._active_plugins: Dict[str, BaseAgent] = {}
        
    def create_plugin_instance(self, plugin_name: str, **kwargs) -> Optional[BaseAgent]:
        """Create an instance of a plugin.
        
        Args:
            plugin_name: Name of the plugin to instantiate
            **kwargs: Additional arguments to pass to the plugin constructor
            
        Returns:
            Instance of the plugin if successful, None otherwise
        """
        plugin_class = self.registry.get_plugin(plugin_name)
        
        if not plugin_class:
            logger.error(f"Plugin {plugin_name} not found in registry")
            return None
        
        try:
            # Get the constructor signature
            sig = inspect.signature(plugin_class.__init__)
            
            # Filter kwargs to only include parameters that the constructor accepts
            valid_kwargs = {}
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue
                if param_name in kwargs:
                    valid_kwargs[param_name] = kwargs[param_name]
            
            # Create the plugin instance
            plugin_instance = plugin_class(**valid_kwargs)
            
            # Store the active plugin
            self._active_plugins[plugin_name] = plugin_instance
            logger.info(f"Created instance of plugin {plugin_name}")
            
            return plugin_instance
            
        except Exception as e:
            logger.error(f"Error creating instance of plugin {plugin_name}: {e}")
            return None
        
    def get_plugin_instance(self, plugin_name: str) -> Optional[BaseAgent]:
        """Get an active plugin instance.
        
        Args:
            plugin_name: Name of the plugin instance to retrieve
            
        Returns:
            Plugin instance if found and active, None otherwise
        """
        return self._active_plugins.get(plugin_name)
        
    def initialize_plugin(self, plugin_name: str, context: Optional[dict] = None) -> bool:
        """Initialize a plugin instance.
        
        Args:
            plugin_name: Name of the plugin to initialize
            context: Optional context to pass to the plugin
            
        Returns:
            True if initialization was successful, False otherwise
        """
        plugin_instance = self.get_plugin_instance(plugin_name)
        
        if not plugin_instance:
            logger.error(f"Plugin instance {plugin_name} not found")
            return False
        
        try:
            # Set up context if provided
            if context:
                plugin_instance.context = context
            
            # Call initialize method if it exists
            if hasattr(plugin_instance, 'initialize') and callable(getattr(plugin_instance, 'initialize')):
                plugin_instance.initialize()
            
            logger.info(f"Initialized plugin {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing plugin {plugin_name}: {e}")
            return False
        
    def execute_plugin(self, plugin_name: str, task: dict, context: Optional[dict] = None) -> Optional[dict]:
        """Execute a plugin with a specific task.
        
        Args:
            plugin_name: Name of the plugin to execute
            task: Task dictionary containing execution parameters
            context: Optional context to pass to the plugin
            
        Returns:
            Result of the plugin execution if successful, None otherwise
        """
        plugin_instance = self.get_plugin_instance(plugin_name)
        
        if not plugin_instance:
            logger.error(f"Plugin instance {plugin_name} not found")
            return None
        
        try:
            # Update context if provided
            if context:
                if hasattr(plugin_instance, 'context'):
                    plugin_instance.context.update(context)
                else:
                    plugin_instance.context = context
            
            # Execute the plugin
            if hasattr(plugin_instance, 'execute') and callable(getattr(plugin_instance, 'execute')):
                result = plugin_instance.execute(task)
                logger.info(f"Executed plugin {plugin_name} with task: {task.get('task_id', 'unknown')}")
                return result
            else:
                logger.error(f"Plugin {plugin_name} does not have an execute method")
                return None
            
        except Exception as e:
            logger.error(f"Error executing plugin {plugin_name}: {e}")
            return None
        
    def cleanup_plugin(self, plugin_name: str) -> bool:
        """Clean up a plugin instance.
        
        Args:
            plugin_name: Name of the plugin to clean up
            
        Returns:
            True if cleanup was successful, False otherwise
        """
        plugin_instance = self.get_plugin_instance(plugin_name)
        
        if not plugin_instance:
            logger.warning(f"Plugin instance {plugin_name} not found for cleanup")
            return False
        
        try:
            # Call cleanup method if it exists
            if hasattr(plugin_instance, 'cleanup') and callable(getattr(plugin_instance, 'cleanup')):
                plugin_instance.cleanup()
            
            # Remove from active plugins
            del self._active_plugins[plugin_name]
            logger.info(f"Cleaned up plugin {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error cleaning up plugin {plugin_name}: {e}")
            return False
        
    def cleanup_all_plugins(self) -> None:
        """Clean up all active plugin instances."""
        for plugin_name in list(self._active_plugins.keys()):
            self.cleanup_plugin(plugin_name)
        logger.info("Cleaned up all active plugins")
        
    def list_active_plugins(self) -> List[str]:
        """List all active plugin instances.
        
        Returns:
            List of names of all active plugin instances
        """
        return list(self._active_plugins.keys())
        
    def get_plugin_status(self, plugin_name: str) -> dict:
        """Get the status of a plugin instance.
        
        Args:
            plugin_name: Name of the plugin to check
            
        Returns:
            Dictionary containing plugin status information
        """
        plugin_instance = self.get_plugin_instance(plugin_name)
        
        if not plugin_instance:
            return {'status': 'not_found', 'plugin_name': plugin_name}
        
        status = {
            'status': 'active',
            'plugin_name': plugin_name,
            'class': plugin_instance.__class__.__name__,
            'module': plugin_instance.__class__.__module__
        }
        
        # Add additional status info if available
        if hasattr(plugin_instance, 'get_status') and callable(getattr(plugin_instance, 'get_status')):
            status.update(plugin_instance.get_status())
        
        return status
        
    def configure_plugin(self, plugin_name: str, config: dict) -> bool:
        """Configure a plugin instance.
        
        Args:
            plugin_name: Name of the plugin to configure
            config: Configuration dictionary
            
        Returns:
            True if configuration was successful, False otherwise
        """
        plugin_instance = self.get_plugin_instance(plugin_name)
        
        if not plugin_instance:
            logger.error(f"Plugin instance {plugin_name} not found")
            return False
        
        try:
            if hasattr(plugin_instance, 'configure') and callable(getattr(plugin_instance, 'configure')):
                plugin_instance.configure(config)
                logger.info(f"Configured plugin {plugin_name}")
                return True
            else:
                # If no configure method, try to set attributes directly
                for key, value in config.items():
                    if hasattr(plugin_instance, key):
                        setattr(plugin_instance, key, value)
                logger.info(f"Configured plugin {plugin_name} via direct attribute setting")
                return True
            
        except Exception as e:
            logger.error(f"Error configuring plugin {plugin_name}: {e}")
            return False