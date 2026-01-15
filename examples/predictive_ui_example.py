"""
Example demonstrating predictive UI integration with the AI agent orchestration system.

This example shows how to:
1. Initialize the orchestrator with predictive UI enabled
2. Get optimal UI configurations based on context
3. Record user interactions for pattern analysis
4. Adapt UI based on cognitive state and workflow context
5. Manage user preferences and get insights
"""

import time
from datetime import datetime
from orchestrator.parallel.orchestrator import ParallelOrchestrator
from orchestrator.agents.registry import AgentRegistry


def simulate_user_interactions(orchestrator, num_interactions=10):
    """Simulate user interactions for pattern analysis."""
    
    print("👤 Simulating user interactions...")
    
    interaction_types = ['click', 'scroll', 'hover', 'select', 'input']
    features = ['task_list', 'dashboard', 'settings', 'search', 'notification']
    themes = ['light', 'dark', 'system']
    layouts = ['compact', 'spacious', 'auto']
    
    for i in range(num_interactions):
        interaction_data = {
            'action_type': interaction_types[i % len(interaction_types)],
            'feature': features[i % len(features)],
            'ui_theme': themes[i % len(themes)],
            'layout_type': layouts[i % len(layouts)],
            'timestamp': datetime.now().isoformat(),
            'features_used': [features[i % len(features)], 'common_feature'],
            'session_id': 'demo_session_001'
        }
        
        # Record the interaction
        result = orchestrator.record_user_interaction(interaction_data)
        
        if result['status'] == 'success':
            print(f"   ✓ Recorded interaction {i+1}: {interaction_data['action_type']} on {interaction_data['feature']}")
        else:
            print(f"   ✗ Failed to record interaction {i+1}")
        
        time.sleep(0.1)
    
    print(f"   ✅ Completed {num_interactions} user interactions")


def demonstrate_context_adaptive_ui(orchestrator):
    """Demonstrate UI adaptation to different contexts."""
    
    print("\n🎨 Demonstrating context-adaptive UI...")
    
    scenarios = [
        {
            'name': 'Initial Setup',
            'description': 'No tasks, starting fresh',
            'expected': 'Spacious layout, medium information density'
        },
        {
            'name': 'Light Workload',
            'description': 'Few tasks, normal cognitive state',
            'expected': 'Balanced UI for productivity'
        },
        {
            'name': 'Heavy Workload',
            'description': 'Many tasks, high cognitive load',
            'expected': 'Compact layout, high information density'
        },
        {
            'name': 'Stress Detection',
            'description': 'High stress levels detected',
            'expected': 'Calm color scheme, low information density'
        }
    ]
    
    for scenario in scenarios:
        print(f"\n--- {scenario['name']} ---")
        print(f"Description: {scenario['description']}")
        print(f"Expected: {scenario['expected']}")
        
        # Get optimal UI configuration
        result = orchestrator.get_optimal_ui_configuration()
        
        if result['status'] == 'success':
            ui_config = result['ui_configuration']
            cognitive_state = result['cognitive_state']
            workflow_context = result['workflow_context']
            
            print(f"Recommended UI Configuration:")
            print(f"   • Color Scheme: {ui_config.get('color_scheme', 'default')}")
            print(f"   • Information Density: {ui_config.get('information_density', 'medium')}")
            print(f"   • Layout Compactness: {ui_config.get('layout_compactness', 'default')}")
            print(f"   • Animation Speed: {ui_config.get('animation_speed', 'normal')}")
            print(f"   • Brightness: {ui_config.get('brightness', 'medium')}")
            
            print(f"Based on:")
            print(f"   • Cognitive State: Focus={cognitive_state.get('focus_level', 0):.2f}, "
                  f"Stress={cognitive_state.get('stress_level', 0):.2f}")
            print(f"   • Workflow Context: {workflow_context.get('task_load', 0)} tasks pending")
        else:
            print(f"   ❌ Failed to get UI configuration: {result.get('message', 'Unknown error')}")
        
        time.sleep(0.5)


def demonstrate_user_preferences(orchestrator):
    """Demonstrate user preference management."""
    
    print("\n👥 Demonstrating user preference management...")
    
    # Get initial preferences
    insights = orchestrator.get_user_insights()
    if insights['status'] == 'success':
        initial_prefs = insights['user_profile']['preferences']
        print(f"Initial Preferences:")
        for key, value in initial_prefs.items():
            print(f"   • {key}: {value}")
    
    # Update preferences
    new_preferences = {
        'ui_theme': 'dark',
        'color_scheme': 'vibrant',
        'font_size': 'large',
        'animation_speed': 'fast'
    }
    
    print(f"\nUpdating preferences...")
    update_result = orchestrator.update_user_preferences(new_preferences)
    
    if update_result['status'] == 'success':
        print(f"   ✅ Preferences updated successfully")
        
        # Get updated preferences
        updated_insights = orchestrator.get_user_insights()
        if updated_insights['status'] == 'success':
            updated_prefs = updated_insights['user_profile']['preferences']
            print(f"Updated Preferences:")
            for key, value in updated_prefs.items():
                print(f"   • {key}: {value}")
    else:
        print(f"   ❌ Failed to update preferences")


