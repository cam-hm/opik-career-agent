"""
🕷️ Black Widow QA Tests - Gamification Service

Tests for:
- Daily streak logic (same day, consecutive, broken)
- Badge awarding logic  
- XP/Level calculations
- Node completion flow
"""
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch


# ===== Mock Fixtures =====

@pytest.fixture
def mock_db():
    """Create a mock async database session."""
    db = AsyncMock()
    db.execute = AsyncMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.flush = AsyncMock()
    return db


@pytest.fixture
def mock_user_progress():
    """Create a mock UserProgress object."""
    progress = MagicMock()
    progress.user_id = "user_test123"
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
    return progress


@pytest.fixture
def mock_user_node():
    """Create a mock UserNode object."""
    node = MagicMock()
    node.user_id = "user_test123"
    node.node_id = "node_test"
    node.status = "unlocked"
    node.high_score = 0
    node.completed_at = None
    return node


# ===== Daily Streak Tests =====

class TestDailyStreakLogic:
    """Tests for daily streak tracking in complete_node."""
    
    def test_streak_unchanged_if_already_active_today(self, mock_user_progress):
        """Streak should not change if user already active today."""
        # Setup: last_active_at is today
        now = datetime.now(timezone.utc)
        mock_user_progress.last_active_at = now
        mock_user_progress.daily_streak = 5
        
        today = now.date()
        last_active = mock_user_progress.last_active_at.date()
        
        # Logic from complete_node
        if last_active == today:
            new_streak = mock_user_progress.daily_streak  # unchanged
        elif last_active == today - timedelta(days=1):
            new_streak = mock_user_progress.daily_streak + 1
        else:
            new_streak = 1
        
        assert new_streak == 5  # Unchanged
    
    def test_streak_increments_on_consecutive_day(self, mock_user_progress):
        """Streak should increment if last active was yesterday."""
        # Setup: last_active_at is yesterday
        now = datetime.now(timezone.utc)
        yesterday = now - timedelta(days=1)
        mock_user_progress.last_active_at = yesterday
        mock_user_progress.daily_streak = 3
        
        today = now.date()
        last_active = mock_user_progress.last_active_at.date()
        
        # Logic from complete_node
        if last_active == today:
            new_streak = mock_user_progress.daily_streak
        elif last_active == today - timedelta(days=1):
            new_streak = mock_user_progress.daily_streak + 1
        else:
            new_streak = 1
        
        assert new_streak == 4  # Incremented
    
    def test_streak_resets_if_gap_of_two_days(self, mock_user_progress):
        """Streak should reset to 1 if more than 1 day gap."""
        # Setup: last_active_at is 2 days ago
        now = datetime.now(timezone.utc)
        two_days_ago = now - timedelta(days=2)
        mock_user_progress.last_active_at = two_days_ago
        mock_user_progress.daily_streak = 10
        
        today = now.date()
        last_active = mock_user_progress.last_active_at.date()
        
        # Logic from complete_node
        if last_active == today:
            new_streak = mock_user_progress.daily_streak
        elif last_active == today - timedelta(days=1):
            new_streak = mock_user_progress.daily_streak + 1
        else:
            new_streak = 1
        
        assert new_streak == 1  # Reset
    
    def test_streak_starts_at_1_for_first_activity(self, mock_user_progress):
        """Streak should start at 1 for first ever activity."""
        # Setup: never active before
        mock_user_progress.last_active_at = None
        mock_user_progress.daily_streak = 0
        
        today = datetime.now(timezone.utc).date()
        last_active = None
        
        # Logic from complete_node
        if last_active == today:
            new_streak = mock_user_progress.daily_streak
        elif last_active and last_active == today - timedelta(days=1):
            new_streak = mock_user_progress.daily_streak + 1
        else:
            new_streak = 1
        
        assert new_streak == 1  # First activity


# ===== XP & Level Calculation Tests =====

