
"""
Career Manager Module.

Responsible for loading the Career Tree definition from YAML and providing
access methods for the Game Engine.

This is the "Content Engine" described in Project Odyssey.
"""
import os
import yaml
import logging
from typing import Dict, List, Optional
from app.models.gamification import CareerNode

logger = logging.getLogger("career-manager")

class CareerManager:
    def __init__(self, config_path: str = "config/career_tree.yaml"):
        from config.settings import settings
        self.config_path = str(settings.base_path / config_path)
        
        self.nodes: Dict[str, Dict] = {}
        self.params: Dict = {} # Global params like Rank Titles
        self._load_config()

    def _load_config(self):
        """Load YAML config from disk."""
        if not os.path.exists(self.config_path):
            logger.error(f"Career Tree config not found at {self.config_path}")
            return

        try:
            with open(self.config_path, "r") as f:
                data = yaml.safe_load(f)
                
            self.params['ranks'] = data.get('ranks', {})
            
            # Index nodes by ID
            raw_nodes = data.get('nodes', [])
            for node in raw_nodes:
                self.nodes[node['id']] = node
                
            logger.info(f"Loaded {len(self.nodes)} career nodes from {self.config_path}")
            
        except Exception as e:
            logger.error(f"Failed to load Career Tree config: {e}")

    def get_node(self, node_id: str) -> Optional[Dict]:
        """Get raw node dictionary by ID."""
        return self.nodes.get(node_id)
        
    def get_all_nodes(self) -> List[Dict]:
        """Get all nodes as list."""
        return list(self.nodes.values())

    def get_rank_title(self, rank_level: int) -> str:
        """Get title for a rank level."""
        return self.params.get('ranks', {}).get(rank_level, f"Level {rank_level}")

    def get_next_unlocks(self, completed_node_ids: List[str]) -> List[str]:
        """
        Determine which nodes are UNLOCKED based on completed nodes.
        logic: 
        1. Find all nodes referenced in 'unlocks' of completed nodes.
        2. Filter out already completed nodes.
        3. Check if we meet rank requirement? (Optional)
        """
        unlocked_candidates = set()
        
        # 1. Start with nodes that have NO parents (roots) if nothing completed?
        # Actually, let's look at the tree. 
        # For MVP: If valid root nodes exist, they are unlocked by default? 
        # We'll handle 'Start' logic in Service.
        
        for nid in completed_node_ids:
            node = self.get_node(nid)
            if node:
                for child_id in node.get('unlocks', []):
                    unlocked_candidates.add(child_id)
                    
        # Filter completed
        final_list = [nid for nid in unlocked_candidates if nid not in completed_node_ids]
        return final_list

# Singleton
career_manager = CareerManager()
