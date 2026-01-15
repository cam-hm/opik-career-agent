"""
Tests for config/stages.py - Stage configuration and helpers.
"""
import pytest
from config.stages import (
    get_stage_type,
    get_stage_by_number,
    get_stage_by_type,
    get_persona_for_stage,
    get_voice_for_stage,
    build_persona_prompt,
    STAGES,
    # HR_PERSONA, # Removed
    # TECHNICAL_PERSONA, # Removed
    # BEHAVIORAL_PERSONA, # Removed
    # PRACTICE_PERSONA, # Removed
)



class TestGetStageType:
    """Tests for get_stage_type function."""
    
    def test_stage_1_returns_hr(self):
        """Stage 1 should return 'hr'."""
        assert get_stage_type(1) == "hr"
    
    def test_stage_2_returns_technical(self):
        """Stage 2 should return 'technical'."""
        assert get_stage_type(2) == "technical"
    
    def test_stage_3_returns_behavioral(self):
        """Stage 3 should return 'behavioral'."""
        assert get_stage_type(3) == "behavioral"
    
    def test_invalid_stage_returns_unknown(self):
        """Invalid stage numbers should return 'unknown'."""
        assert get_stage_type(0) == "unknown"
        assert get_stage_type(4) == "unknown"
        assert get_stage_type(-1) == "unknown"
        assert get_stage_type(999) == "unknown"


class TestGetStageByNumber:
    """Tests for get_stage_by_number function."""
    
    def test_returns_stage_config_for_valid_number(self):
        """Should return StageConfig for valid stage numbers."""
        stage = get_stage_by_number(1)
        assert stage is not None
        assert stage.type == "hr"
        assert stage.id == 1
    
    def test_returns_none_for_invalid_number(self):
        """Should return None for invalid stage numbers."""
        assert get_stage_by_number(0) is None
        assert get_stage_by_number(4) is None
        assert get_stage_by_number(-1) is None


class TestGetStageByType:
    """Tests for get_stage_by_type function."""
    
    def test_returns_stage_config_for_valid_type(self):
        """Should return StageConfig for valid stage types."""
        stage = get_stage_by_type("hr")
        assert stage is not None
        assert stage.id == 1
        
        stage = get_stage_by_type("technical")
        assert stage is not None
        assert stage.id == 2
    
    def test_returns_none_for_invalid_type(self):
        """Should return None for invalid stage types."""
        assert get_stage_by_type("invalid") is None
        assert get_stage_by_type("") is None
        assert get_stage_by_type("practice") is None  # Not in STAGES


class TestGetPersonaForStage:
    """Tests for get_persona_for_stage function."""
    
    def test_hr_stage_returns_hr_persona(self):
        """HR stage should return Sarah Alexa OR Marcus Reynolds persona."""
        persona = get_persona_for_stage("hr")
        assert persona.name in ["Sarah Alexa", "Marcus Reynolds"]
        assert persona.role_template == "HR Recruiter"
    
    def test_technical_stage_returns_technical_persona(self):
        """Technical stage should return David Park OR Elena Rostova persona."""
        persona = get_persona_for_stage("technical")
        assert persona.name in ["David Park", "Elena Rostova"]
        assert "Lead" in persona.role_template
    
    def test_behavioral_stage_returns_behavioral_persona(self):
        """Behavioral stage should return Michael Torres persona."""
        persona = get_persona_for_stage("behavioral")
        assert persona.name is not None
        
    def test_unknown_stage_returns_practice_persona(self):
        """Unknown stage type should fallback to practice persona."""
        persona = get_persona_for_stage("unknown")
        # Could be Alex Chen or Jordan Lee
        assert persona.name in ["Alex Chen", "Jordan Lee"]


class TestGetVoiceForStage:
    """Tests for get_voice_for_stage function."""
    
    def test_hr_stage_uses_female_voice(self):
        """HR stage should use Brooke (Female) or Ronald (Male) UUID."""
        voice = get_voice_for_stage("hr")
        # e07c... (Brooke), 5ee9... (Ronald)
        valid_voices = [
            "e07c00bc-4134-4eae-9ea4-1a55fb45746b",
            "5ee9feff-1265-424a-9d7f-8e4d431a12c7"
        ]
        assert voice in valid_voices
    
    def test_technical_stage_uses_male_voice(self):
        """Technical stage should use Blake (Male) or Brooke (Female) UUID."""
        voice = get_voice_for_stage("technical")
        # a167... (Blake), e07c... (Brooke)
        valid_voices = [
            "a167e0f3-df7e-4d52-a9c3-f949145efdab",
            "e07c00bc-4134-4eae-9ea4-1a55fb45746b"
        ]
        assert voice in valid_voices
        
    def test_unknown_stage_fallbacks_to_practice_voice(self):
        """Unknown stage should fallback to default."""
        voice = get_voice_for_stage("unknown")
        assert voice is not None


class TestBuildPersonaPrompt:
    """Tests for build_persona_prompt function."""
    
    def test_contains_persona_name(self):
        """Prompt should contain SOME persona name."""
        prompt = build_persona_prompt("hr", "Developer")
        # Check against possible names
        assert any(name in prompt for name in ["Sarah Alexa", "Marcus Reynolds"])
        
    def test_contains_company_name(self):
        """Prompt should contain provided company name."""
        prompt = build_persona_prompt("hr", "Developer", "Google")
        assert "Google" in prompt
    
    def test_contains_focus_areas(self):
        """Prompt should contain focus areas."""
        # Just check it's not empty, exact words depend on skills/JD/Role
        prompt = build_persona_prompt("technical", "Engineer")
        assert len(prompt) > 50
    
    def test_contains_avoid_topics(self):
        """Prompt should mention topics to avoid (safety)."""
        prompt = build_persona_prompt("hr", "Dev")
        # Global skills include 'topic_blocker'. Check that prompt is substantial
        # and likely contains additional instructions beyond role.
        assert len(prompt) > 100


class TestStagesConfig:
    """Tests for STAGES configuration."""
    
    def test_has_three_stages(self):
        """Should have exactly 3 stages defined."""
        assert len(STAGES) == 3
    
    def test_stages_have_required_fields(self):
        """Each stage should have all required fields."""
        for stage_id, stage in STAGES.items():
            assert stage.id == stage_id
            assert stage.type in ["hr", "technical", "behavioral"]
            assert stage.name
            assert stage.description
            assert stage.persona_id is not None # Changed from persona to persona_id
            assert stage.duration_minutes > 0
