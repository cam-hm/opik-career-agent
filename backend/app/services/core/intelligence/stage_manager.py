"""
Stage Manager Module.

Manages the flow and configuration of interview stages.
Loads stage definitions from stages.yaml.
"""
import os
import yaml
import logging
from dataclasses import dataclass
from typing import Optional, List, Dict

logger = logging.getLogger("stage-manager")

@dataclass
class StageConfig:
    """Configuration for an interview stage."""
    id: int
    type: str
    name: str
    description: str
    persona_id: str
    duration_minutes: int

class StageManager:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(self.base_dir, "stages.yaml")
        
        self.stages: Dict[int, StageConfig] = {}
        self.stages_by_type: Dict[str, StageConfig] = {}
        
        self._load_config()
        
    def _load_config(self):
        """Load stage configuration from YAML."""
        try:
            with open(self.config_path, "r") as f:
                data = yaml.safe_load(f)
                
            for item in data.get("stages", []):
                stage = StageConfig(
                    id=item["id"],
                    type=item["type"],
                    name=item["name"],
                    description=item["description"],
                    persona_id=item["persona_id"],
                    duration_minutes=item.get("duration_minutes", 20)
                )
                self.stages[stage.id] = stage
                self.stages_by_type[stage.type] = stage
                
            logger.info(f"Loaded {len(self.stages)} stages from config.")
            
        except FileNotFoundError:
            logger.error(f"Stage config file not found: {self.config_path}")
            # Fallback default hardcoded stages if file missing (Safety net)
            self._load_defaults()

    def _load_defaults(self):
        """Fallback defaults if YAML is missing."""
        logger.warning("Loading default stages.")
        defaults = [
            StageConfig(1, "hr", "HR Screening", "Culture fit", "hr_recruiter", 15),
            StageConfig(2, "technical", "Technical Round", "Hard skills", "tech_lead", 30),
            StageConfig(3, "behavioral", "Manager Round", "Leadership", "behavioral_manager", 20),
        ]
        for stage in defaults:
            self.stages[stage.id] = stage
            self.stages_by_type[stage.type] = stage

    def get_stage_by_number(self, stage_number: int) -> Optional[StageConfig]:
        """Get stage configuration by ID."""
        return self.stages.get(stage_number)

    def get_stage_by_type(self, stage_type: str) -> Optional[StageConfig]:
        """Get stage configuration by type."""
        return self.stages_by_type.get(stage_type)

    def get_stage_type(self, stage_number: int) -> str:
        """Get stage type string from number."""
        stage = self.stages.get(stage_number)
        return stage.type if stage else "unknown"

# Singleton instance
stage_manager = StageManager()
