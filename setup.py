"""
Setup script for agent-delegate orchestration system.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "CLAUDE.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="agent-delegate",
    version="0.1.0",
    description="Multi-agent orchestration system using OpenHands SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Agent-Delegate Project",
    python_requires=">=3.10",
    packages=find_packages(where="src", exclude=["tests", "tests.*"]),
    package_dir={"": "src"},
    install_requires=[
        "openhands-sdk>=1.8.1",
        "openhands-tools",
        "PyYAML>=6.0.0",
        "jsonschema>=4.26.0",
        "click>=8.3.0",
        "pydantic>=2.9.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.3.0",
            "pytest-cov>=5.0.0",
            "black>=24.8.0",
            "ruff>=0.7.0",
            "mypy>=1.11.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "agent-delegate=orchestrator.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
