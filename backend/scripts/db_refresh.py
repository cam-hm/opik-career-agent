import sys
import os

# Add root directory to path so we can import 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import logging
import argparse
from sqlalchemy import text
from app.services.core.database import AsyncSessionLocal
from database.seeders.runner import run_all_seeders
from alembic.config import Config
from alembic import command

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("db_fresh")

async def drop_all_tables():
    """Drop all tables in the database."""
    logger.info("🗑️  Dropping all tables...")
    async with AsyncSessionLocal() as session:
        # Disable foreign key checks temporarily if needed, 
        # but pure SQL execute is safer for drop cascade
        await session.execute(text("DROP SCHEMA public CASCADE;"))
        await session.execute(text("CREATE SCHEMA public;"))
        await session.execute(text("GRANT ALL ON SCHEMA public TO postgres;"))
        await session.execute(text("GRANT ALL ON SCHEMA public TO public;"))
        # Workaround for asyncpg/alembic issue on fresh DB
        await session.execute(text("CREATE TABLE IF NOT EXISTS alembic_version (version_num VARCHAR(32) NOT NULL PRIMARY KEY);"))
        await session.commit()
    logger.info("✅ All tables dropped & prepared.")

def run_migrations():
    """Run alembic migrations."""
    logger.info("🔄 Running migrations...")
import subprocess

def run_migrations():
    """Run alembic migrations."""
    logger.info("🔄 Running migrations...")
    subprocess.run(["alembic", "upgrade", "head"], check=True)
    logger.info("✅ Migrations complete.")

async def main():
    parser = argparse.ArgumentParser(description="Refresh database (drop all, migrate, seed)")
    parser.add_argument("--seed", action="store_true", help="Run seeders after fresh")
    args = parser.parse_args()

    # 1. Drop All
    await drop_all_tables()
    
    # 2. Migrate
    # Alembic commands are synchronous
    run_migrations()
    
    # 3. Seed (optional)
    if args.seed:
        await run_all_seeders()

if __name__ == "__main__":
    asyncio.run(main())
