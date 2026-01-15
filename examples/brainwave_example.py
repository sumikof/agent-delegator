"""
Example demonstrating brainwave interface integration with the AI agent orchestration system.

This example shows how to:
1. Initialize the orchestrator with brainwave interface enabled
2. Process EEG data to extract cognitive states
3. Use cognitive states to control workflow execution
4. Handle brainwave-based actions and feedback
"""

import numpy as np
import time
from orchestrator.parallel.orchestrator import ParallelOrchestrator
from orchestrator.agents.registry import AgentRegistry


def generate_mock_eeg_data(num_channels=8, num_samples=256):
    """Generate mock EEG data for demonstration purposes."""
    # Generate random data that simulates different cognitive states
    base_data = np.random.randn(num_channels, num_samples) * 0.1
    
    # Add patterns that might simulate different cognitive states
    # Channel 1: Alpha waves (8-12 Hz) - associated with relaxation
    base_data[0, :] += np.sin(np.linspace(0, 20 * np.pi, num_samples)) * 0.5
    
    # Channel 2: Beta waves (12-30 Hz) - associated with focus/concentration
    base_data[1, :] += np.sin(np.linspace(0, 40 * np.pi, num_samples)) * 0.3
    
    # Channel 3: Theta waves (4-8 Hz) - associated with creativity/meditation
    base_data[2, :] += np.sin(np.linspace(0, 10 * np.pi, num_samples)) * 0.2
    
    return base_data


def simulate_cognitive_state_transitions():
    """Simulate transitions between different cognitive states."""
    states = []
    
    # Simulate a work session with varying cognitive states
    for minute in range(30):  # 30-minute work session
        if minute < 5:
            # Initial focus period
            state = {
                'focus_level': 0.85,
                'stress_level': 0.2,
                'cognitive_load': 0.4,
                'engagement': 0.9
            }
        elif minute < 15:
            # Productive work period
            state = {
                'focus_level': 0.75,
                'stress_level': 0.3,
                'cognitive_load': 0.6,
                'engagement': 0.8
            }
        elif minute < 20:
            # Fatigue setting in
            state = {
                'focus_level': 0.55,
                'stress_level': 0.5,
                'cognitive_load': 0.7,
                'engagement': 0.6
            }
        else:
            # Need for break
            state = {
                'focus_level': 0.35,
                'stress_level': 0.7,
                'cognitive_load': 0.8,
                'engagement': 0.4
            }
        
        states.append(state)
    
    return states


def brainwave_workflow_demo():
    """Demonstrate brainwave interface integration with workflow orchestration."""
    
    print("🧠 Brainwave Interface Integration Demo")
    print("=" * 50)
    
    # Initialize orchestrator with brainwave interface
    print("🔧 Initializing orchestrator with brainwave interface...")
    orchestrator = ParallelOrchestrator(
        max_workers=4,
        agent_registry=AgentRegistry(),
        enable_brainwave=True
    )
    
    # Check brainwave interface status
    status = orchestrator.get_brainwave_status()
    print(f"✅ Brainwave interface status: {status}")
    
    # Submit some example tasks
    print("\n📋 Submitting example tasks...")
    task_ids = []
    
    for i in range(3):
        task_id = orchestrator.submit_task(
            agent_type=f"example_agent_{i}",
            payload={
                "task": f"Example Task {i+1}",
                "description": f"Processing data for task {i+1}"
            },
            priority="medium"
        )
        task_ids.append(task_id)
        print(f"   ✓ Submitted task {task_id}")
    
    # Simulate a work session with brainwave monitoring
    print(f"\n🧠 Starting brainwave monitoring session (simulated)...")
    
    # Simulate cognitive state transitions
    cognitive_states = simulate_cognitive_state_transitions()
    
    actions_taken = []
    
    for minute, state in enumerate(cognitive_states):
        print(f"\n--- Minute {minute + 1} ---")
        print(f"Cognitive State: Focus={state['focus_level']:.2f}, Stress={state['stress_level']:.2f}, "
              f"Load={state['cognitive_load']:.2f}, Engagement={state['engagement']:.2f}")
        
        # Generate mock EEG data that would produce this cognitive state
        # (In reality, this would come from an actual EEG device)
        eeg_data = generate_mock_eeg_data()
        
        # Process EEG data through brainwave interface
        result = orchestrator.handle_brainwave_input(eeg_data)
        
        # Check if any actions were triggered
        if result['action_taken']:
            action = result['action_taken']
            actions_taken.append(action)
            print(f"🚀 Action Triggered: {action['type']}")
            
            if 'params' in action:
                for key, value in action['params'].items():
                    print(f"   - {key}: {value}")
        else:
            print("📊 No actions triggered - continuing normal operation")
        
        # Simulate work being done
        time.sleep(0.5)
    
    # Print summary
    print(f"\n📈 Session Summary:")
    print(f"   • Total time: 30 minutes")
    print(f"   • Actions triggered: {len(actions_taken)}")
    
    if actions_taken:
        print(f"   • Action types:")
        action_types = {}
        for action in actions_taken:
            action_type = action['type']
            action_types[action_type] = action_types.get(action_type, 0) + 1
        
        for action_type, count in action_types.items():
            print(f"     - {action_type}: {count} times")
    
    # Show final task status
    print(f"\n📋 Final Task Status:")
    all_tasks = orchestrator.task_queue.get_all_tasks()
    for task in all_tasks:
        print(f"   • Task {task.task_id}: {task.status.name}")
    
    return orchestrator


