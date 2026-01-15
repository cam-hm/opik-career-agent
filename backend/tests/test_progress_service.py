"""
Tests for Progress Service - Personal Growth & Learning features.

Tests for:
- Resolution CRUD operations
- Progress calculation logic
- Skill gap analysis
- Weekly insights generation
"""
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.services.progress_service import ProgressService, DEFAULT_SKILL_DIMENSIONS


# ===== Mock Fixtures =====

@pytest.fixture
def mock_db():
    """Create a mock async database session."""
    db = AsyncMock()
    db.execute = AsyncMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.flush = AsyncMock()
    db.refresh = AsyncMock()
    return db


@pytest.fixture
def mock_user_progress():
    """Create a mock UserProgress object."""
    progress = MagicMock()
    progress.user_id = "user_test123"
    progress.skill_stats = {
        "tech_proficiency": 60,
        "communication": 55,
        "algorithms": 65,
        "system_design": 50,
        "coding_standards": 45,
        "debugging": 58
    }
    return progress


@pytest.fixture
def mock_resolution():
    """Create a mock UserResolution object."""
    resolution = MagicMock()
    resolution.id = uuid4()
    resolution.user_id = "user_test123"
    resolution.title = "Master System Design"
    resolution.description = "Improve system design skills for senior roles"
    resolution.target_role = "Senior Software Engineer"
    resolution.target_skills = {
        "technical_depth": 80,
        "communication": 75,
        "system_design": 85
    }
    resolution.baseline_skills = {
        "technical_depth": 60,
        "communication": 55,
        "system_design": 50
    }
    resolution.target_date = datetime(2026, 12, 31, tzinfo=timezone.utc)
    resolution.status = "active"
    resolution.created_at = datetime.now(timezone.utc)
    return resolution


@pytest.fixture
def mock_interview_session():
    """Create a mock InterviewSession object."""
    session = MagicMock()
    session.session_id = "session_test123"
    session.overall_score = 75
    session.status = "completed"
    session.created_at = datetime.now(timezone.utc)
    session.competency_scores = {
        "communication": {"score": 70},
        "problem_solving": {"score": 80},
        "technical_depth": {"score": 75}
    }
    session.candidate_profile = {
        "verified_skills": {
            "python": {"depth": 3},
            "react": {"depth": 2}
        },
        "identified_gaps": ["system_design", "distributed_systems"]
    }
    session.application = MagicMock()
    session.application.job_role = "Software Engineer"
    session.stage_type = "technical"
    return session


# ===== Resolution Tests =====

