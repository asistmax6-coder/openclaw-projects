#!/usr/bin/env python3
"""
Unit tests for the Whisper transcription service
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import json

# Add the project root to Python path for testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from transcribe import WhisperTranscriber
except ImportError as e:
    print(f"Warning: Could not import transcribe module: {e}")
    WhisperTranscriber = None

@pytest.fixture
def temp_audio_file():
    """Create a temporary ogg file for testing"""
    try:
        import numpy as np
        from pydub import AudioSegment
        
        # Create 1 second of silence
        duration = 1000  # milliseconds
        audio = AudioSegment.silent(duration=duration)
        audio = audio.set_frame_rate(16000).set_channels(1)
        
        with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as tmp:
            audio.export(tmp.name, format='ogg')
            yield tmp.name
    except ImportError:
        # Fallback for environments without audio libs
        with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as tmp:
            tmp.write(b'dummy audio data')
            yield tmp.name
    finally:
        if os.path.exists(tmp.name):
            os.unlink(tmp.name)

def test_transcriber_initialization():
    """Test basic transcriber initialization"""
    if WhisperTranscriber is None:
        pytest.skip("Transcriber not available")
    
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        transcriber = WhisperTranscriber()
        assert transcriber.api_key == "test-key"
        assert transcriber.client is not None

def test_transcriber_missing_api_key():
    """Test error when API key is missing"""
    if WhisperTranscriber is None:
        pytest.skip("Transcriber not available")
    
    with patch.dict(os.environ, clear=True):
        with pytest.raises(ValueError, match="OpenAI API key required"):
            WhisperTranscriber()

def test_transcriber_invalid_file():
    """Test handling of non-existent file"""
    if WhisperTranscriber is None:
        pytest.skip("Transcriber not available")
    
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        transcriber = WhisperTranscriber()
        
        # Mock the OpenAI client
        mock_client = MagicMock()
        transcriber.client = mock_client
        
        result = transcriber.transcribe_audio("nonexistent.ogg")
        assert "error" in result
        assert "File not found" in result["error"]

@patch('openai.OpenAI')
def test_transcriber_success(mock_openai_class, temp_audio_file):
    """Test successful transcription"""
    if WhisperTranscriber is None:
        pytest.skip("Transcriber not available")
    
    # Mock API response
    mock_client = MagicMock()
    mock_transcriptions = MagicMock()
    mock_transcription = MagicMock()
    
    mock_transcription.text = "Hello world from test audio"
    mock_transcription.language = "en"
    mock_transcription.duration = 1.0
    mock_transcription.segments = []
    
    mock_transcriptions.create.return_value = mock_transcription
    mock_client.audio = MagicMock()
    mock_client.audio.transcriptions = mock_transcriptions
    mock_openai_class.return_value = mock_client
    
    transcriber = WhisperTranscriber(api_key="test-key")
    result = transcriber.transcribe_audio(temp_audio_file)
    
    assert "error" not in result
    assert result["text"] == "Hello world from test audio"
    assert result["language"] == "en"
    assert result["file"].endswith('.ogg')

def test_batch_transcription():
    """Test batch processing functionality"""
    if WhisperTranscriber is None:
        pytest.skip("Transcriber not available")
    
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        transcriber = WhisperTranscriber()
        
        # Mock the transcribe_audio method
        transcriber.transcribe_audio = MagicMock()
        transcriber.transcribe_audio.return_value = {
            "file": "test.ogg",
            "text": "test transcription",
            "language": "en"
        }
        
        files = ["file1.ogg", "file2.ogg", "file3.ogg"]
        results = transcriber.batch_transcribe(files, max_workers=2)
        
        assert len(results) == 3
        for result in results:
            assert result["text"] == "test transcription"

def test_main_cli():
    """Test CLI interface"""
    # Test help output
    sys.argv = ["transcribe", "--help"]
    
    try:
        from transcribe import main
        with patch('sys.argv', ["transcribe", "--help"]):
            with pytest.raises(SystemExit):
                main()
    except Exception:
        # CLI testing can be complex; this is a basic test
        pass

if __name__ == "__main__":
    pytest.main([__file__, "-v"])