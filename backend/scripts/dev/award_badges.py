"""
Award Badges to User - Development/Testing Helper

Usage:
    python scripts/dev/award_badges.py <user_id> <badge_id> [badge_id2...]
    python scripts/dev/award_badges.py user_abc123 first_step perfectionist
    python scripts/dev/award_badges.py user_abc123 --all  # Award all badges
    
Docker:
    docker exec -it interviewer-backend python scripts/dev/award_badges.py user_abc123 first_step
"""
import asyncio
import argparse
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.services.core.database import AsyncSessionLocal
from app.models.gamification import UserAchievement, Achievement
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert


async def get_all_badge_ids():
    """Get all available badge IDs from database."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Achievement.id))
        return [row[0] for row in result.fetchall()]


async def award_badges(user_id: str, badge_ids: list):
    """Award badges to a user."""
    async with AsyncSessionLocal() as db:
        for badge_id in badge_ids:
            # Check if badge exists
            badge_check = await db.execute(
                select(Achievement).where(Achievement.id == badge_id)
            )
            if not badge_check.scalar_one_or_none():
                print(f"⚠️  Badge '{badge_id}' not found, skipping")
                continue
            
            # Upsert user achievement
            stmt = insert(UserAchievement).values(
                user_id=user_id,
                achievement_id=badge_id
            )
            stmt = stmt.on_conflict_do_nothing()
            await db.execute(stmt)
            print(f"🏅 Awarded: {badge_id}")
        
        await db.commit()
        print(f"\n✅ Done! Awarded badges to {user_id}")


async def main():
    parser = argparse.ArgumentParser(
        description="Award badges to a user for testing",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("user_id", help="User ID to award badges to")
    parser.add_argument(
        "badges",
        nargs="*",
        help="Badge IDs to award (or --all for all badges)"
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Award all available badges"
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List available badges"
    )
    
    args = parser.parse_args()
    
    if args.list:
        badge_ids = await get_all_badge_ids()
        print("\n📋 Available Badges:")
        for bid in badge_ids:
            print(f"  • {bid}")
        return
    
    if args.all:
        badge_ids = await get_all_badge_ids()
        await award_badges(args.user_id, badge_ids)
    elif args.badges:
        await award_badges(args.user_id, args.badges)
    else:
        print("Error: Must specify badge IDs or --all")
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
