import asyncio
import os
import sys

# Add parent directory to path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

from config.settings import get_settings
from app.models.base import Base
# Make sure to import all models so they are registered with Base.metadata
from app.models import *

# Alembic imports
from alembic.config import Config
from alembic import command

# Seeder import
from database.seeders import seed

settings = get_settings()

async def reset_database():
    print("⚠️  DANGER: RESETTING DATABASE IN 5 SECONDS...")
    print(f"Target: {settings.DATABASE_URL.split('@')[-1]}")  # Print only host/db part for safety
    await asyncio.sleep(5)

    print("♻️  Dropping all tables...")
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        # Disable foreign key checks to allow dropping tables in any order
        # This is specific to PostgreSQL
        await conn.execute(text("DROP SCHEMA public CASCADE;"))
        await conn.execute(text("CREATE SCHEMA public;"))
        
    await engine.dispose()
    print("✅ Tables dropped.")

    print("🚀 Running Migrations (Alembic Upgrade)...")
    try:
        # Needs to be run synchronously
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        print("✅ Migrations applied.")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)

    print("🌱 Seeding Database...")
    try:
        await seed.main()
        print("✅ Database seeded.")
    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        sys.exit(1)

    print("🎉 Database Reset Complete!")

if __name__ == "__main__":
    asyncio.run(reset_database())
