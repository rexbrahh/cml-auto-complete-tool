"""
Setup configuration for CML Auto-Complete Tool
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cml-auto-complete-tool",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A CLI tool that converts natural language to terminal commands using AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/cml-auto-complete-tool",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.1.7",
        "rich>=13.7.0",
        "openai>=1.12.0",
        "python-dotenv>=1.0.0",
        "prompt_toolkit>=3.0.43",
        "pyyaml>=6.0.1",
    ],
    entry_points={
        "console_scripts": [
            "cml-auto-complete-tool=cml_auto_complete_tool.cli:cli",
            "cact=cml_auto_complete_tool.cli:cli",
        ],
    },
    package_data={
        "cml_auto_complete_tool": ["py.typed"],
    },
    include_package_data=True,
) 