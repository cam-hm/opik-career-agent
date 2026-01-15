"""
Cartesia TTS Test Endpoint - For debugging Cartesia TTS
"""
import os
import asyncio
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from cartesia import Cartesia
import logging

router = APIRouter()
logger = logging.getLogger("tts-test")

# Get API key from environment
CARTESIA_API_KEY = os.getenv("CARTESIA_API_KEY")


@router.post("/test-tts")
async def test_tts(
    text: str = "Hello, this is a test of Cartesia Text to Speech.",
    voice: str = "British Lady",
    language: str = "en",
    model_id: str = None
):
    """
    Test Cartesia TTS directly.
    Returns audio as WAV file.
    """
    if not CARTESIA_API_KEY:
        raise HTTPException(status_code=500, detail="CARTESIA_API_KEY not set")
    
    try:
        client = Cartesia(api_key=CARTESIA_API_KEY)
        
        # Determine model
        # Default to sonic-3 for Vietnamese, sonic-english for English
        if not model_id:
            if language == "vi":
                model_id = "sonic-3"
            elif language == "en":
                model_id = "sonic-english"
            else:
                model_id = "sonic-multilingual" # Fallback for other languages
        
        logger.info(f"Calling Cartesia TTS | Voice: {voice} | Lang: {language} | Model: {model_id}")
        
        # Build arguments for tts.bytes
        tts_args = {
            "model_id": model_id,
            "transcript": text,
            "voice": {"mode": "id", "id": voice},
            "output_format": {"container": "wav", "encoding": "pcm_s16le", "sample_rate": 24000}
        }
        
        # For sonic-multilingual, language is required.
        # For sonic-3, we pass language if not en, assuming it supports it.
        if language != "en" and model_id in ["sonic-multilingual", "sonic-3", "sonic-preview"]:
            tts_args["language"] = language
            
        # Generate audio using Cartesia
        audio_iterator = client.tts.bytes(**tts_args)
        
        # Collect all audio chunks
        audio_data = b"".join(audio_iterator)
        
        logger.info(f"TTS response received: {len(audio_data)} bytes")
        
        return Response(
            content=audio_data,
            media_type="audio/wav",
            headers={
                "Content-Disposition": "inline; filename=tts_test.wav"
            }
        )
        
    except Exception as e:
        logger.error(f"TTS Error: {str(e)}")
        # Log detailed error info but don't expose to client
        if hasattr(e, 'response') and e.response:
             logger.error(f"Response body: {e.response.text}")
             
        raise HTTPException(status_code=500, detail="TTS generation failed")


@router.get("/test-tts-simple")
async def test_tts_simple():
    """
    Simple test to verify Cartesia API access.
    Returns JSON with status.
    """
    if not CARTESIA_API_KEY:
        return {
            "status": "error",
            "message": "CARTESIA_API_KEY not set in environment"
        }
    
    try:
        client = Cartesia(api_key=CARTESIA_API_KEY)
        
        # List available voices - convert pager to list
        voices_pager = client.voices.list()
        voices = list(voices_pager)
        voice_names = [v.name for v in voices[:10]]
        
        return {
            "status": "success",
            "message": "Cartesia API is accessible",
            "sample_voices": voice_names,
            "total_voices": len(voices)
        }
        
    except Exception as e:
        logger.error(f"Cartesia test failed: {e}")
        return {
            "status": "error",
            "message": "Failed to connect to Cartesia API"
        }


@router.get("/voices")
async def list_voices():
    """
    List all available Cartesia voices.
    """
    if not CARTESIA_API_KEY:
        raise HTTPException(status_code=500, detail="CARTESIA_API_KEY not set")
    
    try:
        client = Cartesia(api_key=CARTESIA_API_KEY)
        voices_pager = client.voices.list()
        voices = list(voices_pager)
        
        return {
            "voices": [
                {
                    "id": v.id,
                    "name": v.name,
                    "language": getattr(v, "language", "en")
                }
                for v in voices[:50]  # Limit to 50 for readability
            ]
        }
    except Exception as e:
        logger.error(f"Failed to list voices: {e}")
        raise HTTPException(status_code=500, detail="Failed to list voices")

