"""
Example demonstrating personalized experience integration with the AI agent orchestration system.

This example shows how to:
1. Initialize the orchestrator with personalized experience enabled
2. Create comprehensive personalized experience configurations
3. Update user profiles based on interactions
4. Adapt experiences based on cognitive state, UI preferences, and workflow context
5. Integrate brainwave data, predictive UI, and user feedback
"""

import time
from datetime import datetime
from orchestrator.parallel.orchestrator import ParallelOrchestrator
from orchestrator.agents.registry import AgentRegistry


def demonstrate_personalized_experience_creation(orchestrator):
    """Demonstrate creation of personalized experiences."""
    
    print("🎨 Demonstrating personalized experience creation...")
    
    # Create personalized experience
    result = orchestrator.create_personalized_experience()
    
    if result['status'] == 'success':
        personalized_exp = result['personalized_experience']
        components = result['components']
        
        print(f"Personalized Experience Configuration:")
        print(f"   • Cognitive Profile: {personalized_exp['cognitive_profile']['cognitive_style']}")
        print(f"   • Work Pattern: {personalized_exp['cognitive_profile']['work_pattern']}")
        print(f"   • Preferred Interaction: {personalized_exp['cognitive_profile']['preferred_interaction']}")
        print(f"   • Personalization Level: {personalized_exp['personalization_level']}")
        
        print(f"\nUI Settings:")
        ui_settings = personalized_exp['ui_settings']
        for key, value in ui_settings.items():
            print(f"   • {key}: {value}")
        
        print(f"\nWorkflow Adaptations:")
        for adaptation in personalized_exp['workflow_adaptations']:
            print(f"   • {adaptation}")
        
        print(f"\nComponents Used:")
        print(f"   • Brainwave Source: {components['brainwave']['source']}")
        print(f"   • UI Configuration: {len(components['ui'])} settings")
        print(f"   • User Insights: {components['user_insights'].get('interaction_count', 0)} interactions")
    else:
        print(f"   ❌ Failed to create personalized experience: {result.get('message', 'Unknown error')}")


def demonstrate_profile_updates(orchestrator):
    """Demonstrate user profile updates and personalization."""
    
    print("\n👥 Demonstrating user profile updates...")
    
    # Get initial personalization status
    status = orchestrator.get_personalization_status()
    print(f"Initial Cognitive Style: {status['user_profile']['cognitive_style']}")
    print(f"Initial Work Pattern: {status['user_profile']['work_pattern']}")
    
    # Update user profile
    profile_updates = {
        'cognitive_style': 'analytical',
        'work_pattern': 'intensive',
        'preferred_interaction': 'detailed_control',
        'adaptation_history': ['initial_setup']
    }
    
    update_result = orchestrator.update_personalized_profile(profile_updates)
    
    if update_result['status'] == 'success':
        print(f"   ✅ Profile updated successfully")
        
        # Get updated status
        updated_status = orchestrator.get_personalization_status()
        print(f"Updated Cognitive Style: {updated_status['user_profile']['cognitive_style']}")
        print(f"Updated Work Pattern: {updated_status['user_profile']['work_pattern']}")
        print(f"Adaptation Count: {updated_status['adaptation_count']}")
    else:
        print(f"   ❌ Failed to update profile")


def demonstrate_context_adaptive_personalization(orchestrator):
    """Demonstrate context-adaptive personalization."""
    
    print("\n🌍 Demonstrating context-adaptive personalization...")
    
    scenarios = [
        {
            'name': 'Morning Focus Session',
            'description': 'High focus, low stress, morning time',
            'expected': 'Analytical cognitive style with detailed UI'
        },
        {
            'name': 'Afternoon Workload',
            'description': 'Medium focus, medium stress, high workload',
            'expected': 'Balanced approach with workflow optimizations'
        },
        {
            'name': 'Evening Relaxation',
            'description': 'Low focus, low stress, evening time',
            'expected': 'Relaxed cognitive style with simplified UI'
        }
    ]
    
    for scenario in scenarios:
        print(f"\n--- {scenario['name']} ---")
        print(f"Description: {scenario['description']}")
        print(f"Expected: {scenario['expected']}")
        
        # Create personalized experience for this context
        result = orchestrator.create_personalized_experience()
        
        if result['status'] == 'success':
            exp_config = result['personalized_experience']
            
            print(f"Generated Experience:")
            print(f"   • Cognitive Style: {exp_config['cognitive_profile']['cognitive_style']}")
            print(f"   • Work Pattern: {exp_config['cognitive_profile']['work_pattern']}")
            print(f"   • UI Color Scheme: {exp_config['ui_settings'].get('color_scheme', 'default')}")
            print(f"   • Information Density: {exp_config['ui_settings'].get('information_density', 'medium')}")
            print(f"   • Adaptations: {len(exp_config['workflow_adaptations'])} workflow adaptations")
        else:
            print(f"   ❌ Failed to create experience for this scenario")
        
        time.sleep(0.5)


