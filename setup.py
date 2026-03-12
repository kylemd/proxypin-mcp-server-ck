#!/usr/bin/env python3
"""
ProxyPin MCP Server - Enhanced Edition
Setup configuration
"""

from setuptools import setup, find_packages
import os

def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="proxypin-mcp-server-chuankangkk",
    version="2.0.0",
    author="ChuanKangKK",
    author_email="2040168455@qq.com",
    description="ProxyPin MCP Server (Enhanced) - High-performance HTTP request capture and analysis tool",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/1837620622/proxypin-mcp-server",
    project_urls={
        "Bug Tracker": "https://github.com/1837620622/proxypin-mcp-server/issues",
        "Documentation": "https://github.com/1837620622/proxypin-mcp-server/blob/main/README.md",
        "Source Code": "https://github.com/1837620622/proxypin-mcp-server",
    },
    packages=find_packages(),
    py_modules=["proxypin_mcp_server"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Networking :: Monitoring",
        "Topic :: Utilities",
    ],
    python_requires=">=3.10",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "proxypin-mcp-server=proxypin_mcp_server:main",
            "proxypin-mcp=proxypin_mcp_server:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.md", "*.yml", "*.yaml"],
    },
    zip_safe=False,
    keywords=[
        "proxypin", "mcp", "server", "http", "proxy", "capture", "analysis",
        "network", "monitoring", "debugging"
    ],
    license="MIT",
)
