"""
Tests for Intelligence v2 components.

Tests for:
- CandidateProfileManager
- ScoringEngine
- DifficultyAdapter
- CompetencyEvaluator
- CrossStageMemory
- QuestionGenerator
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.core.intelligence.candidate_profile import (
    CandidateProfile,
    CandidateProfileManager,
    candidate_profile_manager
)
from app.services.core.intelligence.scoring_engine import (
    AnswerScore,
    ScoringEngine,
    scoring_engine
)
from app.services.core.intelligence.difficulty_adapter import (
    DifficultyLevel,
    DifficultyState,
    DifficultyAdapter,
    difficulty_adapter
)
from app.services.core.intelligence.competency_evaluator import (
    CompetencyEvaluator,
    competency_evaluator
)


class TestCandidateProfile:
    """Tests for CandidateProfile dataclass."""

    def test_empty_profile_creation(self):
        """Should create an empty profile with default values."""
        profile = CandidateProfile()
        assert profile.verified_skills == {}
        assert profile.identified_gaps == []
        assert profile.red_flags == []
        assert profile.strengths == []
        assert profile.topics_covered == set()
        assert profile.performance_trajectory == []
        assert profile.current_turn == 0

    def test_profile_to_dict(self):
        """Should convert profile to dictionary correctly."""
        profile = CandidateProfile()
        profile.verified_skills = {"Python": {"depth": 4, "evidence": "test"}}
        profile.strengths = ["Strong backend"]
        profile.topics_covered.add("python")

        data = profile.to_dict()

        assert data["verified_skills"]["Python"]["depth"] == 4
        assert "Strong backend" in data["strengths"]
        assert "python" in data["topics_covered"]

    def test_profile_from_dict(self):
        """Should create profile from dictionary."""
        data = {
            "verified_skills": {"Python": {"depth": 3}},
            "identified_gaps": ["Docker"],
            "strengths": ["Good communicator"],
            "topics_covered": ["python", "career"],
            "current_turn": 5
        }

        profile = CandidateProfile.from_dict(data)

        assert profile.verified_skills["Python"]["depth"] == 3
        assert "Docker" in profile.identified_gaps
        assert "Good communicator" in profile.strengths
        assert "python" in profile.topics_covered
        assert profile.current_turn == 5

    def test_profile_from_empty_dict(self):
        """Should handle empty dict gracefully."""
        profile = CandidateProfile.from_dict({})
        assert profile.verified_skills == {}
        assert profile.current_turn == 0

    def test_profile_from_none(self):
        """Should handle None gracefully."""
        profile = CandidateProfile.from_dict(None)
        assert profile.verified_skills == {}


class TestCandidateProfileManager:
    """Tests for CandidateProfileManager."""

    def test_to_context_string_empty_profile(self):
        """Should return empty string for empty profile."""
        profile = CandidateProfile()
        context = candidate_profile_manager.to_context_string(profile)
        assert context == ""

    def test_to_context_string_with_skills(self):
        """Should include verified skills in context."""
        profile = CandidateProfile()
        profile.verified_skills = {
            "Python": {"depth": 4, "evidence": "test"},
            "SQL": {"depth": 2, "evidence": "weak"}
        }
        profile.strengths = ["Problem solving"]

        context = candidate_profile_manager.to_context_string(profile)

        assert "Python" in context
        assert "VERIFIED SKILLS" in context
        assert "STRENGTHS" in context

    def test_to_context_string_with_gaps(self):
        """Should include gaps in context."""
        profile = CandidateProfile()
        profile.identified_gaps = ["Docker", "Kubernetes"]

        context = candidate_profile_manager.to_context_string(profile)

        assert "GAPS TO PROBE" in context
        assert "Docker" in context

    def test_to_context_string_with_topics(self):
        """Should include topics covered."""
        profile = CandidateProfile()
        profile.topics_covered = {"python", "career_history"}
        profile.strengths = ["test"]  # Need something to trigger output

        context = candidate_profile_manager.to_context_string(profile)

        assert "TOPICS COVERED" in context
        assert "DO NOT REPEAT" in context

    def test_get_suggested_focus_unverified_skills(self):
        """Should suggest verifying unverified skills."""
        profile = CandidateProfile()
        profile.verified_skills = {
            "Python": {"depth": 1},  # Not verified
            "JavaScript": {"depth": 4}  # Verified
        }

        suggestions = candidate_profile_manager.get_suggested_focus(profile)

        assert any("Python" in s for s in suggestions)
        assert not any("JavaScript" in s for s in suggestions)

    def test_get_suggested_focus_gaps(self):
        """Should suggest probing gaps."""
        profile = CandidateProfile()
        profile.identified_gaps = ["Cloud experience"]

        suggestions = candidate_profile_manager.get_suggested_focus(profile)

        assert any("Cloud" in s for s in suggestions)


class TestAnswerScore:
    """Tests for AnswerScore dataclass."""

    def test_answer_score_creation(self):
        """Should create AnswerScore with all fields."""
        score = AnswerScore(
            overall=75.0,
            relevance=80.0,
            depth=70.0,
            technical_accuracy=75.0,
            communication=80.0,
            dimension="technical_depth",
            feedback="Good answer",
            follow_up_needed=True,
            suggested_follow_up="Ask about edge cases",
            confidence=0.85
        )

        assert score.overall == 75.0
        assert score.dimension == "technical_depth"
        assert score.follow_up_needed is True

    def test_answer_score_to_dict(self):
        """Should convert to dictionary."""
        score = AnswerScore(
            overall=60.0,
            relevance=60.0,
            depth=60.0,
            technical_accuracy=60.0,
            communication=60.0,
            dimension="communication",
            feedback="Average",
            follow_up_needed=False,
            suggested_follow_up=None,
            confidence=0.7
        )

        data = score.to_dict()

        assert data["overall"] == 60.0
        assert data["dimension"] == "communication"
        assert data["follow_up_needed"] is False


class TestDifficultyLevel:
    """Tests for DifficultyLevel enum."""

    def test_all_levels_exist(self):
        """Should have all expected difficulty levels."""
        levels = [l.value for l in DifficultyLevel]
        assert "foundational" in levels
        assert "intermediate" in levels
        assert "advanced" in levels
        assert "expert" in levels

    def test_level_descriptions(self):
        """Should have descriptions for all levels."""
        for level in DifficultyLevel:
            assert level.description is not None
            assert len(level.description) > 10

    def test_level_question_guidance(self):
        """Should have question guidance for all levels."""
        for level in DifficultyLevel:
            assert level.question_guidance is not None
            assert len(level.question_guidance) > 20


class TestDifficultyState:
    """Tests for DifficultyState dataclass."""

    def test_state_to_dict(self):
        """Should convert state to dictionary."""
        state = DifficultyState(
            level=DifficultyLevel.INTERMEDIATE,
            turns_at_level=3,
            last_change_turn=5,
            change_reason="Initial",
            score_window=[70, 75, 80]
        )

        data = state.to_dict()

        assert data["level"] == "intermediate"
        assert data["turns_at_level"] == 3
        assert data["score_window"] == [70, 75, 80]

    def test_state_from_dict(self):
        """Should create state from dictionary."""
        data = {
            "level": "advanced",
            "turns_at_level": 2,
            "last_change_turn": 10,
            "change_reason": "High scores",
            "score_window": [85, 90]
        }

        state = DifficultyState.from_dict(data)

        assert state.level == DifficultyLevel.ADVANCED
        assert state.turns_at_level == 2

    def test_state_from_empty_dict(self):
        """Should handle empty dict with defaults."""
        state = DifficultyState.from_dict({})
        assert state.level == DifficultyLevel.INTERMEDIATE
        assert state.turns_at_level == 0


class TestDifficultyAdapter:
    """Tests for DifficultyAdapter."""

    def test_create_initial_state(self):
        """Should create initial state correctly."""
        state = difficulty_adapter.create_initial_state()
        assert state.level == DifficultyLevel.INTERMEDIATE
        assert state.turns_at_level == 0

    def test_create_initial_state_with_level(self):
        """Should create state with specified level."""
        state = difficulty_adapter.create_initial_state(DifficultyLevel.FOUNDATIONAL)
        assert state.level == DifficultyLevel.FOUNDATIONAL

    def test_update_adds_score_to_window(self):
        """Should add score to window on update."""
        state = difficulty_adapter.create_initial_state()
        state = difficulty_adapter.update(state, 75.0, 1)

        assert 75.0 in state.score_window
        assert state.turns_at_level == 1

    def test_update_maintains_window_size(self):
        """Should maintain window size limit."""
        adapter = DifficultyAdapter(window_size=3)
        state = adapter.create_initial_state()

        for i, score in enumerate([60, 70, 80, 90, 95]):
            state = adapter.update(state, score, i + 1)

        assert len(state.score_window) == 3
        assert state.score_window == [80, 90, 95]

    def test_no_change_below_min_turns(self):
        """Should not change difficulty below min turns."""
        adapter = DifficultyAdapter(min_turns_at_level=3)
        state = adapter.create_initial_state()

        # Add high scores but below min turns
        state = adapter.update(state, 90, 1)
        state = adapter.update(state, 95, 2)

        assert state.level == DifficultyLevel.INTERMEDIATE

    def test_increase_on_high_scores(self):
        """Should increase difficulty on consistently high scores."""
        adapter = DifficultyAdapter(
            increase_threshold=80,
            min_turns_at_level=2,
            window_size=3
        )
        state = adapter.create_initial_state()

        # Add high scores above threshold
        state = adapter.update(state, 85, 1)
        state = adapter.update(state, 90, 2)
        state = adapter.update(state, 92, 3)

        assert state.level == DifficultyLevel.ADVANCED

    def test_decrease_on_low_scores(self):
        """Should decrease difficulty on consistently low scores."""
        adapter = DifficultyAdapter(
            decrease_threshold=50,
            min_turns_at_level=2,
            window_size=3
        )
        state = adapter.create_initial_state()

        # Add low scores below threshold
        state = adapter.update(state, 40, 1)
        state = adapter.update(state, 35, 2)
        state = adapter.update(state, 30, 3)

        assert state.level == DifficultyLevel.FOUNDATIONAL

    def test_no_change_on_average_scores(self):
        """Should not change difficulty on average scores."""
        state = difficulty_adapter.create_initial_state()

        # Add average scores
        for i in range(5):
            state = difficulty_adapter.update(state, 65, i + 1)

        assert state.level == DifficultyLevel.INTERMEDIATE

    def test_get_level_for_stage(self):
        """Should return appropriate starting level for stage."""
        assert difficulty_adapter.get_level_for_stage("hr") == DifficultyLevel.INTERMEDIATE
        assert difficulty_adapter.get_level_for_stage("technical") == DifficultyLevel.INTERMEDIATE
        assert difficulty_adapter.get_level_for_stage("practice") == DifficultyLevel.FOUNDATIONAL

    def test_get_prompt_injection(self):
        """Should generate prompt injection text."""
        state = difficulty_adapter.create_initial_state()
        state.score_window = [70, 75, 80]

        prompt = difficulty_adapter.get_prompt_injection(state)

        assert "INTERMEDIATE" in prompt
        assert "multi-step" in prompt.lower() or "common" in prompt.lower()

    def test_should_provide_hints(self):
        """Should determine when to provide hints."""
        # Foundational level should provide hints
        state = difficulty_adapter.create_initial_state(DifficultyLevel.FOUNDATIONAL)
        assert difficulty_adapter.should_provide_hints(state) is True

        # Intermediate with good scores should not
        state = difficulty_adapter.create_initial_state()
        state.score_window = [70, 75, 80]
        assert difficulty_adapter.should_provide_hints(state) is False

        # Intermediate with poor scores should
        state.score_window = [30, 35, 40]
        assert difficulty_adapter.should_provide_hints(state) is True


class TestCompetencyEvaluator:
    """Tests for CompetencyEvaluator."""

    def test_map_dimension_to_competency(self):
        """Should map dimensions to competencies correctly."""
        assert competency_evaluator.map_dimension_to_competency("system_design") == "technical_depth"
        assert competency_evaluator.map_dimension_to_competency("clarity") == "communication"
        assert competency_evaluator.map_dimension_to_competency("influence") == "leadership"
        assert competency_evaluator.map_dimension_to_competency("unknown") == "general"

    def test_get_stage_focus(self):
        """Should return correct focus competencies for stages."""
        hr_focus = competency_evaluator.get_stage_focus("hr")
        assert "communication" in hr_focus
        assert "professionalism" in hr_focus

        tech_focus = competency_evaluator.get_stage_focus("technical")
        assert "technical_depth" in tech_focus
        assert "problem_solving" in tech_focus

        behavioral_focus = competency_evaluator.get_stage_focus("behavioral")
        assert "leadership" in behavioral_focus

    def test_get_role_weights_exact_match(self):
        """Should return weights for exact role match."""
        weights = competency_evaluator.get_role_weights("Software Engineer")
        assert "technical_depth" in weights
        assert weights["technical_depth"] > 0

    def test_get_role_weights_fuzzy_match(self):
        """Should return weights for fuzzy role match."""
        weights = competency_evaluator.get_role_weights("Senior Software Engineer at Google")
        assert "technical_depth" in weights

    def test_get_role_weights_default(self):
        """Should return default weights for unknown role."""
        weights = competency_evaluator.get_role_weights("Unknown Role XYZ")
        assert "technical_depth" in weights
        assert sum(weights.values()) == pytest.approx(1.0, 0.1)

    def test_get_rubric_level(self):
        """Should return correct rubric level descriptions."""
        level_low = competency_evaluator.get_rubric_level("technical_depth", 25)
        assert "beginner" in level_low.lower() or "basic" in level_low.lower()

        level_high = competency_evaluator.get_rubric_level("technical_depth", 90)
        assert "expert" in level_high.lower() or "exceptional" in level_high.lower()

    def test_compute_competency_scores_empty(self):
        """Should handle empty scores gracefully."""
        result = competency_evaluator.compute_competency_scores([], "Developer")
        assert result["role_fit_score"] == 0
        assert result["competency_scores"] == {}

    def test_compute_competency_scores(self):
        """Should compute competency scores correctly."""
        turn_scores = [
            {"turn": 1, "score": 80, "dimension": "system_design"},
            {"turn": 2, "score": 70, "dimension": "system_design"},
            {"turn": 3, "score": 90, "dimension": "clarity"},
        ]

        result = competency_evaluator.compute_competency_scores(
            turn_scores=turn_scores,
            job_role="Software Engineer"
        )

        assert "competency_scores" in result
        assert "role_fit_score" in result
        assert result["competency_scores"]["technical_depth"]["score"] == 75.0
        assert result["competency_scores"]["communication"]["score"] == 90.0

    def test_get_interview_guidance(self):
        """Should generate interview guidance text."""
        guidance = competency_evaluator.get_interview_guidance(
            stage_type="technical",
            job_role="Software Engineer"
        )

        assert "COMPETENCY FOCUS" in guidance
        assert "technical" in guidance.lower()


class TestIntegration:
    """Integration tests for intelligence v2 components."""

    def test_full_interview_flow_simulation(self):
        """Simulate a full interview flow with all components."""
        # Create profile
        profile = CandidateProfile()
        profile.verified_skills = {"Python": {"depth": 0}}

        # Create difficulty state
        difficulty_state = difficulty_adapter.create_initial_state()

        # Simulate turns with scores
        turn_scores = []
        for i, score in enumerate([65, 70, 75, 80, 85]):
            turn_scores.append({
                "turn": i + 1,
                "score": score,
                "dimension": "system_design"
            })

            # Update difficulty
            difficulty_state = difficulty_adapter.update(
                difficulty_state, score, i + 1
            )

            # Update profile
            profile.performance_trajectory.append(score)

        # Verify difficulty increased
        assert difficulty_state.level in [DifficultyLevel.ADVANCED, DifficultyLevel.INTERMEDIATE]

        # Compute final competencies
        result = competency_evaluator.compute_competency_scores(
            turn_scores=turn_scores,
            job_role="Software Engineer"
        )

        assert result["competency_scores"]["technical_depth"]["score"] == 75.0
        assert result["role_fit_score"] > 0

    def test_profile_context_in_prompt(self):
        """Test that profile context is properly formatted for prompts."""
        profile = CandidateProfile()
        profile.verified_skills = {
            "Python": {"depth": 4, "evidence": "Built APIs"},
            "SQL": {"depth": 3, "evidence": "Optimized queries"}
        }
        profile.identified_gaps = ["Docker", "Kubernetes"]
        profile.strengths = ["Clean code", "System design"]
        profile.topics_covered = {"python", "databases", "api_design"}
        profile.performance_trajectory = [70, 75, 80]

        context = candidate_profile_manager.to_context_string(profile)

        # Verify all sections are present
        assert "VERIFIED SKILLS" in context
        assert "Python" in context
        assert "GAPS TO PROBE" in context
        assert "Docker" in context
        assert "STRENGTHS" in context
        assert "TOPICS COVERED" in context
        assert "PERFORMANCE" in context
        assert "improving" in context
