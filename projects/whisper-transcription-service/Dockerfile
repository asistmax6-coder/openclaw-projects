# Multi-stage build for Whisper Transcription Service
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libbz2-dev \
    libffi-dev \
    liblzma-dev \
    libsqlite3-dev \
    libssl-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

# Install runtime dependencies (including ffmpeg for audio processing)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY transcribe.py web_service.py ./
COPY requirements.txt ./

# Create non-root user
RUN useradd -m -u 1000 whisper && chown -R whisper:whisper /app
USER whisper

# Expose port
EXPOSE 8000

# Default to web service
CMD ["python", "-m", "uvicorn", "web_service:app", "--host", "0.0.0.0", "--port", "8000"]