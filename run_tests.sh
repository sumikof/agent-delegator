#!/bin/bash

echo "Running unit tests..."
pytest tests/unit/ -v --tb=short

echo "Running integration tests..."
pytest tests/integration/ -v --tb=short

echo "Running performance tests..."
pytest tests/performance/ -v --tb=short --benchmark-autosave=true

echo "Generating coverage report..."
pytest --cov=orchestrator --cov-report=html:coverage_report