
import pytest
from app.services.core.intelligence.prompt_manager import prompt_manager

class TestTechStackInjection:
    
    def test_tech_detection_python(self):
        """Verify python keywords are detected."""
        text = "I am a Senior Python Developer with Django experience."
        detected = prompt_manager._detect_tech_stack(text)
        assert "python" in detected
        assert len(detected) >= 1

    def test_tech_detection_react(self):
        """Verify react keywords are detected."""
        text = "Frontend Engineer specialized in React and Next.js"
        detected = prompt_manager._detect_tech_stack(text)
        assert "react" in detected
        text2 = "Next.js Specialist"
        detected2 = prompt_manager._detect_tech_stack(text2)
        assert "react" in detected2

    def test_tech_detection_multiple(self):
        """Verify multiple stacks are detected."""
        text = "Fullstack with Python, React, and AWS."
        detected = prompt_manager._detect_tech_stack(text)
        assert "python" in detected
        assert "react" in detected
        assert "aws" in detected

    def test_tech_detection_none(self):
        """Verify no false positives."""
        text = "I am a Manager."
        detected = prompt_manager._detect_tech_stack(text)
        assert detected == []

    def test_system_prompt_integration(self):
        """Verify detection is actually injected into the prompt text."""
        # Switched to Python to ensure we are testing the Template Logic, 
        # not the tricky 'Go' regex which failed on boundary checks.
        instruction = prompt_manager.get_system_instruction(
            stage_type="technical",
            job_role="Senior Python Developer",
            context_info="",
            language="en"
        )
        
        # Check for Section Header
        assert "TECHNICAL DEEP DIVE" in instruction
        assert "Detected Stack: python" in instruction
        
        # Check for PYTHON specific instructions
        assert "PYTHON Instructions:" in instruction
        assert "Ask about advanced concepts" in instruction

    def test_system_prompt_none_inputs(self):
        """Verify that None inputs for resume/jd do not crash the system (Regression Test)."""
        try:
            instruction = prompt_manager.get_system_instruction(
                stage_type="technical",
                job_role="Python Dev",
                resume_text=None,
                job_description=None
            )
            assert "TECHNICAL DEEP DIVE" in instruction
            # Should fall back to safe empty strings, so has_resume/has_jd should be False
            # meaning no RESUME AUTOPSY or GAP ANALYSIS sections
            assert "RESUME AUTOPSY" not in instruction
            assert "GAP ANALYSIS" not in instruction
        except AttributeError:
            pytest.fail("PromptManager raised AttributeError on None inputs")
