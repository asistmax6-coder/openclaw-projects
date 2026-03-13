#!/usr/bin/env python3
"""
Test script for Whisper Transcription Service
"""

import pytest
import tempfile
import os
from pathlib import Path
from transcribe import WhisperTranscriber

class TestWhisperTranscriber:
    
    def test_init_without_api_key(self):
        """Test initialization without API key raises ValueError"""
        # Remove API key from environment
        old_key = os.environ.pop('OPENAI_API_KEY', None)
        try:
            with pytest.raises(ValueError, match="OpenAI API key required"):
                WhisperTranscriber()
        finally:
            # Restore original value
            if old_key:
                os.environ['OPENAI_API_KEY'] = old_key
    
    def test_init_with_valid_api_key(self):
        """Test initialization with valid API key"""
        # This is a dummy test since we can't use real API key
        assert True  # Placeholder for real API testing
    
    def test_supported_formats(self):
        """Test supported formats list"""
        transcriber = WhisperTranscriber(api_key="dummy_key")
        formats = transcriber.get_supported_formats()
        assert ".ogg" in formats
        assert ".mp3" in formats
        assert ".wav" in formats
        assert len(formats) >= 6
    
    def test_transcribe_nonexistent_file(self):
        """Test transcribing non-existent file"""
        transcriber = WhisperTranscriber(api_key="dummy_key")
        result = transcriber.transcribe_audio("nonexistent.ogg")
        assert "error" in result
        assert "not found" in result["error"].lower()

def test_cli_import():
    """Test that CLI can be imported"""
    import transcribe
    assert hasattr(transcribe, 'main')

def test_web_service_import():
    """Test that web service can be imported"""
    import web_service
    assert hasattr(web_service, 'app')

if __name__ == "__main__":
    pytest.main([__file__, "-v"])