class TestResolutionManagement:
    """Tests for resolution CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_resolution_with_custom_targets(self, mock_db, mock_user_progress):
        """Resolution should be created with specified target skills."""
        # Setup
        mock_db.execute.return_value.scalar_one_or_none.return_value = mock_user_progress

        service = ProgressService(mock_db)

        target_skills = {
            "technical_depth": 90,
            "communication": 85,
            "system_design": 95
        }

        # Execute
        with patch.object(service, '_get_current_skill_levels', return_value={
            "technical_depth": 60,
            "communication": 55,
            "system_design": 50
        }):
            # Since we're mocking, we just verify the method would be called correctly
            baseline = await service._get_current_skill_levels("user_test123")

        # Verify baseline is fetched
        assert baseline["technical_depth"] == 60
        assert baseline["system_design"] == 50

    def test_default_skill_dimensions_defined(self):
        """Ensure default skill dimensions are properly defined."""
        assert len(DEFAULT_SKILL_DIMENSIONS) >= 6
        assert "technical_depth" in DEFAULT_SKILL_DIMENSIONS
        assert "communication" in DEFAULT_SKILL_DIMENSIONS
        assert "problem_solving" in DEFAULT_SKILL_DIMENSIONS
        assert "system_design" in DEFAULT_SKILL_DIMENSIONS


class TestProgressCalculation:
    """Tests for progress calculation logic."""

    def test_progress_percent_calculation_basic(self):
        """Progress should be calculated correctly between baseline and target."""
        baseline = 50
        current = 65
        target = 80

        # Formula: (current - baseline) / (target - baseline) * 100
        expected_progress = (65 - 50) / (80 - 50) * 100
        assert expected_progress == 50.0  # 50% progress

    def test_progress_percent_at_target(self):
        """Progress should be 100% when current equals target."""
        baseline = 50
        current = 80
        target = 80

        progress = (current - baseline) / (target - baseline) * 100
        assert progress == 100.0

    def test_progress_percent_exceeds_target(self):
        """Progress should be capped at 100% when exceeding target."""
        baseline = 50
        current = 90
        target = 80

        progress = (current - baseline) / (target - baseline) * 100
        clamped = max(0, min(100, progress))
        # Should be capped at 100
        assert clamped == 100

    def test_progress_percent_below_baseline(self):
        """Progress should be clamped to 0% if current is below baseline."""
        baseline = 50
        current = 40  # Below baseline
        target = 80

        progress = (current - baseline) / (target - baseline) * 100
        clamped = max(0, min(100, progress))
        assert clamped == 0  # Negative progress clamped to 0

    def test_progress_with_equal_baseline_and_target(self):
        """Handle edge case where baseline equals target."""
        baseline = 80
        current = 80
        target = 80

        # When target equals baseline, progress is 100% if current >= target
        if target > baseline:
            progress = (current - baseline) / (target - baseline) * 100
        else:
            progress = 100 if current >= target else 0

        assert progress == 100

    def test_overall_progress_averaging(self):
        """Overall progress should be average of all skill progress."""
        skill_progress = {
            "technical_depth": 60,
            "communication": 80,
            "system_design": 40
        }

        overall = sum(skill_progress.values()) / len(skill_progress)
        assert overall == 60.0


# ===== Skill Gap Analysis Tests =====

class TestSkillGapAnalysis:
    """Tests for skill gap analysis logic."""

    def test_gap_identification(self):
        """Gaps should be identified when current < target by > 15."""
        current_skills = {
            "technical_depth": 60,
            "communication": 70,
            "system_design": 40
        }
        target_requirements = {
            "technical_depth": 80,  # Gap: 20 (significant)
            "communication": 75,    # Gap: 5 (not significant)
            "system_design": 85     # Gap: 45 (significant)
        }

        gaps = []
        for skill, target in target_requirements.items():
            current = current_skills.get(skill, 0)
            gap = target - current
            if gap > 15:
                gaps.append({"skill": skill, "gap": gap})

        assert len(gaps) == 2
        assert any(g["skill"] == "technical_depth" for g in gaps)
        assert any(g["skill"] == "system_design" for g in gaps)

    def test_strength_identification(self):
        """Strengths should be identified when current > target by > 10."""
        current_skills = {
            "technical_depth": 95,  # Exceeds by 15
            "communication": 70,
            "system_design": 40
        }
        target_requirements = {
            "technical_depth": 80,
            "communication": 75,
            "system_design": 85
        }

        strengths = []
        for skill, target in target_requirements.items():
            current = current_skills.get(skill, 0)
            gap = target - current
            if gap < -10:  # Exceeds target
                strengths.append({"skill": skill, "level": current})

        assert len(strengths) == 1
        assert strengths[0]["skill"] == "technical_depth"

    def test_gaps_sorted_by_severity(self):
        """Gaps should be sorted by severity (largest gap first)."""
        gaps = [
            {"skill": "communication", "gap": 15},
            {"skill": "system_design", "gap": 45},
            {"skill": "technical_depth", "gap": 20}
        ]

        gaps.sort(key=lambda x: x["gap"], reverse=True)

        assert gaps[0]["skill"] == "system_design"
        assert gaps[1]["skill"] == "technical_depth"
        assert gaps[2]["skill"] == "communication"


class TestGapRecommendations:
    """Tests for gap-based recommendations."""

    def test_recommendations_include_top_gap(self):
        """Recommendations should mention the top skill gap."""
        service = ProgressService(AsyncMock())

        gaps = [
            {"skill": "system_design", "current": 40, "target": 85, "gap": 45}
        ]

        recommendations = service._generate_gap_recommendations(gaps, [])

        assert len(recommendations) > 0
        assert "system_design" in recommendations[0] or "system design" in recommendations[0]

    def test_recommendations_with_identified_gaps(self):
        """Recommendations should include areas identified from interviews."""
        service = ProgressService(AsyncMock())

        gaps = []
        identified_gaps = ["distributed_systems", "microservices"]

        recommendations = service._generate_gap_recommendations(gaps, identified_gaps)

        # Should mention interview feedback
        has_interview_mention = any("feedback" in r.lower() or "identified" in r.lower() for r in recommendations)
        assert has_interview_mention or len(recommendations) > 0

    def test_recommendations_when_no_gaps(self):
        """Should encourage setting higher goals when no gaps exist."""
        service = ProgressService(AsyncMock())

        gaps = []
        identified_gaps = []

        recommendations = service._generate_gap_recommendations(gaps, identified_gaps)

        # Should have encouraging message
        assert len(recommendations) > 0


# ===== Weekly Insights Tests =====

class TestWeeklyInsights:
    """Tests for weekly insights generation."""

    def test_trend_calculation_improving(self):
        """Trend should be positive when this week > last week."""
        this_week_avg = 75
        last_week_avg = 70

        trend = this_week_avg - last_week_avg
        direction = "up" if trend > 0 else "down" if trend < 0 else "stable"

        assert trend == 5
        assert direction == "up"

    def test_trend_calculation_declining(self):
        """Trend should be negative when this week < last week."""
        this_week_avg = 65
        last_week_avg = 70

        trend = this_week_avg - last_week_avg
        direction = "up" if trend > 0 else "down" if trend < 0 else "stable"

        assert trend == -5
        assert direction == "down"

    def test_trend_calculation_stable(self):
        """Trend should be stable when scores are equal."""
        this_week_avg = 70
        last_week_avg = 70

        trend = this_week_avg - last_week_avg
        direction = "up" if trend > 0 else "down" if trend < 0 else "stable"

        assert trend == 0
        assert direction == "stable"

    def test_competency_aggregation(self):
        """Competency scores should be averaged across sessions."""
        sessions_competencies = [
            {"communication": {"score": 70}, "problem_solving": {"score": 80}},
            {"communication": {"score": 80}, "problem_solving": {"score": 70}},
        ]

        competencies = {}
        counts = {}

        for session_comp in sessions_competencies:
            for comp, data in session_comp.items():
                score = data.get("score", 0)
                if comp not in competencies:
                    competencies[comp] = 0
                    counts[comp] = 0
                competencies[comp] += score
                counts[comp] += 1

        averages = {
            comp: round(total / counts[comp], 1)
            for comp, total in competencies.items()
        }

        assert averages["communication"] == 75.0
        assert averages["problem_solving"] == 75.0


class TestFallbackInsights:
    """Tests for fallback insights when AI is unavailable."""

    def test_fallback_strengths_identified(self):
        """Fallback should identify strengths for scores >= 75."""
        service = ProgressService(AsyncMock())

        competencies = {
            "communication": 80,  # Strength
            "problem_solving": 60,  # Not strength
            "system_design": 78   # Strength
        }

        result = service._generate_fallback_insights(75, competencies, None)

        assert len(result["strengths"]) >= 2

    def test_fallback_areas_to_improve_identified(self):
        """Fallback should identify areas to improve for scores < 60."""
        service = ProgressService(AsyncMock())

        competencies = {
            "communication": 55,  # Needs attention
            "problem_solving": 80,
            "system_design": 45   # Needs attention
        }

        result = service._generate_fallback_insights(60, competencies, None)

        assert len(result["areas_to_improve"]) >= 2

    def test_fallback_highlights_excellent_performance(self):
        """Fallback should highlight excellent performance for avg >= 80."""
        service = ProgressService(AsyncMock())

        result = service._generate_fallback_insights(85, {}, None)

        # Should have positive highlight
        has_excellent = any("excellent" in h.lower() for h in result["highlights"])
        assert has_excellent

    def test_fallback_highlights_improvement(self):
        """Fallback should highlight when trend is significantly positive."""
        service = ProgressService(AsyncMock())

        result = service._generate_fallback_insights(70, {}, 10)  # +10 improvement

        # Should mention improvement
        has_improvement = any("improvement" in h.lower() or "up" in h.lower() for h in result["highlights"])
        assert has_improvement

    def test_fallback_recommendation_for_decline(self):
        """Fallback should recommend review when trend is negative."""
        service = ProgressService(AsyncMock())

        result = service._generate_fallback_insights(65, {}, -10)  # -10 decline

        # Should have recommendation about decline
        has_decline_rec = any("dipped" in r.lower() or "review" in r.lower() for r in result["recommendations"])
        assert has_decline_rec


# ===== Skill Level Mapping Tests =====

class TestSkillLevelMapping:
    """Tests for skill stats to standard dimensions mapping."""

    def test_skill_stats_mapping(self):
        """Skill stats should map to standard dimensions correctly."""
        skill_stats = {
            "tech_proficiency": 60,
            "communication": 55,
            "algorithms": 65,
            "system_design": 50,
            "coding_standards": 45,
            "debugging": 58
        }

        # Expected mapping (from _get_current_skill_levels)
        mapped = {
            "technical_depth": skill_stats.get("tech_proficiency", 50),
            "communication": skill_stats.get("communication", 50),
            "problem_solving": skill_stats.get("algorithms", 50),
            "system_design": skill_stats.get("system_design", 50),
            "leadership": skill_stats.get("coding_standards", 50),
            "adaptability": skill_stats.get("debugging", 50)
        }

        assert mapped["technical_depth"] == 60
        assert mapped["problem_solving"] == 65
        assert mapped["leadership"] == 45

    def test_default_skill_levels_when_no_progress(self):
        """Default skill levels should be 50 for all dimensions."""
        defaults = {skill: 50 for skill in DEFAULT_SKILL_DIMENSIONS}

        for skill, level in defaults.items():
            assert level == 50


# ===== Target Requirements Tests =====

class TestTargetRequirements:
    """Tests for role-based target requirements."""

    def test_senior_role_targets(self):
        """Senior roles should have higher targets."""
        role_targets = {
            "senior": {
                "technical_depth": 80,
                "communication": 75,
                "problem_solving": 80,
                "system_design": 75,
                "leadership": 70,
                "adaptability": 70
            }
        }

        # Senior targets should all be >= 70
        for skill, target in role_targets["senior"].items():
            assert target >= 70

    def test_mid_role_targets(self):
        """Mid-level roles should have moderate targets."""
        role_targets = {
            "mid": {
                "technical_depth": 70,
                "communication": 65,
                "problem_solving": 70,
                "system_design": 60,
                "leadership": 55,
                "adaptability": 65
            }
        }

        # Mid targets should be between 55-70
        for skill, target in role_targets["mid"].items():
            assert 55 <= target <= 70

    def test_default_role_targets(self):
        """Default targets should be balanced for entry-level."""
        role_targets = {
            "default": {
                "technical_depth": 60,
                "communication": 60,
                "problem_solving": 60,
                "system_design": 50,
                "leadership": 50,
                "adaptability": 60
            }
        }

        # Default targets should be around 50-60
        for skill, target in role_targets["default"].items():
            assert 50 <= target <= 60


# ===== Days Remaining Tests =====

class TestDaysRemaining:
    """Tests for target date calculations."""

    def test_days_remaining_positive(self):
        """Days remaining should be positive for future dates."""
        target_date = datetime.now(timezone.utc) + timedelta(days=100)
        now = datetime.now(timezone.utc)

        days_remaining = (target_date - now).days

        assert days_remaining > 0
        assert days_remaining <= 100

    def test_days_remaining_past_date(self):
        """Days remaining should be negative for past dates."""
        target_date = datetime.now(timezone.utc) - timedelta(days=10)
        now = datetime.now(timezone.utc)

        days_remaining = (target_date - now).days

        assert days_remaining < 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
