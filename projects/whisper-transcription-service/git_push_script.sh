#!/bin/bash
# Complete deployment script for Whisper Transcription Service

set -e

REPO_NAME="whisper-transcription-service"
REMOTE_URL="git@github.com:your-username/${REPO_NAME}.git"

echo "🎤 Setting up Git repository for ${REPO_NAME}..."

# Initialize git if not already done
if [ ! -d .git ]; then
    git init
fi

# Add all files
git add .

# Initial commit
git commit -m "Initial commit: Complete Whisper transcription service

- CLI tool with batch processing
- FastAPI web service
- Docker support
- Comprehensive testing
- Production-ready deployment scripts
- OpenAI integration
- Multi-format audio support"