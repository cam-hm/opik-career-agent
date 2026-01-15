"""
Transcript management for interview sessions.
"""
import json
import logging
import asyncio
from typing import Optional

from sqlalchemy import update

from app.services.core.database import AsyncSessionLocal
from app.models.interview import InterviewSession

logger = logging.getLogger("interview-agent")


class TranscriptManager:
    """
    Manages transcript capture and persistence.
    
    Handles periodic saving to prevent data loss.
    """
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.transcript: list[dict] = []
        self.last_save_count = 0
        self._save_task: Optional[asyncio.Task] = None
    
    def add_message(self, role: str, content: str):
        """Add a message to the transcript."""
        if content:
            self.transcript.append({"role": role, "content": content})
            logger.info(f"Transcript [{role}]: {content[:100]}...")
    
    async def save(self, final: bool = False):
        """Save transcript to database."""
        logger.info(f"Saving transcript for session {self.session_id}... (final={final})")
        
        if not self.transcript and not final:
            logger.warning("No transcript to save.")
            return
        
        status = "completed" if final else "active"
        
        async with AsyncSessionLocal() as db:
            stmt = (
                update(InterviewSession)
                .where(InterviewSession.session_id == self.session_id)
                .values(transcript=json.dumps(self.transcript), status=status)
            )
            await db.execute(stmt)
            await db.commit()
        
        self.last_save_count = len(self.transcript)
        logger.info(f"Transcript saved ({len(self.transcript)} messages, status={status})")
    
    async def start_periodic_save(self, interval_seconds: int = 30):
        """Start periodic background save task."""
        async def _periodic_save():
            while True:
                await asyncio.sleep(interval_seconds)
                if len(self.transcript) > self.last_save_count:
                    await self.save(final=False)
        
        self._save_task = asyncio.create_task(_periodic_save())
    
    async def stop_and_save(self):
        """Stop periodic save and perform final save."""
        if self._save_task:
            self._save_task.cancel()
        await self.save(final=True)
