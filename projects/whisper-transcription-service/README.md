# Whisper Transcription Service

Complete audio transcription service built with Python and OpenAI Whisper API, specifically designed to process .ogg files and other audio formats.

## Features

- 📁 **Multi-format support**: .ogg, .mp3, .wav, .m4a, .flac, .webm
- 🚀 **CLI and Web API**: Command-line tool and FastAPI web service
- ⚡ **Async processing**: Background job handling with parallel processing
- 🔧 **Docker ready**: Containerized deployment with docker-compose
- 📊 **Detailed output**: Verbose JSON with timestamps, confidence scores
- 🌍 **Multi-language**: Support for 50+ languages
- 🔒 **Error handling**: Robust error detection and logging

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/asistmax6-coder/whisper-transcription-service.git
cd whisper-transcription-service

# Install dependencies
pip install -r requirements.txt

# Or install as package
pip install -e .
```

### 2. Configuration

Set your OpenAI API key:

```bash
export OPENAI_API_KEY="your_openai_api_key_here"
```

Or create a `.env` file from `.env.example`.

### 3. CLI Usage

```bash
# Transcribe .ogg file
python transcribe.py audio/sample.ogg

# Transcribe multiple files
python transcribe.py audio/*.ogg

# Specify language
python transcribe.py --language es audio/spanish.ogg

# Output JSON format
python transcribe.py --format json audio/file.ogg > transcription.json

# Batch processing
python transcribe.py --format json --workers 5 *.ogg
```

### 4. Web API

Start the web service:

```bash
python web_service.py
# Or
python -m uvicorn web_service:app --host 0.0.0.0 --port 8000
```

API endpoints:

- `GET /` - Home page
- `GET /health` - Health check
- `POST /transcribe` - Upload and transcribe immediately
- `POST /transcribe/async` - Async transcription with job ID
- `GET /job/{job_id}` - Get job status
- `GET /formats` - Supported file formats

### 5. Docker Deployment

```bash
# Build and run with docker-compose
docker-compose up --build

# Or build manually
docker build -t whisper-service .
docker run -p 8000:8000 -e OPENAI_API_KEY=your_key whisper-service
```

## API Reference

### Upload File
```bash
curl -X POST "http://localhost:8000/transcribe" \
  -F "file=@sample.ogg" \
  -F "language=es"
```

### Async Upload
```bash
curl -X POST "http://localhost:8000/transcribe/async" \
  -F "file=@sample.ogg" \
  -F "language=fr"
```

### Check Job Status
```bash
curl "http://localhost:8000/job/{job_id}"
```

## Response Format

```json
{
  "file": "/path/to/audio.ogg",
  "text": "Complete transcription text here...",
  "language": "en",
  "duration": 45.67,
  "segments": [
    {
      "start": 0.0,
      "end": 4.56,
      "text": "First segment text",
      "avg_logprob": -0.123,
      "compression_ratio": 1.45,
      "no_speech_prob": 0.001,
      "temperature": 0.0
    }
  ]
}
```

## Supported Languages

The service supports 50+ languages. Common codes:
- `en` - English
- `es` - Spanish
- `fr` - French
- `de` - German
- `it` - Italian
- `pt` - Portuguese
- `ru` - Russian
- `zh` - Chinese
- `ja` - Japanese
- `ko` - Korean

## Development

### Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install development dependencies
pip install -r requirements.txt
pip install pytest mypy black isort

# Run tests
pytest

# Code formatting
black .
isort .
```

### Project Structure
```
whisper-transcription-service/
├── transcribe.py           # CLI tool
├── web_service.py          # FastAPI web service
├── requirements.txt        # Python dependencies
├── Dockerfile             # Container build
├── docker-compose.yml     # Docker compose
├── README.md             # This file
└── .env.example          # Environment template
```

## Error Handling

The service includes robust error handling:
- File validation
- API rate limiting
- Network timeouts
- Audio format compatibility
- Comprehensive logging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and test thoroughly
4. Run tests and linting
5. Submit a pull request

## License

MIT License - feel free to use in personal and commercial projects.