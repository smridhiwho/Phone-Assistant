"""Script to seed the database with phone data."""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import init_db, AsyncSessionLocal, Phone
from app.repositories.phone_repository import PhoneRepository


async def load_phones_data():
    """Load phones data from JSON file."""
    data_path = Path(__file__).parent.parent / "app" / "data" / "phones.json"
    with open(data_path, "r") as f:
        return json.load(f)


async def seed_database():
    """Seed the database with phone data."""
    print("Initializing database...")
    await init_db()

    print("Loading phone data...")
    phones_data = await load_phones_data()

    print(f"Seeding {len(phones_data)} phones...")

    async with AsyncSessionLocal() as db:
        phone_repo = PhoneRepository(db)

        existing_count = await phone_repo.count()
        if existing_count > 0:
            print(f"Database already has {existing_count} phones. Skipping seed.")
            return

        for phone_data in phones_data:
            if 'id' in phone_data:
                del phone_data['id']

            await phone_repo.create(phone_data)

        print(f"Successfully seeded {len(phones_data)} phones!")


async def main():
    """Main entry point."""
    try:
        await seed_database()
        print("Database seeding complete!")
    except Exception as e:
        print(f"Error seeding database: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
