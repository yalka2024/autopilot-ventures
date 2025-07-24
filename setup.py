"""
Setup script for AutoPilot Ventures Platform
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="autopilot-ventures",
    version="1.0.0",
    author="AutoPilot Ventures Team",
    author_email="team@autopilotventures.com",
    description="Multilingual AI Agent Platform for Autonomous Business Operations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/autopilot-ventures/platform",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "multilingual": [
            "polyglot>=16.7.4",
            "langdetect>=1.0.9",
            "googletrans==4.0.0rc1",
            "sentencepiece>=0.1.99",
            "sacremoses>=0.0.53",
        ],
    },
    entry_points={
        "console_scripts": [
            "autopilot-ventures=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.json", "*.txt", "*.md"],
    },
) 