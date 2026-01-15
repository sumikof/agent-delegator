"""
Plugin Loader - Dynamically loads plugins from various sources.

The PluginLoader handles the dynamic loading of plugins from different sources
including local directories, installed packages, and remote repositories.
"""

import importlib
import logging
import os
import sys
from typing import Dict, List, Optional, Type
import inspect

# Alias for compatibility
isclass = inspect.isclass

from orchestrator.agents.base import Agent as BaseAgent
from .registry import PluginRegistry

logger = logging.getLogger(__name__)


class PluginLoader:
    """Loads plugins dynamically from various sources."""
    
    def __init__(self, registry: PluginRegistry):
        self.registry = registry
        
    def load_plugin_from_module(self, module_path: str, plugin_name: Optional[str] = None) -> bool:
        """Load a plugin from a Python module.
        
        Args:
            module_path: Path to the Python module (e.g., 'myplugin.module')
            plugin_name: Optional name to register the plugin as
            
        Returns:
            True if plugin was loaded successfully, False otherwise
        """
        try:
            module = importlib.import_module(module_path)
            
            # Find all agent classes in the module
            plugin_classes = []
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, BaseAgent) and 
                    attr != BaseAgent and 
                    not attr_name.startswith('_')):
                    plugin_classes.append((attr_name, attr))
            
            if not plugin_classes:
                logger.warning(f"No agent classes found in module {module_path}")
                return False
            
            # Register all found plugin classes
            for class_name, plugin_class in plugin_classes:
                effective_plugin_name = plugin_name or class_name
                
                # Extract metadata from the class
                metadata = {
                    'module': module_path,
                    'class': class_name,
                    'description': getattr(plugin_class, '__doc__', '').strip() if getattr(plugin_class, '__doc__') else '',
                    'version': getattr(plugin_class, '__version__', '1.0.0')
                }
                
                self.registry.register_plugin(effective_plugin_name, plugin_class, metadata)
                logger.info(f"Loaded plugin {effective_plugin_name} from {module_path}")
            
            return True
            
        except ImportError as e:
            logger.error(f"Failed to import module {module_path}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error loading plugin from {module_path}: {e}")
            return False
        
    def load_plugin_from_file(self, file_path: str, plugin_name: Optional[str] = None) -> bool:
        """Load a plugin from a Python file.
        
        Args:
            file_path: Path to the Python file
            plugin_name: Optional name to register the plugin as
            
        Returns:
            True if plugin was loaded successfully, False otherwise
        """
        try:
            # Get the directory and module name from file path
            dir_path = os.path.dirname(file_path)
            module_name = os.path.splitext(os.path.basename(file_path))[0]
            
            # Add directory to sys.path temporarily
            if dir_path not in sys.path:
                sys.path.insert(0, dir_path)
            
            # Import the module
            module = importlib.import_module(module_name)
            
            # Find agent classes and register them
            success = False
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isclass(attr) and 
                    issubclass(attr, BaseAgent) and 
                    attr != BaseAgent and 
                    not attr_name.startswith('_')):
                    
                    effective_plugin_name = plugin_name or attr_name
                    metadata = {
                        'file': file_path,
                        'class': attr_name,
                        'description': getattr(attr, '__doc__', '').strip() if getattr(attr, '__doc__') else ''
                    }
                    
                    self.registry.register_plugin(effective_plugin_name, attr, metadata)
                    logger.info(f"Loaded plugin {effective_plugin_name} from {file_path}")
                    success = True
            
            return success
            
        except Exception as e:
            logger.error(f"Error loading plugin from {file_path}: {e}")
            return False
        finally:
            # Clean up sys.path
            if dir_path in sys.path:
                sys.path.remove(dir_path)
        
    def load_plugins_from_directory(self, directory_path: str) -> Dict[str, bool]:
        """Load all plugins from a directory.
        
        Args:
            directory_path: Path to directory containing plugin files
            
        Returns:
            Dictionary mapping plugin names to load success status
        """
        results = {}
        
        if not os.path.isdir(directory_path):
            logger.error(f"Directory {directory_path} does not exist")
            return results
        
        # Add directory to sys.path temporarily
        if directory_path not in sys.path:
            sys.path.insert(0, directory_path)
        
        try:
            for filename in os.listdir(directory_path):
                if filename.endswith('.py') and not filename.startswith('_'):
                    module_name = os.path.splitext(filename)[0]
                    
                    try:
                        module = importlib.import_module(module_name)
                        
                        # Find and register agent classes
                        for attr_name in dir(module):
                            attr = getattr(module, attr_name)
                            if (isclass(attr) and 
                                issubclass(attr, BaseAgent) and 
                                attr != BaseAgent and 
                                not attr_name.startswith('_')):
                                
                                plugin_name = f"{module_name}.{attr_name}"
                                metadata = {
                                    'file': os.path.join(directory_path, filename),
                                    'module': module_name,
                                    'class': attr_name,
                                    'description': getattr(attr, '__doc__', '').strip() if getattr(attr, '__doc__') else ''
                                }
                                
                                self.registry.register_plugin(plugin_name, attr, metadata)
                                results[plugin_name] = True
                                logger.info(f"Loaded plugin {plugin_name} from {filename}")
                                
                    except Exception as e:
                        logger.error(f"Error loading plugin from {filename}: {e}")
                        results[filename] = False
        
        finally:
            # Clean up sys.path
            if directory_path in sys.path:
                sys.path.remove(directory_path)
        
        return results
        
    def load_plugin_from_entry_point(self, entry_point: str) -> bool:
        """Load a plugin from a setuptools entry point.
        
        Args:
            entry_point: Entry point string (e.g., 'myplugin=myplugin.module:PluginClass')
            
        Returns:
            True if plugin was loaded successfully, False otherwise
        """
        try:
            if ':' not in entry_point:
                logger.error(f"Invalid entry point format: {entry_point}")
                return False
            
            module_path, class_name = entry_point.split(':', 1)
            module = importlib.import_module(module_path)
            plugin_class = getattr(module, class_name)
            
            if not issubclass(plugin_class, BaseAgent):
                logger.error(f"Class {class_name} is not a valid agent plugin")
                return False
            
            # Extract metadata
            metadata = {
                'entry_point': entry_point,
                'module': module_path,
                'class': class_name,
                'description': getattr(plugin_class, '__doc__', '').strip() if getattr(plugin_class, '__doc__') else ''
            }
            
            self.registry.register_plugin(class_name, plugin_class, metadata)
            logger.info(f"Loaded plugin {class_name} from entry point {entry_point}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading plugin from entry point {entry_point}: {e}")
            return False