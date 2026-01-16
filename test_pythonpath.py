#!/usr/bin/env python3
"""
Test script to verify PYTHONPATH configuration for src directory.
"""

import sys
import os

def test_pythonpath():
    """Test that src directory is accessible via PYTHONPATH."""
    
    # Add src directory to Python path if not already present
    src_path = "/workspace/src"
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
        print(f"Added {src_path} to PYTHONPATH")
    
    # Test importing from src directory
    try:
        import orchestrator
        print("✓ Successfully imported orchestrator module")
        
        import orchestrator.cli
        print("✓ Successfully imported orchestrator.cli module")
        
        # Try to import other modules from src
        import validate_schema
        print("✓ Successfully imported validate_schema module")
        
        print("\n🎉 All imports successful! PYTHONPATH is correctly configured.")
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("\n🔧 Please ensure PYTHONPATH includes /workspace/src")
        return False

if __name__ == "__main__":
    test_pythonpath()