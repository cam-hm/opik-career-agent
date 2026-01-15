"""
Prompt Manager Module.

Central intelligence controller that:
1. Loads Persona definitions from YAML.
4. Central intelligence controller that:
5. 1. Loads Persona definitions from YAML.
6. 2. Resolves Identity (Name/Voice) based on Session ID.
7. 3. Renders Jinja2 templates for System Instructions and Greetings.
8. 4. Manages language and voice selection.
"""
import os
import yaml
import random
import logging
from typing import Dict, Any, List
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path

from app.services.core.intelligence.skills.registry import skill_registry

logger = logging.getLogger("prompt-manager")

# Map stage types to persona filenames
STAGE_PERSONA_MAP = {
    "hr": "hr_recruiter",
    "technical": "tech_lead",
    "behavioral": "behavioral_manager",
    "practice": "practice_interviewer"
}

# Skills that apply to EVERY persona (Safety & Security)
GLOBAL_SKILLS = [
    {"id": "bias_filter"},
    {"id": "topic_blocker"}
]

# Define TEMPLATES_DIR as a Path object relative to the current file
TEMPLATES_DIR = Path(__file__).parent / "templates"

class PromptManager:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.personas_dir = os.path.join(self.base_dir, "personas")
        self.templates_dir = str(TEMPLATES_DIR)
        
        # Initialize Jinja2 Env
        self.env = Environment(
            loader=FileSystemLoader(self.templates_dir),
            autoescape=select_autoescape(['html', 'xml', 'j2']) # Updated autoescape
        )
        
        # Cache for loaded personas
        self.persona_cache: Dict[str, Any] = {}
        
        self._load_intelligence_config() # Load intelligence config
        logger.info(f"Loaded {len(self.persona_cache)} personas") # This line might be misleading if personas aren't loaded yet. Keeping as per instruction.
        
    def _load_intelligence_config(self):
        """Load Data-Driven Intelligence Configuration."""
        from config.settings import settings
        config_path = settings.base_path / "config" / "intelligence.yaml"
        try:
            with open(config_path, "r") as f:
                self.config = yaml.safe_load(f)
                logger.info("Intelligence Config Loaded Successfully")
        except Exception as e:
            logger.error(f"Failed to load intelligence config: {e}")
            # Fallback to empty to prevent crash, though logic might fail
            self.config = {"tech_stacks": {}, "strategies": {}}

    def _load_persona(self, persona_name: str) -> Dict[str, Any]:
        """Load persona YAML from disk with caching."""
        if persona_name in self.persona_cache:
            return self.persona_cache[persona_name]
            
        file_path = os.path.join(self.personas_dir, f"{persona_name}.yaml")
        try:
            with open(file_path, "r") as f:
                data = yaml.safe_load(f)
                self.persona_cache[persona_name] = data
                return data
        except FileNotFoundError:
            logger.error(f"Persona file not found: {file_path}. Falling back to practice.")
            # Fallback to practice if specific persona missing
            if persona_name != "practice_interviewer":
                return self._load_persona("practice_interviewer")
            raise

    def _resolve_identity(self, persona: Dict[str, Any], session_id: str = "", language: str = "en") -> Dict[str, Any]:
        """
        Deterministically select an identity from the persona based on session_id.
        Returns a dict with resolved 'name' (str) and 'voice'.
        """
        identities = persona.get("identities")
        
        # Legacy fallback: if no identities list, use root fields
        if not identities:
            raw_identity = {
                "name": persona.get("name", "Interviewer"),
                "voice": persona.get("voice", {})
            }
        elif not session_id:
            # If no session ID, pick random
            raw_identity = random.choice(identities)
        else:
            # Deterministic selection based on session_id hash
            # This ensures the same session always talks to the same "person"
            import hashlib
            hash_val = int(hashlib.md5(session_id.encode()).hexdigest(), 16)
            index = hash_val % len(identities)
            raw_identity = identities[index]
        
        # Resolve localized name if it's a dict
        name = raw_identity.get("name")
        if isinstance(name, dict):
            name = name.get(language, name.get("en", "Interviewer"))
            
        return {
            "name": name,
            "voice": raw_identity.get("voice", {})
        }

    def _execute_skills(self, persona: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Execute all skills defined in persona and return combined injection."""
        # Merge persona skills with global skills
        persona_skills = persona.get("skills", [])
        # We use a list to preserve order: Global (Safety) first, then Persona (Specifics)
        all_skills = GLOBAL_SKILLS + persona_skills
        
        injection_text = ""
        
        seen_skills = set() # Avoid duplicates if defined in both
        
        for skill_conf in all_skills:
            skill_id = skill_conf.get("id")
            if not skill_id or skill_id in seen_skills:
                continue
                
            seen_skills.add(skill_id)
                
            SkillClass = skill_registry.get_skill_class(skill_id)
            if SkillClass:
                try:
                    skill = SkillClass(config=skill_conf)
                    result = skill.execute(context)
                    if result:
                        injection_text += f"\n{result}\n"
                except Exception as e:
                    logger.error(f"Error executing skill {skill_id}: {e}")
            else:
                logger.warning(f"Skill ID {skill_id} not found in registry.")

        return injection_text

    def _select_strategy(self, session_id: str, stage_type: str = "technical") -> dict:
        """Select a random strategic lens for the interview based on session_id."""
        # Strategies only apply to technical rounds
        if stage_type != "technical":
            return None

        strategies = [
            {
                "name": "The Purist",
                "description": "Focus strictly on Clean Code, SOLID principles, and design patterns. Reject 'hacky' solutions that work but are messy."
            },
            {
                "name": "The Pragmatist",
                "description": "Focus on shipping speed, MVP trade-offs, and business value. Challenge over-engineering and ask 'What is the fastest way to get this live?'."
            },
            {
                "name": "The Scaler",
                "description": "Obsess over high-load scenarios. Ask about caching (Redis), database indexing, load balancing, and O(n) complexity."
            },
            {
                "name": "The Security Auditor",
                "description": "Paranoid about vulnerabilities. Explicitly ask about XSS, SQL Injection, AuthZ/AuthN, and data encryption in every answer."
            },
            {
                "name": "The Legacy Cleaner",
                "description": "Focus on refactoring and technical debt. Ask 'How would you migrate this monolith?' or 'How do you handle dependency updates?'."
            }
        ]
        
        # Deterministic random based on session_id so the strategy stays constant for the whole session
        if not session_id:
            return random.choice(strategies)
            
        import hashlib
        hash_val = int(hashlib.md5((session_id + "strategy").encode()).hexdigest(), 16)
        return strategies[hash_val % len(strategies)]

    def _detect_tech_stack(self, text: str) -> List[str]:
        """Detect common tech stack keywords in text for specific probing."""
        if not text:
            return []
            
        text_lower = text.lower()
        detected = []
        
        keywords = self.config.get("tech_stacks", {})
        
        for tech, patterns in keywords.items():
            for pattern in patterns:
                if pattern in text_lower:
                    detected.append(tech)
                    break
        
        return detected

    def get_system_instruction(
        self,
        stage_type: str,
        job_role: str,
        context_info: str = "",
        language: str = "en",
        company_name: str = "TechVision",
        resume_text: str = "",  # Added resume_text for skills
        job_description: str = "",  # Added job_description for skills
        session_id: str = "",  # Added for identity stability
        # Intelligence v2 parameters
        previous_stage_insights: str = "",  # Cross-stage memory context
        candidate_profile_context: str = "",  # Real-time profile context
        difficulty_level: str = "",  # Current difficulty level
        competency_focus: str = "",  # Competency guidance
        prepared_questions: str = ""  # Pre-generated questions
    ) -> str:
        """Render complete system prompt with intelligence v2 enhancements."""
        # Sanitize inputs
        resume_text = resume_text or ""
        job_description = job_description or ""
        
        persona_key = STAGE_PERSONA_MAP.get(stage_type, "practice_interviewer")
        persona = self._load_persona(persona_key)
        
        # Resolve Identity
        identity = self._resolve_identity(persona, session_id, language)
        
        # Resolve Strategy (Entropy Layer)
        strategy = self._select_strategy(session_id, stage_type)
        
        # Inject resolved identity back into persona context for template
        persona_context = persona.copy()
        persona_context["name"] = identity["name"]
        
        # Helper to resolve localized fields
        def resolve_loc(field):
            if isinstance(field, dict) and "en" in field:
                return field.get(language, field.get("en"))
            return field

        # Resolve directives, sample_questions, scenarios
        persona_context["directives"] = resolve_loc(persona.get("directives", []))
        persona_context["sample_questions"] = resolve_loc(persona.get("sample_questions", []))
        
        # Resolve scenarios deeply
        raw_scenarios = persona.get("scenarios", [])
        resolved_scenarios = []
        for sc in raw_scenarios:
            resolved_scenarios.append({
                "trigger": sc["trigger"],
                "response_pattern": resolve_loc(sc["response_pattern"])
            })
        persona_context["scenarios"] = resolved_scenarios
        
        # Detect Tech Stack from Role + Resume + JD
        combat_text = f"{job_role} {resume_text} {job_description}"
        detected_stack = self._detect_tech_stack(combat_text)
        
        # Analyze Context Availability
        has_resume = len(resume_text.strip()) > 50 # Basic length check
        has_jd = len(job_description.strip()) > 50
        
        # Execute Skills
        skill_context = {
            "job_role": job_role,
            "resume_text": resume_text,
            "job_description": job_description,
            "language": language,
            "stage_type": stage_type  # Pass stage_type for stage-aware skills
        }
        skill_injections = self._execute_skills(persona, skill_context)
        
        # Append skill output to context_info or a new field
        full_context = f"{context_info}\n{skill_injections}"
        
        template = self.env.get_template("system_instruction.j2")

        return template.render(
            persona=persona_context,
            job_role=job_role,
            context_info=full_context,
            language=language,
            company_name=company_name,
            tech_stack=detected_stack,
            strategy=strategy,
            stage_type=stage_type,
            has_resume=has_resume,
            has_jd=has_jd,
            resume_text=resume_text if has_resume else "",
            job_description=job_description if has_jd else "",
            # Intelligence v2 context
            previous_stage_insights=previous_stage_insights,
            candidate_profile_context=candidate_profile_context,
            difficulty_level=difficulty_level,
            competency_focus=competency_focus,
            prepared_questions=prepared_questions
        )

    def get_greeting(
        self, 
        stage_type: str, 
        job_role: str, 
        language: str = "en",
        session_id: str = ""
    ) -> str:
        """Render initial greeting."""
        persona_key = STAGE_PERSONA_MAP.get(stage_type, "practice_interviewer")
        persona = self._load_persona(persona_key)
        
        # Resolve Identity
        identity = self._resolve_identity(persona, session_id, language)
        persona_context = persona.copy()
        persona_context["name"] = identity["name"]
        
        template = self.env.get_template("greeting.j2")
        
        return template.render(
            persona=persona_context,
            stage_type=stage_type,
            job_role=job_role,
            language=language
        ).strip()

    def get_voice_model(self, stage_type: str, language: str = "en", session_id: str = "") -> str:
        """Get Cartesia voice UUID for stage/language."""
        persona_key = STAGE_PERSONA_MAP.get(stage_type, "practice_interviewer")
        persona = self._load_persona(persona_key)
        
        # Resolve Identity
        identity = self._resolve_identity(persona, session_id, language)
        
        voices = identity.get("voice", {})
        # Default to English if specific language voice missing
        return voices.get(language, voices.get("en"))

# Singleton instance
prompt_manager = PromptManager()
