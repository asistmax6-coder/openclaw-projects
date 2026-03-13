#!/usr/bin/env python3
"""
Example usage of the Whisper transcription service
Demo script showing both CLI and programmatic usage
"""

import os
import tempfile
from transcribe import WhisperTranscriber

def example_cli_usage():
    """Show example CLI commands"""
    print("📋 CLI Usage Examples:")
    print("1. Single file:")
    print("   python transcribe.py sample.ogg")
    print()
    print("2. Batch processing:")
    print("   python transcribe.py *.ogg --output results.json")
    print()
    print("3. Language specification:")
    print("   python transcribe.py audio.mp3 --language es --format verbose")

def example_programmatic():
    """Show programmatic usage"""
    print("🐍 Programmatic Usage:")
    
    # Initialize
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Note: Set OPENAI_API_KEY environment variable to test")
        return
    
    transcriber = WhisperTranscriber()
    
    print("Basic usage:")
    print("""
from transcribe import WhisperTranscriber

transcriber = WhisperTranscriber()

# Single file
result = transcriber.transcribe_audio('audio.ogg')
print(result['text'])

# Batch processing
files = ['file1.ogg', 'file2.ogg', 'file3.ogg']
results = transcriber.batch_transcribe(files)
for r in results:
    print(f"{r['file']}: {r['text']}")
""")

def example_web_client():
    """Show web API usage examples"""
    print("🌐 Web API Usage:")
    print("""
import requests

# Upload file
with open('audio.ogg', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8000/transcribe', files=files)
    result = response.json()
    print(result['text'])

# Health check
response = requests.get('http://localhost:8000/health')
print(response.json())
""")

if __name__ == "__main__":
    print("🔧 Whisper Transcription Service - Usage Examples")
    print("=" * 50)
    example_cli_usage()
    print()
    example_programmatic()
    print()
    example_web_client()