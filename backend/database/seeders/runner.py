"""
Seeder Runner - Laravel-Style CLI

Usage:
    python -m seeders.runner                    # Run all seeders
    python -m seeders.runner badges             # Run specific seeder
    python -m seeders.runner badges career_nodes # Run multiple seeders
    python -m seeders.runner --list             # List available seeders
    
Docker:
    docker exec -it interviewer-backend python -m seeders.runner
"""
import asyncio
import argparse
import logging
from typing import List, Type

from app.services.core.database import AsyncSessionLocal
from database.seeders.base import BaseSeeder
from database.seeders.badge_seeder import BadgeSeeder
from database.seeders.career_node_seeder import CareerNodeSeeder

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("seeders")

# Registry of all available seeders
SEEDERS: List[Type[BaseSeeder]] = [
    BadgeSeeder,
    CareerNodeSeeder,
]


def get_seeder_by_name(name: str) -> Type[BaseSeeder] | None:
    """Find seeder class by name."""
    for seeder_cls in SEEDERS:
        if seeder_cls.name == name:
            return seeder_cls
    return None


async def run_seeder(seeder_cls: Type[BaseSeeder]) -> int:
    """Run a single seeder."""
    seeder = seeder_cls()
    
    async with AsyncSessionLocal() as db:
        if not await seeder.should_run(db):
            logger.info(f"⏭️  [{seeder.name}] Skipped (already seeded)")
            return 0
        
        logger.info(f"🌱 [{seeder.name}] Running...")
        count = await seeder.run(db)
        return count


async def run_all_seeders():
    """Run all registered seeders in order."""
    logger.info("=" * 50)
    logger.info("🌱 Running All Seeders")
    logger.info("=" * 50)
    
    total = 0
    for seeder_cls in SEEDERS:
        count = await run_seeder(seeder_cls)
        total += count
    
    logger.info("=" * 50)
    logger.info(f"✅ Seeding complete! Total records: {total}")
    logger.info("=" * 50)


async def run_specific_seeders(names: List[str]):
    """Run specific seeders by name."""
    logger.info("=" * 50)
    logger.info(f"🌱 Running Seeders: {', '.join(names)}")
    logger.info("=" * 50)
    
    total = 0
    for name in names:
        seeder_cls = get_seeder_by_name(name)
        if seeder_cls:
            count = await run_seeder(seeder_cls)
            total += count
        else:
            logger.warning(f"⚠️  Seeder '{name}' not found")
    
    logger.info("=" * 50)
    logger.info(f"✅ Seeding complete! Total records: {total}")
    logger.info("=" * 50)


def list_seeders():
    """List all available seeders."""
    print("\n📋 Available Seeders:")
    print("-" * 40)
    for seeder_cls in SEEDERS:
        print(f"  • {seeder_cls.name:<20} {seeder_cls.description}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Laravel-style database seeder for Python",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m seeders.runner              # Run all seeders
  python -m seeders.runner badges       # Run badge seeder only
  python -m seeders.runner --list       # List available seeders
        """
    )
    parser.add_argument(
        "seeders",
        nargs="*",
        help="Specific seeders to run (leave empty for all)"
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List available seeders"
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_seeders()
        return
    
    if args.seeders:
        asyncio.run(run_specific_seeders(args.seeders))
    else:
        asyncio.run(run_all_seeders())


if __name__ == "__main__":
    main()
