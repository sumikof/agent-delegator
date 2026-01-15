#!/usr/bin/env python3
"""Test script for multi-agent coordination system."""

import time
from orchestrator.coordination import (
    communication_protocol,
    coordination_protocol,
    task_coordinator,
    conflict_resolution_system,
    MessageType,
    MessagePriority
)


def test_communication_protocol():
    """Test the agent communication protocol."""
    print("Testing communication protocol...")
    
    # Send a test message
    message_id = communication_protocol.send_message(
        sender_id="agent1",
        recipient_id="agent2",
        message_type=MessageType.REQUEST,
        payload={"test": "hello", "data": "test_message"},
        priority=MessagePriority.MEDIUM
    )
    
    print(f"Sent message with ID: {message_id}")
    
    # Check if message was received
    message = communication_protocol.receive_message("agent2", timeout=1.0)
    if message:
        print(f"Message received: {message.message_id}")
        print(f"Message payload: {message.payload}")
    else:
        print("No message received")
    
    # Get queue metrics
    metrics = communication_protocol.get_queue_metrics()
    print(f"Queue metrics: {metrics}")
    
    return True


def test_coordination_protocol():
    """Test the coordination protocol."""
    print("\nTesting coordination protocol...")
    
    # Test resource access
    granted, request_id = coordination_protocol.request_resource_access(
        requesting_agent="agent1",
        resource_id="test_resource",
        access_type="read"
    )
    
    print(f"Resource access granted: {granted}")
    if not granted:
        print(f"Coordination request ID: {request_id}")
    
    # Release resource
    coordination_protocol.release_resource("agent1", "test_resource")
    
    return True


def test_task_coordinator():
    """Test the task coordinator."""
    print("\nTesting task coordinator...")
    
    # Create some test tasks
    task1_id = task_coordinator.create_task(
        name="Test Task 1",
        description="First test task",
        payload={"data": "task1_data"},
        priority=MessagePriority.MEDIUM
    )
    
    task2_id = task_coordinator.create_task(
        name="Test Task 2",
        description="Second test task",
        payload={"data": "task2_data"},
        priority=MessagePriority.HIGH,
        coordination_group="test_group"
    )
    
    print(f"Created tasks: {task1_id}, {task2_id}")
    
    # Add dependency
    success = task_coordinator.add_dependency(
        task_id=task2_id,
        dependency_task_id=task1_id,
        description="Task 2 depends on Task 1"
    )
    
    print(f"Dependency added: {success}")
    
    # Get task graph metrics
    metrics = task_coordinator.get_coordination_status()
    print(f"Task graph metrics: {metrics}")
    
    return True


def test_conflict_resolution():
    """Test the conflict resolution system."""
    print("\nTesting conflict resolution system...")
    
    # Start monitoring
    conflict_resolution_system.start_monitoring(interval=2.0)
    
    # Let it run for a few seconds
    time.sleep(3.0)
    
    # Get system status
    status = conflict_resolution_system.get_system_status()
    print(f"Conflict resolution status: {status}")
    
    # Stop monitoring
    conflict_resolution_system.stop_monitoring()
    
    return True


def main():
    """Run all coordination system tests."""
    print("Testing Multi-Agent Coordination System")
    print("=" * 50)
    
    try:
        # Test communication protocol
        test_communication_protocol()
        
        # Test coordination protocol
        test_coordination_protocol()
        
        # Test task coordinator
        test_task_coordinator()
        
        # Test conflict resolution
        test_conflict_resolution()
        
        print("\n" + "=" * 50)
        print("All tests completed successfully!")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    main()