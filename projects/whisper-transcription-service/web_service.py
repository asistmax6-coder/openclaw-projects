#!/usr/bin/env python3
"""
FastAPI web service for Whisper transcription
Provides endpoints for uploading and transcribing audio files
"""

import os
import tempfile
import shutil
import asyncio
import logging
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from transcribe import WhisperTranscriber

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Whisper Transcription API",
    description="Audio transcription service using OpenAI Whisper",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global transcriber instance
_transcriber = None

def get_transcriber() -> WhisperTranscriber:
    """Get or initialize the transcriber"""
    global _transcriber
    if _transcriber is None:
        try:
            _transcriber = WhisperTranscriber()
        except ValueError as e:
            raise HTTPException(status_code=500, detail=str(e))
    return _transcriber

class TranscriptionJob(BaseModel):
    job_id: str
    status: str
    filename: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# In-memory job storage (replace with Redis for production)
job_storage: Dict[str, TranscriptionJob] = {}

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with basic information"""
    return """
    <html>
        <head>
            <title>Whisper Transcription Service</title>
        </head>
        <body>
            <h1>Whisper Transcription Service</h1>
            <p>Audio transcription powered by OpenAI Whisper API</p>
            <p><a href="/docs">API Documentation</a></p>
            <p><a href="/health">Health Check</a></p>
        </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        transcriber = get_transcriber()
        return {
            "status": "healthy",
            "service": "whisper-transcription",
            "supported_formats": transcriber.get_supported_formats(),
            "timestamp": str(asyncio.get_event_loop().time())
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )

@app.get("/formats")
async def supported_formats():
    """Get supported audio formats"""
    transcriber = get_transcriber()
    return {"supported_formats": transcriber.get_supported_formats()}

@app.post("/transcribe", response_model=TranscriptionJob)
async def transcribe_audio(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    language: Optional[str] = Query(None, description="Language code")
):
    """
    Upload an audio file for immediate transcription
    
    Supports: .ogg, .mp3, .wav, .m4a, .flac, .webm
    """
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    # Check file extension
    allowed_extensions = transcriber.get_supported_formats()
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    try:
        # Create temporary file
        suffix = file_extension or ".tmp"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False, dir=tempfile.gettempdir()) as tmp_file:
            # Write file content
            content = await file.read()
            if len(content) == 0:
                raise HTTPException(status_code=400, detail="Empty file")
                
            tmp_file.write(content)
            tmp_path = tmp_file.name
            
        # Transcribe immediately (synchronous for single file)
        transcriber = get_transcriber()
        
        try:
            result = transcriber.transcribe_audio(tmp_path, language=language)
            
            if "error" in result:
                raise HTTPException(status_code=500, detail=result["error"])
            
            return TranscriptionJob(
                job_id="immediate",
                status="completed",
                filename=file.filename,
                result=result
            )
            
        finally:
            # Clean temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
                
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transcribe/async", response_model=TranscriptionJob)
async def transcribe_audio_async(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    language: Optional[str] = Query(None, description="Language code")
):
    """
    Upload an audio file for asynchronous transcription
    Returns job ID for status checking
    """
    import uuid
    
    job_id = str(uuid.uuid4())
    
    # Create job record
    job = TranscriptionJob(
        job_id=job_id,
        status="processing",
        filename=file.filename,
        result=None
    )
    job_storage[job_id] = job
    
    # Process in background
    background_tasks.add_task(process_transcription, job_id, file, language)
    
    return job

async def process_transcription(job_id: str, file: UploadFile, language: Optional[str]):
    """Process transcription in background"""
    try:
        with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False, dir=tempfile.gettempdir()) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        transcriber = get_transcriber()
        result = transcriber.transcribe_audio(tmp_path, language=language)
        
        job_storage[job_id].status = "completed"
        if "error" not in result:
            job_storage[job_id].result = result
        else:
            job_storage[job_id].error = result["error"]
            job_storage[job_id].status = "failed"
        
        # Clean up
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
            
    except Exception as e:
        job_storage[job_id].status = "failed"
        job_storage[job_id].error = str(e)

@app.get("/job/{job_id}")
async def get_job_status(job_id: str):
    """Get job status and results"""
    if job_id not in job_storage:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job_storage[job_id]

@app.get("/stats")
async def service_stats():
    """Get service statistics"""
    jobs = list(job_storage.values())
    stats = {
        "total_jobs": len(jobs),
        "completed": len([j for j in jobs if j.status == "completed"]),
        "processing": len([j for j in jobs if j.status == "processing"]),
        "failed": len([j for j in jobs if j.status == "failed"])
    }
    return stats

@app.delete("/job/{job_id}")
async def delete_job(job_id: str):
    """Delete a job (cleanup)"""
    if job_id not in job_storage:
        raise HTTPException(status_code=404, detail="Job not found")
    
