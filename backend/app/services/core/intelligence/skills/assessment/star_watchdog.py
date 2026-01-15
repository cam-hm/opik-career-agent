"""
STAR Method Watchdog Skill.

Assessment skill that validates if a candidate's answer follows the STAR framework:
- Situation
- Task
- Action
- Result

If the candidate misses a part (especially 'Result'), this skill prompts the AI to dig deeper.
"""
from typing import Dict, Any
from app.services.core.intelligence.skills import BaseSkill

class StarWatchdog(BaseSkill):
    def execute(self, context: Dict[str, Any]) -> str:
        # This skill works best when we have the *current* transcript context, 
        # but for the MVP prompt injection, we set a "Listening Mode".
        
        prompt_injection = """
[SKILL: STAR METHOD WATCHDOG ACTIVE]
Mode: LISTENING_FOR_STRUCTURE

As the candidate matches their story, check for the STAR components:
1. Situation/Task (The Context)
2. Action (What THEY specifically did)
3. Result (The Outcome/Metrics)

IF they finish their story and missed 'Action' (used "we" too much) -> Ask: "What was YOUR specific role in that?"
IF they finish their story and missed 'Result' -> Ask: "What was the final outcome or impact of that?"
"""
        return prompt_injection
