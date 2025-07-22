#!/usr/bin/env python3
"""
Social Media Agent System Setup
"""

from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="social-media-agent",
    version="1.0.0",
    author="Manus AI",
    author_email="contact@manus.ai",
    description="An open-source, AI-powered social media management system with autonomous agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/social-media-agent",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Communications",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Scheduling",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "pytest-cov>=4.1.0",
            "black>=23.11.0",
            "flake8>=6.1.0",
            "mypy>=1.7.1",
            "pre-commit>=3.6.0",
        ],
        "dashboard": [
            "streamlit>=1.28.0",
            "plotly>=5.17.0",
            "dash>=2.14.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "social-media-agent=main:main",
            "sma-dashboard=dashboard.app:main",
            "sma-config=config.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.json", "*.txt", "*.md"],
    },
    zip_safe=False,
    keywords="social media, automation, ai, agents, content generation, marketing",
    project_urls={
        "Bug Reports": "https://github.com/your-org/social-media-agent/issues",
        "Source": "https://github.com/your-org/social-media-agent",
        "Documentation": "https://social-media-agent.readthedocs.io/",
    },
)

