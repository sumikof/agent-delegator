"""Unit tests for ConfigValidator."""

import unittest
from orchestrator.config.validator import ConfigValidator


class TestConfigValidator(unittest.TestCase):
    
    def test_validate_workflow(self):
        """Test validating a workflow configuration."""
        validator = ConfigValidator()

        # Test with a valid workflow configuration
        valid_workflow_config = {
            "version": "1.0",
            "project": {
                "name": "Test Project",
                "type": "web",  # Changed from 'test' to valid type
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
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_validate_workflow_invalid(self):
        """Test validating an invalid workflow configuration."""
        validator = ConfigValidator()

        # Test with an invalid workflow configuration (invalid project type)
        invalid_workflow_config = {
            "version": "1.0",
            "project": {
                "name": "Test Project",
                "type": "invalid-type",  # Invalid project type
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

        # Should fail validation
        is_valid, errors = validator.validate_workflow(invalid_workflow_config)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("invalid-type" in error for error in errors))

    def test_validate_agent(self):
        """Test validating an agent configuration."""
        validator = ConfigValidator()

        # Test with a valid agent configuration
        valid_agent_config = {
            "id": "test-agent",
            "name": "Test Agent",
            "description": "Agent for testing",
            "type": "core",
            "role": "testing",  # Added required field
            "responsibilities": {  # Added required field with correct structure
                "must_do": ["execute tests"],
                "must_not_do": ["modify production code"]
            },
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
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_validate_agent_invalid(self):
        """Test validating an invalid agent configuration."""
        validator = ConfigValidator()

        # Test with an invalid agent configuration (missing required fields)
        invalid_agent_config = {
            "id": "test-agent",
            "name": "Test Agent",
            "description": "Agent for testing",
            "type": "core",
            # Missing required fields: role, responsibilities
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

        # Should fail validation
        is_valid, errors = validator.validate_agent(invalid_agent_config)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("required property" in error for error in errors))


if __name__ == '__main__':
    unittest.main()