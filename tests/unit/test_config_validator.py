"""Unit tests for ConfigValidator."""

import pytest
import unittest
from orchestrator.config.validator import ConfigValidator


@unittest.skip("Schema validation requires schema files which are not available in test environment")
def test_validate_workflow():
    """Test validating a workflow configuration."""
    validator = ConfigValidator()
    
    # Test with a valid workflow configuration
    valid_workflow_config = {
        "version": "1.0",
        "project": {
            "name": "Test Project",
            "type": "test",
            "description": "Test project",
            "language_policy": {
                "customer_facing": "en",
                "development": "en",
                "documentation": "en",
                "code_comments": "en",
                "commit_messages": "en"
            }
        },
        "agents": {
            "include_templates": ["core"]
        },
        "workflow": {
            "global_timeout_ms": 300000,
            "stages": [
                {
                    "name": "test-stage",
                    "description": "Test stage",
                    "agents": ["client-liaison"],
                    "execution_mode": "sequential",
                    "timeout_ms": 60000
                }
            ],
            "error_handling": {
                "retry_policy": {
                    "max_attempts": 2,
                    "backoff_type": "exponential",
                    "initial_delay_ms": 1000,
                    "max_delay_ms": 10000,
                    "multiplier": 2.0,
                    "jitter": True,
                    "jitter_factor": 0.1
                },
                "circuit_breaker": {
                    "enabled": True,
                    "failure_threshold": 3,
                    "success_threshold": 2,
                    "recovery_timeout_ms": 30000
                },
                "fallback_strategies": [
                    {
                        "condition": "max_retries_exceeded",
                        "action": "escalate_to_orchestrator"
                    }
                ]
            }
        }
    }
    
    # Should validate successfully
    is_valid, errors = validator.validate_workflow(valid_workflow_config)
    assert is_valid
    assert len(errors) == 0


@unittest.skip("Agent validation requires schema files which are not available in test environment")
def test_validate_agent():
    """Test validating an agent configuration."""
    validator = ConfigValidator()
    
    # Test with a valid agent configuration
    valid_agent_config = {
        "id": "test-agent",
        "name": "Test Agent",
        "description": "Agent for testing",
        "type": "core",
        "capabilities": ["testing"],
        "interface": {
            "input_schema": {
                "type": "object",
                "properties": {
                    "test_input": {"type": "string"}
                }
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "test_output": {"type": "string"}
                }
            }
        }
    }
    
    # Should validate successfully
    is_valid, errors = validator.validate_agent(valid_agent_config)
    assert is_valid
    assert len(errors) == 0
