"""
Plugin Registry - Manages the registration and discovery of available plugins.

The PluginRegistry maintains a catalog of all available plugins, their metadata,
and provides discovery capabilities for the plugin system.
"""

import importlib
import pkgutil
from typing import Dict, List, Optional, Type
import logging

from orchestrator.agents.base import Agent as BaseAgent

logger = logging.getLogger(__name__)


class PluginRegistry:
    """Registry for managing available plugins and their metadata."""
    
    def __init__(self):
        self._plugins: Dict[str, Type[BaseAgent]] = {}
        self._plugin_metadata: Dict[str, dict] = {}
        
    def register_plugin(self, plugin_name: str, plugin_class: Type[BaseAgent], 
                       metadata: Optional[dict] = None) -> None:
        """Register a plugin with the registry.
        
        Args:
            plugin_name: Unique name for the plugin
            plugin_class: The plugin class (must inherit from BaseAgent)
            metadata: Additional metadata about the plugin
        """
        if not issubclass(plugin_class, BaseAgent):
            raise ValueError(f"Plugin class {plugin_class.__name__} must inherit from BaseAgent")
        
        if plugin_name in self._plugins:
            logger.warning(f"Plugin {plugin_name} already registered, overwriting")
        
        self._plugins[plugin_name] = plugin_class
        self._plugin_metadata[plugin_name] = metadata or {}
        logger.info(f"Registered plugin: {plugin_name}")
        
    def get_plugin(self, plugin_name: str) -> Optional[Type[BaseAgent]]:
        """Get a plugin class by name.
        
        Args:
            plugin_name: Name of the plugin to retrieve
            
        Returns:
            The plugin class if found, None otherwise
        """
        return self._plugins.get(plugin_name)
        
    def get_plugin_metadata(self, plugin_name: str) -> Optional[dict]:
        """Get metadata for a plugin.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Plugin metadata if found, None otherwise
        """
        return self._plugin_metadata.get(plugin_name)
        
    def list_plugins(self) -> List[str]:
        """List all registered plugin names.
        
        Returns:
            List of all registered plugin names
        """
        return list(self._plugins.keys())
        
    def discover_plugins(self, package_name: str = "orchestrator.plugins") -> None:
        """Discover and register plugins from a package.
        
        Args:
            package_name: Package name to search for plugins
        """
        try:
            package = importlib.import_module(package_name)
            
            for _, module_name, _ in pkgutil.iter_modules(package.__path__):
                full_module_name = f"{package_name}.{module_name}"
                
                try:
                    module = importlib.import_module(full_module_name)
                    
                    # Look for plugin classes in the module
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        
                        if (isinstance(attr, type) and 
                            issubclass(attr, BaseAgent) and 
                            attr != BaseAgent and 
                            not attr_name.startswith('_')):
                            
                            # Extract metadata from class docstring or attributes
                            metadata = {
                                'module': full_module_name,
                                'class': attr_name,
                                'description': getattr(attr, '__doc__', '').strip() if getattr(attr, '__doc__') else ''
                            }
                            
                            self.register_plugin(module_name, attr, metadata)
                            
                except ImportError as e:
                    logger.warning(f"Failed to import plugin module {full_module_name}: {e}")
                    continue
                    
        except ImportError:
            logger.debug(f"No plugins package found at {package_name}")
        
    def unregister_plugin(self, plugin_name: str) -> bool:
        """Unregister a plugin.
        
        Args:
            plugin_name: Name of the plugin to unregister
            
        Returns:
            True if plugin was found and unregistered, False otherwise
        """
        if plugin_name in self._plugins:
            del self._plugins[plugin_name]
            if plugin_name in self._plugin_metadata:
                del self._plugin_metadata[plugin_name]
            logger.info(f"Unregistered plugin: {plugin_name}")
            return True
        return False
        
    def clear(self) -> None:
        """Clear all registered plugins."""
        self._plugins.clear()
        self._plugin_metadata.clear()
        logger.info("Cleared all plugins from registry")