def brainwave_adaptive_workflow_demo():
    """Demonstrate adaptive workflow control based on brainwave data."""
    
    print("\n" + "=" * 60)
    print("🧠 Adaptive Workflow Control Demo")
    print("=" * 60)
    
    # Initialize orchestrator
    orchestrator = ParallelOrchestrator(
        max_workers=2,
        agent_registry=AgentRegistry(),
        enable_brainwave=True
    )
    
    print("📊 Demonstrating adaptive workflow control...")
    
    # Scenario 1: High focus - auto-start tasks
    print("\n🎯 Scenario 1: High Focus State")
    eeg_data = generate_mock_eeg_data()
    result = orchestrator.handle_brainwave_input(eeg_data)
    
    if result['action_taken'] and result['action_taken']['type'] == 'start_task':
        print("   ✅ Auto-started task due to high focus")
    
    # Scenario 2: Low focus/high stress - suggest break
    print("\n☕ Scenario 2: Fatigue Detection")
    # In a real scenario, this would be EEG data showing fatigue
    # For demo, we'll just call the method directly
    break_result = orchestrator.suggest_user_break(
        duration_minutes=10,
        break_type='stress_reduction'
    )
    print(f"   ✅ Suggested break: {break_result['message']}")
    
    # Scenario 3: High cognitive load - adjust priorities
    print("\n📉 Scenario 3: Cognitive Load Management")
    priority_result = orchestrator.adjust_task_priorities(
        target_load=0.6,
        reduction_factor=0.2
    )
    print(f"   ✅ Adjusted priorities: {priority_result['message']}")
    
    # Scenario 4: High confidence - auto-approve work
    print("\n👍 Scenario 4: Quality Assurance")
    approve_result = orchestrator.auto_approve_current_work(
        confidence=0.95
    )
    print(f"   ✅ Auto-approval: {approve_result['message']}")


def main():
    """Run the brainwave interface demonstration."""
    
    print("Brainwave Interface Integration Examples")
    print("=" * 60)
    print("This demonstrates how EEG brainwave data can be integrated")
    print("with AI agent orchestration for adaptive workflow control.")
    print()
    
    # Run basic demo
    orchestrator = brainwave_workflow_demo()
    
    # Run adaptive control demo
    brainwave_adaptive_workflow_demo()
    
    print("\n" + "=" * 60)
    print("🎉 Brainwave interface demonstration completed!")
    print("\nKey Benefits:")
    print("   • Real-time cognitive state monitoring")
    print("   • Adaptive workflow control")
    print("   • Automatic task prioritization")
    print("   • Stress detection and break suggestions")
    print("   • Quality assurance through confidence monitoring")
    print("   • Enhanced user productivity and well-being")


if __name__ == "__main__":
    main()