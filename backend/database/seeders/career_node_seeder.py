"""
Career Node Seeder - Seeds career tree nodes from YAML.

Syncs nodes defined in config/career_tree.yaml to the career_nodes table.
"""
from database.seeders.base import BaseSeeder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from app.models.gamification import CareerNode
from app.services.core.gamification.career_manager import career_manager


class CareerNodeSeeder(BaseSeeder):
    """Seeds career nodes from YAML config."""
    
    name = "career_nodes"
    description = "Seed career tree nodes from config/career_tree.yaml"
    
    async def run(self, db: AsyncSession) -> int:
        nodes_data = career_manager.get_all_nodes()
        count = 0
        
        for node_def in nodes_data:
            stmt = insert(CareerNode).values(
                id=node_def['id'],
                title=node_def['title'],
                type=node_def['type'],
                rank_required=node_def.get('rank_required', 1),
                metadata_=node_def  # Store everything as JSON
            )
            
            # Upsert
            update_stmt = stmt.on_conflict_do_update(
                index_elements=['id'],
                set_=dict(
                    title=stmt.excluded.title,
                    type=stmt.excluded.type,
                    rank_required=stmt.excluded.rank_required,
                    metadata=stmt.excluded.metadata
                )
            )
            
            await db.execute(update_stmt)
            count += 1
        
        await db.commit()
        self.log(f"✅ Seeded {count} career nodes")
        return count
