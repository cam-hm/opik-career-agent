"""
Sales Objection Simulator Skill.

Simulation skill that forces the AI into a Roleplay Scenario.
The AI adopts the persona of a skeptical client to test negotiation skills.
"""
from typing import Dict, Any
import random
from app.services.core.intelligence.skills import BaseSkill

class SalesObjectionSimulator(BaseSkill):
    def execute(self, context: Dict[str, Any]) -> str:
        # Determine the difficulty/mood of the client
        scenarios = [
            "OBJECTION: PRICE - Say: 'I like the product, but it's 20% more expensive than the competitor. Why should I pay more?'",
            "OBJECTION: AUTHORITY - Say: 'I'm not the decision maker, and my boss hates changing vendors. Give me something to convince him.'",
            "OBJECTION: TIMING - Say: 'We are freezing budget until Q4. Why should we buy now?'",
            "OBJECTION: TRUST - Say: 'I've heard your support is terrible. Convince me otherwise.'"
        ]
        
        selected_scenario = random.choice(scenarios)
        
        prompt_injection = f"""
[SKILL: SALES SIMULATION ACTIVE]
Mode: ROLEPLAY_OBJECTION

You are NO LONGER just an interviewer. You are a SKEPTICAL PROSPECT.
Do not accept their first answer easily. Push back once.

Your current Objection Scenario:
{selected_scenario}

Evaluate how they handle the pressure. Do they listen? Do they empathize? Or do they argue?
"""
        return prompt_injection
