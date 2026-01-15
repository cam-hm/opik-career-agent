"""
Reset User Progress - Development/Testing Helper

Usage:
    python scripts/dev/reset_progress.py <user_id>
    python scripts/dev/reset_progress.py user_abc123 --keep-badges  # Keep badges
    python scripts/dev/reset_progress.py user_abc123 --full        # Full reset including badges
    
Docker:
    docker exec -it interviewer-backend python scripts/dev/reset_progress.py user_abc123
"""
import asyncio
import argparse
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.services.core.database import AsyncSessionLocal
from app.models.gamification import UserProgress, UserNode, UserAchievement
from sqlalchemy import delete, select


async def reset_progress(user_id: str, keep_badges: bool = True):
    """Reset user gamification progress."""
    async with AsyncSessionLocal() as db:
        # Reset UserProgress
        progress_stmt = select(UserProgress).where(UserProgress.user_id == user_id)
        result = await db.execute(progress_stmt)
        progress = result.scalar_one_or_none()
        
        if progress:
            progress.current_level = 1
            progress.current_xp = 0
            progress.daily_streak = 0
            progress.last_active_at = None
            progress.skill_stats = {
                "coding_standards": 50,
                "system_design": 50,
                "algorithms": 50,
                "communication": 50,
                "tech_proficiency": 50,
                "debugging": 50
            }
            print(f"🔄 Reset UserProgress to Level 1, 0 XP")
        else:
            print(f"⚠️  No UserProgress found for {user_id}")
        
        # Delete UserNodes
        node_delete = delete(UserNode).where(UserNode.user_id == user_id)
        result = await db.execute(node_delete)
        print(f"🗑️  Deleted {result.rowcount} UserNode records")
        
        # Optionally delete badges
        if not keep_badges:
            badge_delete = delete(UserAchievement).where(UserAchievement.user_id == user_id)
            result = await db.execute(badge_delete)
            print(f"🗑️  Deleted {result.rowcount} badges")
        else:
            print(f"🏅 Kept existing badges")
        
        await db.commit()
        print(f"\n✅ Progress reset for {user_id}")


async def main():
    parser = argparse.ArgumentParser(
        description="Reset user gamification progress for testing"
    )
    parser.add_argument("user_id", help="User ID to reset")
    parser.add_argument(
        "--keep-badges", "-k",
        action="store_true",
        default=True,
        help="Keep earned badges (default)"
    )
    parser.add_argument(
        "--full", "-f",
        action="store_true",
        help="Full reset including badges"
    )
    
    args = parser.parse_args()
    
    keep_badges = not args.full
    await reset_progress(args.user_id, keep_badges=keep_badges)


if __name__ == "__main__":
    asyncio.run(main())