def demonstrate_user_insights(orchestrator):
    """Demonstrate user insights and pattern analysis."""
    
    print("\n📊 Demonstrating user insights and pattern analysis...")
    
    # Get user insights
    result = orchestrator.get_user_insights()
    
    if result['status'] == 'success':
        insights = result['interaction_insights']
        profile = result['user_profile']
        
        print(f"User Interaction Insights:")
        print(f"   • Total Interactions: {insights.get('interaction_count', 0)}")
        
        if insights.get('frequent_actions'):
            print(f"   • Most Frequent Actions:")
            for action in insights['frequent_actions'][:3]:
                print(f"     - {action['action']}: {action['count']} times")
        
        if insights.get('feature_usage'):
            print(f"   • Feature Usage:")
            for feature, count in list(insights['feature_usage']['feature_usage_distribution'].items())[:3]:
                print(f"     - {feature}: {count} uses")
        
        print(f"\nUser Profile Information:")
        print(f"   • User ID: {profile.get('user_id', 'unknown')}")
        print(f"   • Total Sessions: {profile.get('usage_statistics', {}).get('total_sessions', 0)}")
        print(f"   • Total Interactions: {profile.get('usage_statistics', {}).get('total_interactions', 0)}")
        
        if profile.get('behavioral_patterns'):
            print(f"   • Behavioral Patterns:")
            for pattern, count in list(profile['behavioral_patterns'].items())[:3]:
                print(f"     - {pattern}: {count} occurrences")
    else:
        print(f"   ❌ Failed to get user insights")


def demonstrate_predictive_ui_workflow(orchestrator):
    """Demonstrate predictive UI in a complete workflow."""
    
    print("\n🚀 Demonstrating predictive UI in complete workflow...")
    
    # Submit some tasks to create workflow context
    print("Submitting workflow tasks...")
    task_ids = []
    
    for i in range(5):
        task_id = orchestrator.submit_task(
            agent_type=f"example_agent_{i}",
            payload={
                "task": f"Example Task {i+1}",
                "priority": "medium" if i < 3 else "high"
            },
            priority="medium" if i < 3 else "high"
        )
        task_ids.append(task_id)
        print(f"   ✓ Submitted task {task_id}")
    
    # Get UI configuration for the workflow
    print(f"\nGetting optimal UI configuration for workflow...")
    ui_result = orchestrator.get_optimal_ui_configuration()
    
    if ui_result['status'] == 'success':
        ui_config = ui_result['ui_configuration']
        print(f"Recommended UI for workflow execution:")
        print(f"   • Color Scheme: {ui_config.get('color_scheme', 'default')}")
        print(f"   • Layout: {ui_config.get('layout_compactness', 'default')}")
        print(f"   • Information Density: {ui_config.get('information_density', 'medium')}")
        print(f"   • Animation: {ui_config.get('animation_speed', 'normal')}")
    
    # Simulate user interactions during workflow
    print(f"\nSimulating user interactions during workflow...")
    simulate_user_interactions(orchestrator, num_interactions=5)
    
    # Get updated UI configuration after interactions
    print(f"\nGetting updated UI configuration after user interactions...")
    updated_ui_result = orchestrator.get_optimal_ui_configuration()
    
    if updated_ui_result['status'] == 'success':
        updated_ui_config = updated_ui_result['ui_configuration']
        print(f"Updated UI recommendations:")
        print(f"   • Color Scheme: {updated_ui_config.get('color_scheme', 'default')}")
        print(f"   • Layout: {updated_ui_config.get('layout_compactness', 'default')}")
        print(f"   • Information Density: {updated_ui_config.get('information_density', 'medium')}")
    
    # Get final user insights
    print(f"\nGetting final user insights...")
    final_insights = orchestrator.get_user_insights()
    
    if final_insights['status'] == 'success':
        interaction_count = final_insights['interaction_insights']['interaction_count']
        print(f"   ✅ Total interactions recorded: {interaction_count}")


def main():
    """Run the predictive UI demonstration."""
    
    print("Predictive UI Integration Examples")
    print("=" * 60)
    print("This demonstrates how predictive UI adapts to user behavior,")
    print("cognitive state, and workflow context for optimal experience.")
    print()
    
    # Initialize orchestrator with predictive UI enabled
    print("🔧 Initializing orchestrator with predictive UI...")
    orchestrator = ParallelOrchestrator(
        max_workers=4,
        agent_registry=AgentRegistry(),
        enable_predictive_ui=True
    )
    
    # Check predictive UI status
    status = orchestrator.get_predictive_ui_status()
    print(f"✅ Predictive UI status: {status}")
    
    # Run demonstrations
    simulate_user_interactions(orchestrator)
    demonstrate_context_adaptive_ui(orchestrator)
    demonstrate_user_preferences(orchestrator)
    demonstrate_user_insights(orchestrator)
    demonstrate_predictive_ui_workflow(orchestrator)
    
    print("\n" + "=" * 60)
    print("🎉 Predictive UI demonstration completed!")
    print("\nKey Benefits:")
    print("   • Context-aware UI adaptation")
    print("   • Cognitive state-based optimization")
    print("   • Personalized user experience")
    print("   • Behavioral pattern learning")
    print("   • Workflow-optimized interfaces")
    print("   • Continuous improvement through interaction analysis")
    print("\nUse Cases:")
    print("   • Adaptive dashboards")
    print("   • Intelligent task management")
    print("   • Personalized workflows")
    print("   • Cognitive load optimization")
    print("   • Accessibility enhancements")


if __name__ == "__main__":
    main()