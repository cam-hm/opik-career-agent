"""
Set Daily Streak - Development/Testing Helper

Usage:
    python scripts/dev/set_streak.py <user_id> <streak_count>
    python scripts/dev/set_streak.py user_abc123 5
    
Docker:
    docker exec -it interviewer-backend python scripts/dev/set_streak.py user_abc123 5
"""
import asyncio
import argparse
import sys
import os
from datetime import datetime, timezone

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.services.core.database import AsyncSessionLocal
from app.models.gamification import UserProgress
from sqlalchemy import select


async def set_streak(user_id: str, streak: int):
    """Set user's daily streak."""
    async with AsyncSessionLocal() as db:
        stmt = select(UserProgress).where(UserProgress.user_id == user_id)
        result = await db.execute(stmt)
        progress = result.scalar_one_or_none()
        
        if not progress:
            print(f"❌ User {user_id} not found")
            return
        
        old_streak = progress.daily_streak or 0
        progress.daily_streak = streak
        progress.last_active_at = datetime.now(timezone.utc)
        
        await db.commit()
        print(f"🔥 Streak updated: {old_streak} → {streak}")
        print(f"✅ Done for user {user_id}")


async def main():
    parser = argparse.ArgumentParser(
        description="Set user's daily streak for testing"
    )
    parser.add_argument("user_id", help="User ID")
    parser.add_argument("streak", type=int, help="Streak count to set")
    
    args = parser.parse_args()
    await set_streak(args.user_id, args.streak)


if __name__ == "__main__":
    asyncio.run(main())
