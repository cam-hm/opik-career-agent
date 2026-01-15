"""
Interview stage configuration.
BACKWARD COMPATIBILITY BRIDGE.
Delegates to core.intelligence.stage_manager.
"""
from typing import Optional, Any
from app.services.core.intelligence.stage_manager import stage_manager

# Re-exporting basic types if needed by other modules, 
# but mostly we just need the functions.

def get_stage_by_number(stage_number: int) -> Optional[Any]:
    """Get stage configuration by stage number (1, 2, 3)."""
    return stage_manager.get_stage_by_number(stage_number)

def get_stage_by_type(stage_type: str) -> Optional[Any]:
    """Get stage configuration by type (hr, technical, behavioral)."""
    return stage_manager.get_stage_by_type(stage_type)

def get_stage_type(stage_number: int) -> str:
    """Get stage type string from stage number."""
    return stage_manager.get_stage_type(stage_number)

# ===== Legacy Functions (Deprecated but kept for safety) =====

def get_voice_for_stage(stage_type: str, language: str = "en") -> str:
    """Deprecated: Use prompt_manager.get_voice_model() instead."""
    # This is a temporary bridge if any old code still calls it
    from app.services.core.intelligence.prompt_manager import prompt_manager
    return prompt_manager.get_voice_model(stage_type, language)


def get_persona_for_stage(stage_type: str):
    """Deprecated: Use prompt_manager directly."""
    from app.services.core.intelligence.prompt_manager import prompt_manager, STAGE_PERSONA_MAP
    from types import SimpleNamespace
    
    # Get persona key from map
    persona_key = STAGE_PERSONA_MAP.get(stage_type, "practice_interviewer")
    
    # Load Dict 
    persona_dict = prompt_manager._load_persona(persona_key)
    
    # Resolve default identity to populate 'name' and 'voice' at the root level
    # This mimics the structure expected by legacy code/tests
    identity = prompt_manager._resolve_identity(persona_dict)
    
    # Create a copy to avoid mutating cache
    combined = persona_dict.copy()
    combined.update(identity)
    
    return SimpleNamespace(**combined)

def build_persona_prompt(stage_type: str, job_role: str, company_name: str = "TechVision") -> str:
    """Deprecated: Use prompt_manager.get_system_instruction() instead."""
    # This is a temporary bridge
    from app.services.core.intelligence.prompt_manager import prompt_manager
    context = f"You are interviewing for a {job_role} position."
    return prompt_manager.get_system_instruction(stage_type, job_role, context_info=context, company_name=company_name)

# Backward compatibility for STAGES constant
STAGES = stage_manager.stages

