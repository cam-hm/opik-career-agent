
"""
Gamification Service Module.

Handles all write operations for the RPG layer:
- Granting XP / Level Ups
- Marking Nodes as Complete
- Unlocking new Nodes
- Calculating Radar Chart Stats (Moving Average)
"""
import logging
import math
from typing import List, Dict, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.gamification import UserProgress, UserNode, CareerNode, Achievement, UserAchievement
from app.services.core.gamification.career_manager import career_manager

logger = logging.getLogger("gamification-service")

class GamificationService:
    
    # --- XP CONSTANTS ---
    BASE_XP = 100
    LEVEL_CONSTANT = 0.1 # Level = CONST * sqrt(XP)
    
    async def get_or_create_progress(self, db: AsyncSession, user_id: str) -> UserProgress:
        """Fetch user progress or initialize it."""
        stmt = select(UserProgress).where(UserProgress.user_id == user_id)
        result = await db.execute(stmt)
        progress = result.scalar_one_or_none()
        
        if not progress:
            # Initialize with default stats (Developer Focused)
            default_stats = {
                "coding_standards": 50,
                "system_design": 50,
                "algorithms": 50,
                "communication": 50,
                "tech_proficiency": 50,
                "debugging": 50
            }
            progress = UserProgress(
                user_id=user_id, 
                current_level=1, 
                current_xp=0,
                skill_stats=default_stats
            )
            db.add(progress)
            await db.flush() # Get ID if needed, though user_id is set
            
            # Seed Initial Nodes (Roots)
            # For MVP, we auto-unlock the first node: "node_associate_start"
            # In a real app, CareerManager would define 'roots'
            await self._unlock_node(db, user_id, "node_associate_start")
            
        return progress

    async def get_user_status(self, db: AsyncSession, user_id: str) -> Dict:
        """Get full dashboard status payload."""
        progress = await self.get_or_create_progress(db, user_id)
        
        # Get all UserNodes
        stmt = select(UserNode).where(UserNode.user_id == user_id)
        result = await db.execute(stmt)
        user_nodes = result.scalars().all()
        
        nodes_map = {
            un.node_id: {
                "node_id": un.node_id, 
                "status": un.status, 
                "high_score": un.high_score
            } for un in user_nodes
        }
        
        # Get user badges
        badges = await self._get_user_badges(db, user_id)
        
        return {
            "level": progress.current_level,
            "xp": progress.current_xp,
            "stats": progress.skill_stats,
            "streak": progress.daily_streak,
            "rank_title": career_manager.get_rank_title(progress.current_level // 5 + 1), # Approx logic
            "target_role": progress.target_role,
            "nodes": nodes_map,
            "badges": badges
        }

    async def complete_node(self, db: AsyncSession, user_id: str, node_id: str, score: int, metrics: Dict[str, int]) -> Dict:
        """
        Process node completion.
        1. Mark UserNode as completed.
        2. Calculate XP gain.
        3. Update Radar Stats (Moving Average).
        4. Unlock children.
        """
        node_def = career_manager.get_node(node_id)
        if not node_def:
            raise ValueError(f"Node {node_id} does not exist")
            
        # 0. Ensure User Progress Exists (Foreign Key Constraint)
        await self.get_or_create_progress(db, user_id)
            
        # 1. Get/Update UserNode
        stmt = select(UserNode).where(
            UserNode.user_id == user_id, 
            UserNode.node_id == node_id
        )
        result = await db.execute(stmt)
        user_node = result.scalar_one_or_none()
        
        if not user_node:
            # Should have been unlocked first, but create if missing (defensive)
            user_node = UserNode(user_id=user_id, node_id=node_id, status="unlocked")
            db.add(user_node)
        
        user_node.status = "completed"
        user_node.high_score = max((user_node.high_score or 0), score)
        # updated_at handled by DB or explicit logic? Let's rely on model or just create timestamp
        from datetime import datetime
        user_node.completed_at = datetime.utcnow()
        
        # 2. XP Calculation
        xp_gain = int(self.BASE_XP * (score / 100.0))
        if score == 100:
            xp_gain += 50 # Perfect bonus
            
        progress = await self.get_or_create_progress(db, user_id)
        progress.current_xp += xp_gain
        
        # 3. Daily Streak Logic
        from datetime import datetime, timedelta, timezone
        today = datetime.now(timezone.utc).date()
        last_active = progress.last_active_at.date() if progress.last_active_at else None
        
        if last_active == today:
            pass  # Already active today, streak unchanged
        elif last_active == today - timedelta(days=1):
            progress.daily_streak = (progress.daily_streak or 0) + 1
            logger.info(f"🔥 User {user_id} streak increased to {progress.daily_streak}")
        else:
            # Streak broken (or first activity)
            progress.daily_streak = 1
            logger.info(f"🔄 User {user_id} streak reset to 1")
        
        progress.last_active_at = datetime.now(timezone.utc)
        
        # Level Up Logic: Level = 0.1 * sqrt(XP)  => XP = (Level/0.1)^2
        # Simple linear for MVP: Every 500 XP = 1 Level
        new_level = 1 + (progress.current_xp // 500)
        leveled_up = new_level > progress.current_level
        progress.current_level = new_level
        
        # 3. Update Radar Stats (Moving Averge approximation)
        # NewAverage = OldAverage + (NewValue - OldAverage) / N ??
        # Or just simple weighted: 0.8 * Old + 0.2 * New
        alpha = 0.3 # Weight of new session
        current_stats = progress.skill_stats or {}
        
        updated_stats = {}
        # Developer-First Axis
        for key in ["coding_standards", "system_design", "algorithms", "communication", "tech_proficiency", "debugging"]:
            old_val = current_stats.get(key, 50)
            new_val = metrics.get(key, old_val) # Fallback to old if metric missing
            weighted = int((1 - alpha) * old_val + alpha * new_val)
            updated_stats[key] = weighted
            
        progress.skill_stats = updated_stats
        
        # 4. Unlock Children
        unlocked_ids = []
        children = node_def.get('unlocks', [])
        for child_id in children:
             # Check if already exists
            stmt_child = select(UserNode).where(
                UserNode.user_id == user_id,
                UserNode.node_id == child_id
            )
            res_child = await db.execute(stmt_child)
            existing = res_child.scalar_one_or_none()
            
            if not existing:
                await self._unlock_node(db, user_id, child_id)
                unlocked_ids.append(child_id)
        
        await db.commit()
        
        # 5. Check for new badges
        new_badges = await self.check_and_award_badges(db, user_id, score=score)
        
        return {
            "xp_gained": xp_gain,
            "new_total_xp": progress.current_xp,
            "leveled_up": leveled_up,
            "new_level": new_level,
            "unlocked_nodes": unlocked_ids,
            "new_badges": new_badges
        }

    async def _unlock_node(self, db: AsyncSession, user_id: str, node_id: str):
        """Helper to create an unlocked UserNode."""
        node = UserNode(user_id=user_id, node_id=node_id, status="unlocked")
        db.add(node)
    
    async def _get_user_badges(self, db: AsyncSession, user_id: str) -> List[Dict]:
        """Get all badges the user has unlocked."""
        from sqlalchemy.orm import joinedload
        
        stmt = select(UserAchievement).where(
            UserAchievement.user_id == user_id
        )
        result = await db.execute(stmt)
        user_achievements = result.scalars().all()
        
        # Get badge details
        badges = []
        for ua in user_achievements:
            badge_stmt = select(Achievement).where(Achievement.id == ua.achievement_id)
            badge_result = await db.execute(badge_stmt)
            badge = badge_result.scalar_one_or_none()
            if badge:
                badges.append({
                    "id": badge.id,
                    "name": badge.name,
                    "description": badge.description,
                    "icon": badge.icon_url,
                    "unlocked_at": ua.unlocked_at.isoformat() if ua.unlocked_at else None
                })
        
        return badges
    
    async def check_and_award_badges(self, db: AsyncSession, user_id: str, score: int = 0) -> List[str]:
        """
        Check all badge criteria and award any newly earned badges.
        Returns list of newly awarded badge IDs.
        """
        progress = await self.get_or_create_progress(db, user_id)
        
        # Get all achievements
        all_badges_stmt = select(Achievement)
        all_badges_result = await db.execute(all_badges_stmt)
        all_badges = all_badges_result.scalars().all()
        
        # Get user's current badges
        user_badges_stmt = select(UserAchievement.achievement_id).where(
            UserAchievement.user_id == user_id
        )
        user_badges_result = await db.execute(user_badges_stmt)
        owned_badge_ids = set(user_badges_result.scalars().all())
        
        # Count completed nodes
        completed_stmt = select(UserNode).where(
            UserNode.user_id == user_id,
            UserNode.status == "completed"
        )
        completed_result = await db.execute(completed_stmt)
        completed_nodes = completed_result.scalars().all()
        interview_count = len(completed_nodes)
        
        # Count high scores
        high_score_count = sum(1 for n in completed_nodes if (n.high_score or 0) >= 95)
        
        new_badges = []
        
        for badge in all_badges:
            if badge.id in owned_badge_ids:
                continue  # Already has this badge
                
            criteria = badge.criteria or {}
            criteria_type = criteria.get("type")
            earned = False
            
            if criteria_type == "interview_count":
                earned = interview_count >= criteria.get("min", 1)
            elif criteria_type == "interview_score":
                earned = score >= criteria.get("min", 90)
            elif criteria_type == "level":
                earned = progress.current_level >= criteria.get("min", 1)
            elif criteria_type == "daily_streak":
                earned = (progress.daily_streak or 0) >= criteria.get("min", 3)
            elif criteria_type == "high_score_count":
                earned = high_score_count >= criteria.get("min_count", 3)
            # interview_duration would need session timing data - skip for now
            
            if earned:
                # Award the badge
                new_badge = UserAchievement(
                    user_id=user_id,
                    achievement_id=badge.id
                )
                db.add(new_badge)
                new_badges.append(badge.id)
                logger.info(f"🏅 User {user_id} earned badge: {badge.name}")
        
        if new_badges:
            await db.commit()
        
        return new_badges
        
gamification_service = GamificationService()
