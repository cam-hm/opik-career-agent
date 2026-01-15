"""
Skill Registry.

Central catalog for loading skills by ID.
"""
from typing import Type, Dict, Optional
from app.services.core.intelligence.skills import BaseSkill

# Import available skills here to register them
# We will do lazy import inside get_skill_class to avoid circular deps if needed,
# but for now explicit import is cleaner.

from app.services.core.intelligence.skills.extraction.resume_probe import ResumeProbe
from app.services.core.intelligence.skills.extraction.job_match import JobMatchEvaluator
from app.services.core.intelligence.skills.guardrails.bias_filter import BiasFilter
from app.services.core.intelligence.skills.guardrails.topic_blocker import TopicBlocker
from app.services.core.intelligence.skills.assessment.star_watchdog import StarWatchdog
from app.services.core.intelligence.skills.simulation.sales_objection import SalesObjectionSimulator

class SkillRegistry:
    _registry: Dict[str, Type[BaseSkill]] = {
        "resume_probe": ResumeProbe,
        "job_match": JobMatchEvaluator,
        "bias_filter": BiasFilter,
        "topic_blocker": TopicBlocker,
        "star_watchdog": StarWatchdog,
        "sales_objection": SalesObjectionSimulator,
    }

    @classmethod
    def get_skill_class(cls, skill_id: str) -> Optional[Type[BaseSkill]]:
        """Get skill class by ID."""
        return cls._registry.get(skill_id)

    @classmethod
    def register(cls, skill_id: str, skill_class: Type[BaseSkill]):
        """Dynamically register a new skill."""
        cls._registry[skill_id] = skill_class

skill_registry = SkillRegistry()
