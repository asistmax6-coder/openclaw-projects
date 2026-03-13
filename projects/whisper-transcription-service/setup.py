#!/usr/bin/env python3
"""
Setup script for Whisper Transcription Service
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="whisper-transcription-service",
    version="1.0.0",
    author="Max",
    author_email="max@openclaw.ai",
    description="Audio transcription service using OpenAI Whisper API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/asistmax6-coder/whisper-transcription-service",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "whisper-transcribe=transcribe:main",
            "whisper-api=web_service:main",
        ],
    },
    include_package_data=True,
)