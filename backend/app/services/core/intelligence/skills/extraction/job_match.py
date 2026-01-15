"""
Job Match Evaluator Skill.

Compares Resume vs Job Description to generate targeted interview angles.
Versatility: Uses randomized strategies (Gap Hunter, Amplifier, etc.)
"""
from typing import Dict, Any
import random
from app.services.core.intelligence.skills import BaseSkill

class JobMatchEvaluator(BaseSkill):
    def execute(self, context: Dict[str, Any]) -> str:
        resume_text = context.get("resume_text", "")
        job_description = context.get("job_description", "")
        
        # If missing critical context, skip
        if not resume_text or not job_description or len(job_description) < 20:
            return ""

        # Strategy Roulette: Different ways to compare the two documents
        strategies = [
            """
            STRATEGY: THE GAP HUNTER (Missing Requirements)
            - Compare the Job Description (JD) requirements against the Resume.
            - Identify 1 critical technical skill from the JD that is MISSING or weak in the Resume.
            - Ask: "I see this role requires [Missing Skill], but I don't see much of it in your background. Can you explain your experience with it?"
            """,
            """
            STRATEGY: THE STRENGTH AMPLIFIER (Core Competencies)
            - Identify the STRONGEST match between the Resume and JD.
            - Ask a high-level "System Design" or "Best Practice" question related to that shared strength.
            - Example: "You have great experience in X (which we need). What is your opinion on the future of X?"
            """,
            """
            STRATEGY: THE REALIST (Day-to-Day)
            - Look at the "Responsibilities" section of the JD.
            - Ask: "One of the key responsibilities here is [Responsibility]. Give me an example of a time you handled something similar."
            """,
            """
            STRATEGY: THE ADAPTABILITY CHECK
            - If the JD mentions a specific industry (e.g., Fintech, Health), check if the candidate has it.
            - If they DON'T, ask: "This role is in the [Industry] domain. How would you adapt your skills to this specific field?"
            """
        ]
        
        mode = self.config.get("mode", "balanced")
        selected_strategy = random.choice(strategies)
        
        prompt_injection = f"""
[SKILL: JOB MATCH EVALUATOR ACTIVE]
Mode: {mode.upper()}

You have the Job Description (JD).
Your goal is to assess the FIT between the Candidate and the Role.
To keep the assessment dynamic, use this specific comparison strategy:

{selected_strategy}

Context - Job Description:
{job_description[:2000]}...
"""
        return prompt_injection
