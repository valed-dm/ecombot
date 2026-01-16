"""
Script to seed the database with a default pickup point.
Run this to ensure the 'Pickup' checkout flow works immediately.
"""

import asyncio
from pathlib import Path
import sys


# Add the 'src' directory to sys.path so we can import 'ecombot'
# Assumes this file is at src/ecombot/bot/handlers/checkout/seed_pickup.py
sys.path.append(str(Path(__file__).resolve().parents[4]))

from sqlalchemy import select

from ecombot.db.database import AsyncSessionLocal
from ecombot.db.models import PickupPoint
from ecombot.schemas.enums import DeliveryType


async def seed_default_pickup():
    async with AsyncSessionLocal() as session:
        print("Checking for existing pickup points...")
        stmt = select(PickupPoint).limit(1)
        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            print(f"✅ Pickup point already exists: {existing.name}")
            return

        print("Creating default pickup point...")
        new_point = PickupPoint(
            name="Пункт выдачи (Марьино, Симферополь)",
            address="Водников ул, дом 61А Симферополь",
            pickup_type=DeliveryType.PICKUP_STORE,
            working_hours="Mon-Sun: 09:00 - 21:00",
            is_active=True,
        )
        session.add(new_point)
        await session.commit()
        print("✅ Successfully created default pickup point!")


if __name__ == "__main__":
    try:
        asyncio.run(seed_default_pickup())
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        print("Hint: Did you run 'alembic upgrade head' to create the tables first?")
