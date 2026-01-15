"""
Test cases for evolutionary learning system
"""

import pytest
from unittest.mock import Mock
from orchestrator.self_organizing.evolutionary import (
    EvolutionaryLearningSystem, 
    AdaptationExperience, 
    EvolvedStrategy
)


def test_evolutionary_learning_system_initialization():
    """Test EvolutionaryLearningSystem initialization"""
    system = EvolutionaryLearningSystem(max_experiences=100, population_size=20)
    
    assert system.max_experiences == 100
    assert system.population_size == 20
    assert system.generation == 0
    assert len(system.experience_history) == 0
    assert len(system.strategy_population) == 20
    assert len(system.knowledge_base) == 0


def test_adaptation_experience_creation():
    """Test AdaptationExperience creation"""
    experience = AdaptationExperience(
        strategy={"name": "test_strategy", "parameters": {"param1": 0.5}},
        context={"agent_count": 5, "task_load": 0.8},
        result={"status": "success", "performance_improvement": 0.15},
        timestamp=1234567890.0,
        performance_improvement=0.15
    )
    
    assert experience.strategy["name"] == "test_strategy"
    assert experience.context["agent_count"] == 5
    assert experience.result["status"] == "success"
    assert experience.performance_improvement == 0.15


def test_record_adaptation_experience():
    """Test recording adaptation experience"""
    system = EvolutionaryLearningSystem(population_size=10)
    
    # Record an experience
    system.record_adaptation_experience(
        strategy={"name": "role_swap", "parameters": {"swap_probability": 0.3}},
        context={"agent_count": 5, "task_load": 0.8},
        result={"status": "success", "performance_improvement": 0.15},
        performance_improvement=0.15
    )
    
    # Check that experience was recorded
    assert len(system.experience_history) == 1
    assert len(system.knowledge_base) == 1
    assert "role_swap" in system.knowledge_base
    
    # Check knowledge base content
    knowledge = system.knowledge_base["role_swap"]
    assert knowledge["total_experiences"] == 1
    assert knowledge["success_count"] == 1
    assert knowledge["total_improvement"] == 0.15


def test_evolve_strategies():
    """Test evolving strategies"""
    system = EvolutionaryLearningSystem(population_size=10)
    
    # Record some experiences to build knowledge base
    for i in range(5):
        system.record_adaptation_experience(
            strategy={"name": "role_swap", "parameters": {"swap_probability": 0.3}},
            context={"agent_count": 5, "task_load": 0.8},
            result={"status": "success", "performance_improvement": 0.1 + i * 0.02},
            performance_improvement=0.1 + i * 0.02
        )
    
    # Evolve strategies
    new_population = system.evolve_strategies()
    
    # Check that new generation was created
    assert system.generation == 1
    assert len(new_population) == 10
    
    # Check that all strategies have updated generation
    for strategy in new_population:
        assert strategy.generation == 1


def test_get_best_strategy():
    """Test getting best strategy"""
    system = EvolutionaryLearningSystem(population_size=5)
    
    # Record experiences for different strategies
    for strategy_name in ["role_swap", "load_balancing", "capability_matching"]:
        for i in range(3):
            system.record_adaptation_experience(
                strategy={"name": strategy_name, "parameters": {}},
                context={"agent_count": 5, "task_load": 0.8},
                result={"status": "success", "performance_improvement": 0.1 + i * 0.05},
                performance_improvement=0.1 + i * 0.05
            )
    
    # Get best strategy
    best_strategy = system.get_best_strategy()
    
    assert best_strategy is not None
    assert best_strategy.fitness_score > 0


def test_get_strategy_population():
    """Test getting strategy population"""
    system = EvolutionaryLearningSystem(population_size=8)
    
    population = system.get_strategy_population()
    
    assert len(population) == 8
    assert all(isinstance(s, EvolvedStrategy) for s in population)


def test_get_knowledge_base():
    """Test getting knowledge base"""
    system = EvolutionaryLearningSystem(population_size=5)
    
    # Record some experiences
    system.record_adaptation_experience(
        strategy={"name": "test_strategy", "parameters": {"param1": 0.5}},
        context={"agent_count": 5, "task_load": 0.8, "context_param": "value1"},
        result={"status": "success", "performance_improvement": 0.2},
        performance_improvement=0.2
    )
    
    knowledge_base = system.get_knowledge_base()
    
    assert "test_strategy" in knowledge_base
    assert knowledge_base["test_strategy"]["total_experiences"] == 1
    assert knowledge_base["test_strategy"]["success_count"] == 1


def test_get_generation():
    """Test getting current generation"""
    system = EvolutionaryLearningSystem(population_size=5)
    
    assert system.get_generation() == 0
    
    # Evolve strategies
    system.evolve_strategies()
    
    assert system.get_generation() == 1


def test_get_experience_history():
    """Test getting experience history"""
    system = EvolutionaryLearningSystem(max_experiences=3, population_size=5)
    
    # Record some experiences
    for i in range(5):
        system.record_adaptation_experience(
            strategy={"name": f"strategy_{i}", "parameters": {}},
            context={"agent_count": 5, "task_load": 0.8},
            result={"status": "success", "performance_improvement": 0.1},
            performance_improvement=0.1
        )
    
    # Check that history is limited to max_experiences
    history = system.get_experience_history()
    assert len(history) == 3  # max_experiences is 3
    assert all(isinstance(exp, AdaptationExperience) for exp in history)


def test_context_aware_strategy_selection():
    """Test context-aware strategy selection"""
    system = EvolutionaryLearningSystem(population_size=5)
    
    # Record experiences with different contexts
    contexts = [
        {"agent_count": 5, "task_load": 0.8, "context_type": "high_load"},
        {"agent_count": 3, "task_load": 0.3, "context_type": "low_load"},
        {"agent_count": 10, "task_load": 0.9, "context_type": "very_high_load"}
    ]
    
    for i, context in enumerate(contexts):
        for j in range(3):
            system.record_adaptation_experience(
                strategy={"name": f"strategy_{i}", "parameters": {}},
                context=context,
                result={"status": "success", "performance_improvement": 0.1 + j * 0.05},
                performance_improvement=0.1 + j * 0.05
            )
    
    # Test context-aware selection
    high_load_context = {"agent_count": 8, "task_load": 0.85, "context_type": "high_load"}
    best_strategy = system.get_best_strategy(high_load_context)
    
    assert best_strategy is not None
    # The strategy should be one that performed well in similar contexts


def test_evolutionary_learning_with_multiple_generations():
    """Test evolutionary learning over multiple generations"""
    system = EvolutionaryLearningSystem(population_size=5)
    
    initial_generation = system.get_generation()
    initial_population = system.get_strategy_population()
    
    # Evolve through multiple generations
    for i in range(3):
        # Record some experiences
        for j in range(2):
            system.record_adaptation_experience(
                strategy={"name": f"strategy_{i}_{j}", "parameters": {"param": 0.5}},
                context={"agent_count": 5, "task_load": 0.8},
                result={"status": "success", "performance_improvement": 0.1 + j * 0.05},
                performance_improvement=0.1 + j * 0.05
            )
        
        # Evolve to next generation
        system.evolve_strategies()
    
    # Check that generation advanced
    assert system.get_generation() == initial_generation + 3
    
    # Check that population evolved
    final_population = system.get_strategy_population()
    assert len(final_population) == len(initial_population)
    
    # Check that strategies have higher generations
    final_generations = [s.generation for s in final_population]
    assert all(g >= initial_generation + 1 for g in final_generations)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])