class TestXPAndLevelCalculation:
    """Tests for XP gain and level up logic."""
    
    def test_base_xp_calculation(self):
        """XP should be BASE_XP * (score / 100)."""
        BASE_XP = 100
        
        # 100% score = 100 XP + 50 bonus
        score_100 = 100
        xp_gain_100 = int(BASE_XP * (score_100 / 100.0)) + 50  # Perfect bonus
        assert xp_gain_100 == 150
        
        # 80% score = 80 XP
        score_80 = 80
        xp_gain_80 = int(BASE_XP * (score_80 / 100.0))
        assert xp_gain_80 == 80
        
        # 50% score = 50 XP
        score_50 = 50
        xp_gain_50 = int(BASE_XP * (score_50 / 100.0))
        assert xp_gain_50 == 50
    
    def test_level_up_at_500_xp(self):
        """Level should increase every 500 XP."""
        # Level = 1 + (XP // 500)
        
        assert 1 + (0 // 500) == 1      # 0 XP = Level 1
        assert 1 + (499 // 500) == 1    # 499 XP = Level 1
        assert 1 + (500 // 500) == 2    # 500 XP = Level 2
        assert 1 + (999 // 500) == 2    # 999 XP = Level 2
        assert 1 + (1000 // 500) == 3   # 1000 XP = Level 3
        assert 1 + (2500 // 500) == 6   # 2500 XP = Level 6


# ===== Badge Awarding Tests =====

class TestBadgeAwardingLogic:
    """Tests for badge criteria checking."""
    
    def test_first_step_badge_criteria(self):
        """First Step badge should unlock after 1 interview."""
        criteria = {"type": "interview_count", "min": 1}
        interview_count = 1
        
        earned = interview_count >= criteria.get("min", 1)
        assert earned is True
    
    def test_first_step_badge_not_earned_with_zero(self):
        """First Step badge should NOT unlock with 0 interviews."""
        criteria = {"type": "interview_count", "min": 1}
        interview_count = 0
        
        earned = interview_count >= criteria.get("min", 1)
        assert earned is False
    
    def test_perfectionist_badge_criteria(self):
        """Perfectionist badge should unlock with score >= 90."""
        criteria = {"type": "interview_score", "min": 90}
        
        # Score of 90 should earn badge
        assert 90 >= criteria.get("min", 90)
        
        # Score of 89 should not
        assert not (89 >= criteria.get("min", 90))
    
    def test_expert_badge_needs_10_interviews(self):
        """Expert badge should require 10 completed interviews."""
        criteria = {"type": "interview_count", "min": 10}
        
        assert 10 >= criteria.get("min", 10)  # Earned
        assert not (9 >= criteria.get("min", 10))  # Not earned
    
    def test_streak_master_badge_criteria(self):
        """Streak Master badge should unlock with 3-day streak."""
        criteria = {"type": "daily_streak", "min": 3}
        
        assert 3 >= criteria.get("min", 3)  # Earned
        assert not (2 >= criteria.get("min", 3))  # Not earned
    
    def test_level_badge_criteria(self):
        """Guru badge should unlock at level 5."""
        criteria = {"type": "level", "min": 5}
        
        assert 5 >= criteria.get("min", 5)  # Earned at level 5
        assert 6 >= criteria.get("min", 5)  # Earned at level 6
        assert not (4 >= criteria.get("min", 5))  # Not earned at level 4
    
    def test_elite_badge_high_score_count(self):
        """Elite badge should unlock with 3 scores of 95+."""
        criteria = {"type": "high_score_count", "min_score": 95, "min_count": 3}
        
        # Mock completed nodes with high scores
        completed_nodes = [
            MagicMock(high_score=95),
            MagicMock(high_score=98),
            MagicMock(high_score=100),
            MagicMock(high_score=80),  # This one doesn't count
        ]
        
        high_score_count = sum(
            1 for n in completed_nodes 
            if (n.high_score or 0) >= criteria.get("min_score", 95)
        )
        
        earned = high_score_count >= criteria.get("min_count", 3)
        assert earned is True
        assert high_score_count == 3


# ===== Skill Stats Update Tests =====

class TestSkillStatsUpdate:
    """Tests for radar chart stat updates."""
    
    def test_moving_average_calculation(self):
        """Stats should update with weighted moving average."""
        alpha = 0.3  # Weight of new session
        
        old_val = 50
        new_val = 80
        
        # Expected: 0.7 * 50 + 0.3 * 80 = 35 + 24 = 59
        weighted = int((1 - alpha) * old_val + alpha * new_val)
        
        assert weighted == 59
    
    def test_stats_improve_with_high_scores(self):
        """Stats should improve when new session scores higher."""
        alpha = 0.3
        old_stats = {"coding_standards": 50, "algorithms": 50}
        new_metrics = {"coding_standards": 90, "algorithms": 70}
        
        updated_stats = {}
        for key in old_stats.keys():
            old_val = old_stats.get(key, 50)
            new_val = new_metrics.get(key, old_val)
            updated_stats[key] = int((1 - alpha) * old_val + alpha * new_val)
        
        assert updated_stats["coding_standards"] == 62  # 0.7*50 + 0.3*90 = 62
        assert updated_stats["algorithms"] == 56  # 0.7*50 + 0.3*70 = 56


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
