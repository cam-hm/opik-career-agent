"""
Base Seeder Class - Laravel-Style Pattern

Usage:
    class MySeeder(BaseSeeder):
        name = "my_seeder"
        
        async def run(self, db: AsyncSession):
            # Seed logic here
            pass
"""
from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
import logging

logger = logging.getLogger("seeders")


class BaseSeeder(ABC):
    """Base class for all seeders."""
    
    name: str = "base"
    description: str = ""
    
    @abstractmethod
    async def run(self, db: AsyncSession) -> int:
        """
        Execute the seeder.
        
        Returns:
            Number of records seeded.
        """
        raise NotImplementedError
    
    async def should_run(self, db: AsyncSession) -> bool:
        """
        Check if seeder should run (e.g., check if already seeded).
        Override in subclass for conditional seeding.
        
        Returns:
            True if seeder should run, False to skip.
        """
        return True
    
    def log(self, message: str):
        """Log a message with seeder name prefix."""
        logger.info(f"[{self.name}] {message}")
