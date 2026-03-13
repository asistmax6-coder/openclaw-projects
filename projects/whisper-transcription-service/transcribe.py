#!/usr/bin/env python3
"""
Whisper Transcription Service CLI Tool
Processes .ogg audio files and returns exact transcriptions using OpenAI API
"""

import sys
import os
import argparse
import json
import logging
from pathlib import Path
from openai import OpenAI
from pydub import AudioSegment
import concurrent.futures
from typing import Optional, List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WhisperTranscriber:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the transcriber with OpenAI client"""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable or pass --api-key")
        self.client = OpenAI(api_key=self.api_key)
        
    def transcribe_audio(self, file_path: str, language: Optional[str] = None) -> Dict[str, Any]:
        """Transcribe a single audio file"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
                
            logger.info(f"Starting transcription: {file_path}")
            
            # Download and convert .ogg to mp3 format for better compatibility
            if file_path.suffix.lower() == '.ogg':
                audio = AudioSegment.from_ogg(file_path)
                temp_mp3 = file_path.with_suffix('.mp3')
                audio.export(temp_mp3, format='mp3')
                file_to_transcribe = temp_mp3
            else:
                file_to_transcribe = file_path
            
            # Transcribe with OpenAI Whisper API
            with open(file_to_transcribe, 'rb') as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language,
                    response_format="verbose_json",
                    timestamp_granularities=["segment"]
                )
            
            # Clean up converted file
            if file_path.suffix.lower() == '.ogg' and file_to_transcribe != file_path:
                file_to_transcribe.unlink()
                
            logger.info(f"Completed transcription: {file_path}")
            
            return {
                "file": str(file_path),
                "text": transcript.text,
                "language": transcript.language,
                "duration": transcript.duration,
                "segments": [
                    {
                        "start": segment.start,
                        "end": segment.end,
                        "text": segment.text,
                        "avg_logprob": segment.avg_logprob,
                        "compression_ratio": segment.compression_ratio,
                        "no_speech_prob": segment.no_speech_prob,
                        "temperature": segment.temperature
                    }
                    for segment in transcript.segments
                ]
            }
            
        except Exception as e:
            logger.error(f"Error transcribing {file_path}: {str(e)}")
            return {
                "file": str(file_path),
                "error": str(e),
                "text": None
            }
    
    def transcribe_batch(self, file_paths: List[str], language: Optional[str] = None, max_workers: int = 3) -> List[Dict[str, Any]]:
        """Transcribe multiple files in parallel"""
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {
                executor.submit(self.transcribe_audio, file_path, language): file_path 
                for file_path in file_paths
            }
            
            results = []
            for future in concurrent.futures.as_completed(future_to_file):
                result = future.result()
                results.append(result)
                
            return sorted(results, key=lambda x: x.get("file", ""))
    
    def get_supported_formats(self) -> List[str]:
        """Return list of supported audio formats"""
        return [".ogg", ".mp3", ".wav", ".m4a", ".flac", ".webm"]

def main():
    parser = argparse.ArgumentParser(description="Whisper Transcription CLI Tool")
    parser.add_argument("files", nargs="+", help="Audio files to transcribe")
    parser.add_argument("--api-key", help="OpenAI API key")
    parser.add_argument("--language", help="Language code (e.g., 'es', 'en', 'fr')")
    parser.add_argument("--output", help="Output JSON file path")
    parser.add_argument("--format", choices=["text", "json", "verbose"], default="text")
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        transcriber = WhisperTranscriber(api_key=args.api_key)
        
        # Validate files
        valid_files = [f for f in args.files if Path(f).exists()]
        if not valid_files:
            print("❌ No valid files found")
            sys.exit(1)
            
        results = transcriber.transcribe_batch(valid_files, language=args.language, max_workers=args.workers)
        
        # Format and output results
        if args.format == "json" or args.format == "verbose":
            output = json.dumps(results, indent=2, ensure_ascii=False)
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(output)
                print(f"✅ Results saved to {args.output}")
            else:
                print(output)
        else:
            for result in results:
                if "error" in result:
                    print(f"❌ {result['file']}: {result['error']}")
                else:
                    print(f"🎯 {result['file']} ({result['language']})")
                    print(result["text"])
                    print("-" * 50)
            
            success_count = sum(1 for r in results if "error" not in r)
            total_count = len(results)
            print(f"\n✅ Transcribed {success_count}/{total_count} files successfully")
            
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()