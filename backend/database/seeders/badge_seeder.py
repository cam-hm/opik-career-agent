"""
Badge Seeder - Seeds achievement/badge definitions.

This seeds the MASTER DATA for badges (achievements table).
For testing user badge awards, use scripts/dev/award_badges.py
"""
from database.seeders.base import BaseSeeder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from app.models.gamification import Achievement


# Badge Definitions
BADGES = [
    {
        "id": "first_step",
        "name": {"en": "First Step", "vi": "First Step"},
        "description": {"en": "Complete your first interview practice", "vi": "Hoàn thành bài tập phỏng vấn đầu tiên"},
        "icon_url": "🎯",
        "criteria": {"type": "interview_count", "min": 1}
    },
    {
        "id": "speed_demon",
        "name": {"en": "Speed Demon", "vi": "Speed Demon"},
        "description": {"en": "Complete an interview in under 10 minutes", "vi": "Hoàn thành một cuộc phỏng vấn dưới 10 phút"},
        "icon_url": "⚡",
        "criteria": {"type": "interview_duration", "max_minutes": 10}
    },
    {
        "id": "perfectionist",
        "name": {"en": "Perfectionist", "vi": "Perfectionist"},
        "description": {"en": "Score 90% or higher on any interview", "vi": "Đạt điểm 90% trở lên trong bất kỳ cuộc phỏng vấn nào"},
        "icon_url": "💎",
        "criteria": {"type": "interview_score", "min": 90}
    },
    {
        "id": "streak_master",
        "name": {"en": "Streak Master", "vi": "Streak Master"},
        "description": {"en": "Maintain a 3-day practice streak", "vi": "Duy trì chuỗi luyện tập 3 ngày liên tiếp"},
        "icon_url": "🔥",
        "criteria": {"type": "daily_streak", "min": 3}
    },
    {
        "id": "expert",
        "name": {"en": "Expert", "vi": "Expert"},
        "description": {"en": "Complete 10 interviews", "vi": "Hoàn thành 10 cuộc phỏng vấn"},
        "icon_url": "🏆",
        "criteria": {"type": "interview_count", "min": 10}
    },
    {
        "id": "guru",
        "name": {"en": "Guru", "vi": "Guru"},
        "description": {"en": "Reach Level 5", "vi": "Đạt cấp độ 5"},
        "icon_url": "🧙",
        "criteria": {"type": "level", "min": 5}
    },
    {
        "id": "legend",
        "name": {"en": "Legend", "vi": "Legend"},
        "description": {"en": "Reach Level 10", "vi": "Đạt cấp độ 10"},
        "icon_url": "👑",
        "criteria": {"type": "level", "min": 10}
    },
    {
        "id": "champion",
        "name": {"en": "Champion", "vi": "Champion"},
        "description": {"en": "Complete 25 interviews", "vi": "Hoàn thành 25 cuộc phỏng vấn"},
        "icon_url": "🥇",
        "criteria": {"type": "interview_count", "min": 25}
    },
    {
        "id": "elite",
        "name": {"en": "Elite", "vi": "Elite"},
        "description": {"en": "Score 95% or higher 3 times", "vi": "Đạt điểm 95% trở lên 3 lần"},
        "icon_url": "⭐",
        "criteria": {"type": "high_score_count", "min_score": 95, "min_count": 3}
    },
]


class BadgeSeeder(BaseSeeder):
    """Seeds badge/achievement definitions."""
    
    name = "badges"
    description = "Seed badge definitions to achievements table"
    
    async def run(self, db: AsyncSession) -> int:
        count = 0
        
        for badge in BADGES:
            stmt = insert(Achievement).values(
                id=badge["id"],
                name=badge["name"],
                description=badge["description"],
                icon_url=badge["icon_url"],
                criteria=badge["criteria"]
            )
            
            # Upsert - update if exists
            update_stmt = stmt.on_conflict_do_update(
                index_elements=['id'],
                set_=dict(
                    name=stmt.excluded.name,
                    description=stmt.excluded.description,
                    icon_url=stmt.excluded.icon_url,
                    criteria=stmt.excluded.criteria
                )
            )
            
            await db.execute(update_stmt)
            count += 1
        
        await db.commit()
        self.log(f"✅ Seeded {count} badges")
        return count
