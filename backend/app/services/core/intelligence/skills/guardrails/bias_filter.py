"""
Bias Filter Guardrail Skill.

Prevents the AI from asking illegal or discriminatory questions.
Categories: Age, Race, Religion, Politics, Marital Status, Disability (unless relevant to accommodation).
"""
from typing import Dict, Any
from app.services.core.intelligence.skills import BaseSkill

class BiasFilter(BaseSkill):
    def execute(self, context: Dict[str, Any]) -> str:
        # This skill injects a high-priority NEGATIVE constraint.
        
        prompt_injection = """
[SKILL: BIAS FILTER ACTIVE]
CRITICAL LEGAL COMPLIANCE RULES:
You are strictly FORBIDDEN from asking about:
- Age, Date of Birth, or Graduation Years (unless present to verify timeline).
- Marital Status, Children, or Pregnancy.
- Religion, Politics, or Ethnicity.
- Disabilities or Health Conditions.

Focus ONLY on professional competency and diverse work experiences. 
If the candidate volunteers this info, acknowledge politely and pivot back to work.
"""
        return prompt_injection
