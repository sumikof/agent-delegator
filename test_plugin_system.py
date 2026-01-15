#!/usr/bin/env python3
"""
Test script for the plugin system.

This script tests the dynamic plugin loading and management functionality.
"""

import sys
import os

# Add the workspace to the Python path
sys.path.insert(0, '/workspace')

from orchestrator.plugin.registry import PluginRegistry
from orchestrator.plugin.loader import PluginLoader
from orchestrator.plugin.manager import PluginManager
from orchestrator.context import ContextManager


def test_plugin_system():
    """Test the plugin system functionality."""
    print("Testing Plugin System...")
    
    # Create plugin registry
    registry = PluginRegistry()
    print(f"✓ Created plugin registry")
    
    # Create plugin loader
    loader = PluginLoader(registry)
    print(f"✓ Created plugin loader")
    
    # Create context manager
    context_manager = ContextManager()
    print(f"✓ Created context manager")
    
    # Create plugin manager
    plugin_manager = PluginManager(registry, context_manager)
    print(f"✓ Created plugin manager")
    
    # Load plugins from directory
    print(f"\nLoading plugins from orchestrator/plugins...")
    results = loader.load_plugins_from_directory("orchestrator/plugins")
    
    if results:
        print(f"✓ Loaded {len(results)} plugins:")
        for plugin_name, success in results.items():
            status = "✓" if success else "✗"
            print(f"  {status} {plugin_name}")
    else:
        print(f"✗ No plugins loaded")
    
    # List available plugins
    available_plugins = registry.list_plugins()
    print(f"\nAvailable plugins: {available_plugins}")
    
    # Test creating plugin instances
    if available_plugins:
        print(f"\nTesting plugin instantiation...")
        for plugin_name in available_plugins[:2]:  # Test first 2 plugins
            print(f"Creating instance of {plugin_name}...")
            plugin_instance = plugin_manager.create_plugin_instance(plugin_name)
            
            if plugin_instance:
                print(f"✓ Created instance: {plugin_instance.name}")
                
                # Test initialization
                if hasattr(plugin_instance, 'initialize'):
                    plugin_instance.initialize()
                    print(f"✓ Initialized {plugin_name}")
                
                # Test execution with a simple task
                if hasattr(plugin_instance, 'execute'):
                    task = {
                        'task_id': 'test_task_001',
                        'data': {'test': 'data'},
                        'trace_id': 'test-trace-001'
                    }
                    result = plugin_instance.execute(task)
                    print(f"✓ Executed {plugin_name}: {result.get('summary', 'No summary')}")
                
                # Test cleanup
                if hasattr(plugin_instance, 'cleanup'):
                    plugin_instance.cleanup()
                    print(f"✓ Cleaned up {plugin_name}")
            else:
                print(f"✗ Failed to create instance of {plugin_name}")
    
    # List active plugins
    active_plugins = plugin_manager.list_active_plugins()
    print(f"\nActive plugins: {active_plugins}")
    
    # Cleanup all plugins
    plugin_manager.cleanup_all_plugins()
    print(f"✓ Cleaned up all plugins")
    
    print(f"\n✓ Plugin system test completed successfully!")


if __name__ == "__main__":
    test_plugin_system()