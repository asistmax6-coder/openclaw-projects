# Whisper Transcription Service Makefile

.PHONY: install test run-dev build-docker deploy clean lint format

install:
	@echo "🎤 Installing Whishes Transcription Service..."
	@./install.sh

test:
	@echo "🧪 Running tests..."
	@./venv/bin/python -m pytest tests/ -v

test-coverage:
	@echo "📊 Running tests with coverage..."
	@./venv/bin/python -m pytest tests/ --cov=. --cov-report=html

dev:
	@echo "🚀 Starting development server..."
	@./venv/bin/uvicorn web_service:app --reload

run-cli:
	@echo "📋 Testing CLI with sample..."
	@./venv/bin/python transcribe.py examples/sample.ogg --language en --format json

build:
	@echo "🏗️  Building Docker image..."
	@docker build -t whisper-service:latest .

run-docker:
	@echo "🐳 Running Docker container..."
	@docker run -p 8000:8000 -e OPENAI_API_KEY=$(OPENAI_API_KEY) --rm whisper-service:latest

deploy:
	@echo "🚀 Deploying to Heroku..."
	@echo "Note: Requires heroku-cli and OPENAI_API_KEY config"

lint:
	@echo "🔍 Running linter..."
	@./venv/bin/python -m flake8 *.py tests/ --max-line-length=88 --ignore=E501,W503

format:
	@echo "✨ Formatting code..."
	@./venv/bin/python -m black *.py tests/

clean:
	@echo "🧹 Cleaning up..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

demo: clean install
	@echo "🎯 Running complete demo..."
	@make test
	make run-cli

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make test       - Run all tests"
	@echo "  make dev        - Start development server"
	@echo "  make build      - Build Docker image"
	@echo "  make run-docker - Run Docker container"
	@echo "  make clean      - Clean up files"
	@echo "  make demo       - Complete demo run"