def demonstrate_integration_with_other_systems(orchestrator):
    """Demonstrate integration with brainwave and predictive UI systems."""
    
    print("\n🔗 Demonstrating integration with other systems...")
    
    # Check if brainwave interface is available
    brainwave_status = orchestrator.get_brainwave_status()
    print(f"Brainwave Interface: {'Enabled' if brainwave_status.get('enabled', False) else 'Disabled'}")
    
    # Check if predictive UI is available
    predictive_ui_status = orchestrator.get_predictive_ui_status()
    print(f"Predictive UI: {'Enabled' if predictive_ui_status.get('enabled', False) else 'Disabled'}")
    
    # Create personalized experience that integrates both
    result = orchestrator.create_personalized_experience()
    
    if result['status'] == 'success':
        components = result['components']
        
        print(f"\nIntegration Results:")
        print(f"   • Brainwave Data Source: {components['brainwave']['source']}")
        print(f"   • Cognitive State: Focus={components['brainwave']['cognitive_state']['focus_level']:.2f}")
        print(f"   • UI Configuration Source: {'Predictive UI' if components['ui'] else 'Default'}")
        print(f"   • User Insights: {components['user_insights'].get('interaction_count', 0)} interactions analyzed")
        
        # Show how the integration affects the final experience
        exp_config = result['personalized_experience']
        print(f"\nFinal Integrated Experience:")
        print(f"   • Cognitive Profile: {exp_config['cognitive_profile']['cognitive_style']}")
        print(f"   • UI Adaptations: {len(exp_config.get('ui_adaptations', {}))} adaptations")
        print(f"   • Workflow Adaptations: {len(exp_config['workflow_adaptations'])} adaptations")
        print(f"   • Interaction Adaptations: {len(exp_config.get('interaction_adaptations', {}))} adaptations")


def demonstrate_personalization_lifecycle(orchestrator):
    """Demonstrate complete personalization lifecycle."""
    
    print("\n🔄 Demonstrating complete personalization lifecycle...")
    
    # Step 1: Initial personalization
    print("\n1. Initial Personalization:")
    initial_result = orchestrator.create_personalized_experience()
    if initial_result['status'] == 'success':
        initial_style = initial_result['personalized_experience']['cognitive_profile']['cognitive_style']
        print(f"   ✅ Initial cognitive style: {initial_style}")
    
    # Step 2: Update profile based on user behavior
    print("\n2. Updating Profile Based on Behavior:")
    behavior_updates = {
        'cognitive_style': 'focused',
        'work_pattern': 'active',
        'preferred_interaction': 'efficient_control'
    }
    update_result = orchestrator.update_personalized_profile(behavior_updates)
    if update_result['status'] == 'success':
        print(f"   ✅ Profile updated to reflect user behavior")
    
    # Step 3: Adapted personalization
    print("\n3. Adapted Personalization:")
    adapted_result = orchestrator.create_personalized_experience()
    if adapted_result['status'] == 'success':
        adapted_style = adapted_result['personalized_experience']['cognitive_profile']['cognitive_style']
        print(f"   ✅ Adapted cognitive style: {adapted_style}")
        
        # Show differences
        if initial_result['status'] == 'success' and initial_style != adapted_style:
            print(f"   📊 Personalization adapted from '{initial_style}' to '{adapted_style}'")
    
    # Step 4: Continuous improvement
    print("\n4. Continuous Improvement:")
    status = orchestrator.get_personalization_status()
    print(f"   ✅ Adaptation count: {status['adaptation_count']}")
    print(f"   ✅ Current cognitive style: {status['user_profile']['cognitive_style']}")
    print(f"   ✅ Current work pattern: {status['user_profile']['work_pattern']}")


def main():
    """Run the personalized experience demonstration."""
    
    print("Personalized Experience Integration Examples")
    print("=" * 60)
    print("This demonstrates how personalized experiences integrate")
    print("brainwave data, predictive UI, and user preferences to")
    print("create tailored agent interactions.")
    print()
    
    # Initialize orchestrator with all personalized features
    print("🔧 Initializing orchestrator with personalized experience...")
    orchestrator = ParallelOrchestrator(
        max_workers=4,
        agent_registry=AgentRegistry(),
        enable_brainwave=True,
        enable_predictive_ui=True,
        enable_personalized_experience=True
    )
    
    # Check status
    status = orchestrator.get_personalization_status()
    print(f"✅ Personalized experience status: {status}")
    
    # Run demonstrations
    demonstrate_personalized_experience_creation(orchestrator)
    demonstrate_profile_updates(orchestrator)
    demonstrate_context_adaptive_personalization(orchestrator)
    demonstrate_integration_with_other_systems(orchestrator)
    demonstrate_personalization_lifecycle(orchestrator)
    
    print("\n" + "=" * 60)
    print("🎉 Personalized experience demonstration completed!")
    print("\nKey Benefits:")
    print("   • Holistic user experience personalization")
    print("   • Cognitive state-aware adaptations")
    print("   • Context-sensitive workflow optimizations")
    print("   • Continuous learning and improvement")
    print("   • Multi-system integration (brainwave + predictive UI)")
    print("   • Adaptive interaction patterns")
    print("\nUse Cases:")
    print("   • Personalized agent assistants")
    print("   • Cognitive workload management")
    print("   • Adaptive learning systems")
    print("   • Intelligent productivity tools")
    print("   • Accessibility enhancements")
    print("   • User behavior analysis and optimization")


if __name__ == "__main__":
    main()