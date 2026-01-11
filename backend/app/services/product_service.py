from typing import List, Dict, Any, Optional
import json

from app.models.database import Phone
from app.models.schemas import PhoneResponse, ComparisonSpec


class ProductService:
    """Service for product-related operations."""

    def phone_to_response(self, phone: Phone) -> PhoneResponse:
        """Convert Phone model to PhoneResponse schema."""
        features = None
        colors = None

        if phone.features:
            try:
                features = json.loads(phone.features) if isinstance(phone.features, str) else phone.features
            except json.JSONDecodeError:
                features = []

        if phone.colors:
            try:
                colors = json.loads(phone.colors) if isinstance(phone.colors, str) else phone.colors
            except json.JSONDecodeError:
                colors = []

        return PhoneResponse(
            id=phone.id,
            brand=phone.brand,
            model=phone.model,
            price_inr=phone.price_inr,
            display_size=phone.display_size,
            display_type=phone.display_type,
            display_resolution=phone.display_resolution,
            refresh_rate=phone.refresh_rate,
            processor=phone.processor,
            ram_gb=phone.ram_gb,
            storage_gb=phone.storage_gb,
            rear_camera=phone.rear_camera,
            front_camera=phone.front_camera,
            battery_mah=phone.battery_mah,
            fast_charging_w=phone.fast_charging_w,
            wireless_charging=phone.wireless_charging or False,
            os=phone.os,
            launch_year=phone.launch_year,
            dimensions=phone.dimensions,
            weight_g=phone.weight_g,
            features=features,
            colors=colors,
            highlights=phone.highlights,
            image_url=phone.image_url,
            created_at=phone.created_at
        )

    def phones_to_response(self, phones: List[Phone]) -> List[PhoneResponse]:
        """Convert list of Phone models to list of PhoneResponse schemas."""
        return [self.phone_to_response(phone) for phone in phones]

    def generate_comparison(self, phones: List[Phone]) -> List[ComparisonSpec]:
        """Generate comparison specifications for phones."""
        if len(phones) < 2:
            return []

        comparisons = []
        phone_ids = [str(p.id) for p in phones]

        price_values = {str(p.id): f"₹{p.price_inr:,}" for p in phones}
        min_price_phone = min(phones, key=lambda p: p.price_inr)
        comparisons.append(ComparisonSpec(
            spec_name="Price",
            values=price_values,
            winner=str(min_price_phone.id)
        ))

        display_values = {}
        for p in phones:
            display_info = f"{p.display_size}\" {p.display_type or ''}"
            if p.refresh_rate:
                display_info += f" {p.refresh_rate}Hz"
            display_values[str(p.id)] = display_info.strip()
        max_refresh = max(phones, key=lambda p: p.refresh_rate or 0)
        comparisons.append(ComparisonSpec(
            spec_name="Display",
            values=display_values,
            winner=str(max_refresh.id) if max_refresh.refresh_rate else None
        ))

        processor_values = {str(p.id): p.processor or "N/A" for p in phones}
        comparisons.append(ComparisonSpec(
            spec_name="Processor",
            values=processor_values,
            winner=None  
        ))

        ram_values = {str(p.id): f"{p.ram_gb}GB" if p.ram_gb else "N/A" for p in phones}
        max_ram = max(phones, key=lambda p: p.ram_gb or 0)
        comparisons.append(ComparisonSpec(
            spec_name="RAM",
            values=ram_values,
            winner=str(max_ram.id) if max_ram.ram_gb else None
        ))

        storage_values = {str(p.id): f"{p.storage_gb}GB" if p.storage_gb else "N/A" for p in phones}
        max_storage = max(phones, key=lambda p: p.storage_gb or 0)
        comparisons.append(ComparisonSpec(
            spec_name="Storage",
            values=storage_values,
            winner=str(max_storage.id) if max_storage.storage_gb else None
        ))

        camera_values = {str(p.id): p.rear_camera or "N/A" for p in phones}
        comparisons.append(ComparisonSpec(
            spec_name="Rear Camera",
            values=camera_values,
            winner=None
        ))

        battery_values = {str(p.id): f"{p.battery_mah}mAh" if p.battery_mah else "N/A" for p in phones}
        max_battery = max(phones, key=lambda p: p.battery_mah or 0)
        comparisons.append(ComparisonSpec(
            spec_name="Battery",
            values=battery_values,
            winner=str(max_battery.id) if max_battery.battery_mah else None
        ))

        charging_values = {str(p.id): f"{p.fast_charging_w}W" if p.fast_charging_w else "N/A" for p in phones}
        max_charging = max(phones, key=lambda p: p.fast_charging_w or 0)
        comparisons.append(ComparisonSpec(
            spec_name="Fast Charging",
            values=charging_values,
            winner=str(max_charging.id) if max_charging.fast_charging_w else None
        ))

        return comparisons

    def generate_comparison_summary(self, phones: List[Phone]) -> str:
        """Generate a summary for phone comparison."""
        if len(phones) < 2:
            return "Need at least 2 phones to compare."

        phone_names = [f"{p.brand} {p.model}" for p in phones]
        prices = [(p.id, p.price_inr) for p in phones]

        sorted_by_price = sorted(phones, key=lambda p: p.price_inr)
        cheapest = sorted_by_price[0]
        most_expensive = sorted_by_price[-1]

        best_battery = max(phones, key=lambda p: p.battery_mah or 0)
        best_ram = max(phones, key=lambda p: p.ram_gb or 0)
        fastest_charging = max(phones, key=lambda p: p.fast_charging_w or 0)

        summary_parts = [
            f"Comparing {', '.join(phone_names)}.",
            f"Best value: {cheapest.brand} {cheapest.model} at ₹{cheapest.price_inr:,}.",
            f"Best battery: {best_battery.brand} {best_battery.model} ({best_battery.battery_mah}mAh).",
            f"Fastest charging: {fastest_charging.brand} {fastest_charging.model} ({fastest_charging.fast_charging_w}W)."
        ]

        if most_expensive.id != cheapest.id:
            price_diff = most_expensive.price_inr - cheapest.price_inr
            summary_parts.append(
                f"Price difference: ₹{price_diff:,} between cheapest and most expensive."
            )

        return " ".join(summary_parts)

    def format_phone_context(self, phones: List[Phone]) -> str:
        """Format phones for LLM context."""
        if not phones:
            return "No phones available."

        context_parts = []
        for phone in phones:
            features = ""
            if phone.features:
                try:
                    features_list = json.loads(phone.features) if isinstance(phone.features, str) else phone.features
                    features = ", ".join(features_list[:5])
                except:
                    features = ""

            context_parts.append(
                f"- {phone.brand} {phone.model} (ID: {phone.id}): "
                f"₹{phone.price_inr:,}, {phone.processor or 'N/A'}, "
                f"{phone.ram_gb}GB RAM, {phone.battery_mah}mAh battery, "
                f"{phone.rear_camera or 'N/A'} camera. "
                f"Highlights: {phone.highlights or 'N/A'}. "
                f"Features: {features}"
            )

        return "\n".join(context_parts)


_product_service: Optional[ProductService] = None


def get_product_service() -> ProductService:
    """Get product service singleton."""
    global _product_service
    if _product_service is None:
        _product_service = ProductService()
    return _product_service
