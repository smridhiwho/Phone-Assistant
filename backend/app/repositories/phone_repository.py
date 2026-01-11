from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
import json

from app.models.database import Phone


class PhoneRepository:
    """Repository for phone data operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, limit: int = 100, offset: int = 0) -> List[Phone]:
        """Get all phones with pagination."""
        result = await self.db.execute(
            select(Phone).offset(offset).limit(limit)
        )
        return result.scalars().all()

    async def get_by_id(self, phone_id: int) -> Optional[Phone]:
        """Get a phone by ID."""
        result = await self.db.execute(
            select(Phone).where(Phone.id == phone_id)
        )
        return result.scalar_one_or_none()

    async def get_by_ids(self, phone_ids: List[int]) -> List[Phone]:
        """Get multiple phones by IDs."""
        result = await self.db.execute(
            select(Phone).where(Phone.id.in_(phone_ids))
        )
        return result.scalars().all()

    async def search(
        self,
        brand: Optional[str] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        min_ram: Optional[int] = None,
        min_battery: Optional[int] = None,
        features: Optional[List[str]] = None,
        search_text: Optional[str] = None,
        limit: int = 10
    ) -> List[Phone]:
        """Search phones with filters."""
        query = select(Phone)
        conditions = []

        if brand:
            conditions.append(Phone.brand.ilike(f"%{brand}%"))

        if min_price:
            conditions.append(Phone.price_inr >= min_price)

        if max_price:
            conditions.append(Phone.price_inr <= max_price)

        if min_ram:
            conditions.append(Phone.ram_gb >= min_ram)

        if min_battery:
            conditions.append(Phone.battery_mah >= min_battery)

        if search_text:
            search_conditions = [
                Phone.brand.ilike(f"%{search_text}%"),
                Phone.model.ilike(f"%{search_text}%"),
                Phone.processor.ilike(f"%{search_text}%"),
                Phone.highlights.ilike(f"%{search_text}%")
            ]
            conditions.append(or_(*search_conditions))

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(Phone.price_inr.desc()).limit(limit)
        result = await self.db.execute(query)
        phones = result.scalars().all()

        if features:
            filtered_phones = []
            for phone in phones:
                if phone.features:
                    try:
                        phone_features = json.loads(phone.features) if isinstance(phone.features, str) else phone.features
                        if any(
                            any(f.lower() in pf.lower() for pf in phone_features)
                            for f in features
                        ):
                            filtered_phones.append(phone)
                    except json.JSONDecodeError:
                        continue
            return filtered_phones

        return phones

    async def get_by_brand(self, brand: str, limit: int = 10) -> List[Phone]:
        """Get phones by brand."""
        result = await self.db.execute(
            select(Phone)
            .where(Phone.brand.ilike(f"%{brand}%"))
            .order_by(Phone.price_inr.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_price_range(
        self,
        min_price: int,
        max_price: int,
        limit: int = 10
    ) -> List[Phone]:
        """Get phones within a price range."""
        result = await self.db.execute(
            select(Phone)
            .where(and_(
                Phone.price_inr >= min_price,
                Phone.price_inr <= max_price
            ))
            .order_by(Phone.price_inr.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_budget_phones(self, max_price: int = 20000, limit: int = 10) -> List[Phone]:
        """Get budget phones."""
        return await self.get_by_price_range(0, max_price, limit)

    async def get_flagship_phones(self, min_price: int = 60000, limit: int = 10) -> List[Phone]:
        """Get flagship phones."""
        result = await self.db.execute(
            select(Phone)
            .where(Phone.price_inr >= min_price)
            .order_by(Phone.price_inr.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_gaming_phones(self, limit: int = 10) -> List[Phone]:
        """Get phones suitable for gaming."""
        result = await self.db.execute(
            select(Phone)
            .where(and_(
                Phone.refresh_rate >= 120,
                Phone.ram_gb >= 8
            ))
            .order_by(Phone.refresh_rate.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_camera_phones(self, limit: int = 10) -> List[Phone]:
        """Get phones with best cameras."""
        result = await self.db.execute(
            select(Phone)
            .where(or_(
                Phone.highlights.ilike("%camera%"),
                Phone.highlights.ilike("%photo%"),
                Phone.highlights.ilike("%leica%"),
                Phone.highlights.ilike("%zeiss%"),
                Phone.highlights.ilike("%hasselblad%")
            ))
            .order_by(Phone.price_inr.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_battery_phones(self, min_battery: int = 5000, limit: int = 10) -> List[Phone]:
        """Get phones with best battery life."""
        result = await self.db.execute(
            select(Phone)
            .where(Phone.battery_mah >= min_battery)
            .order_by(Phone.battery_mah.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def count(self) -> int:
        """Get total count of phones."""
        result = await self.db.execute(select(Phone))
        return len(result.scalars().all())

    async def create(self, phone_data: Dict[str, Any]) -> Phone:
        """Create a new phone entry."""
        # Convert lists to JSON strings
        if 'features' in phone_data and isinstance(phone_data['features'], list):
            phone_data['features'] = json.dumps(phone_data['features'])
        if 'colors' in phone_data and isinstance(phone_data['colors'], list):
            phone_data['colors'] = json.dumps(phone_data['colors'])

        phone = Phone(**phone_data)
        self.db.add(phone)
        await self.db.commit()
        await self.db.refresh(phone)
        return phone

    async def bulk_create(self, phones_data: List[Dict[str, Any]]) -> List[Phone]:
        """Create multiple phone entries."""
        phones = []
        for phone_data in phones_data:
            if 'features' in phone_data and isinstance(phone_data['features'], list):
                phone_data['features'] = json.dumps(phone_data['features'])
            if 'colors' in phone_data and isinstance(phone_data['colors'], list):
                phone_data['colors'] = json.dumps(phone_data['colors'])
            phones.append(Phone(**phone_data))

        self.db.add_all(phones)
        await self.db.commit()
        return phones
