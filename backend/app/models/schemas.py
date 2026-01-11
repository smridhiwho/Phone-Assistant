from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class DisplayInfo(BaseModel):
    """Display specification details."""
    size: float
    type: str
    resolution: Optional[str] = None
    refresh_rate: Optional[int] = None


class CameraInfo(BaseModel):
    """Camera specification details."""
    rear: Dict[str, Any]
    front: str


class BatteryInfo(BaseModel):
    """Battery specification details."""
    capacity_mah: int
    fast_charging_w: Optional[int] = None
    wireless_charging: bool = False


class PhoneBase(BaseModel):
    """Base phone model."""
    brand: str
    model: str
    price_inr: int
    display_size: Optional[float] = None
    display_type: Optional[str] = None
    processor: Optional[str] = None
    ram_gb: Optional[int] = None
    storage_gb: Optional[int] = None
    rear_camera: Optional[str] = None
    front_camera: Optional[str] = None
    battery_mah: Optional[int] = None
    fast_charging_w: Optional[int] = None
    os: Optional[str] = None
    launch_year: Optional[int] = None
    features: Optional[List[str]] = None
    highlights: Optional[str] = None
    image_url: Optional[str] = None


class PhoneCreate(PhoneBase):
    """Schema for creating a phone."""
    pass


class PhoneResponse(PhoneBase):
    """Schema for phone response."""
    id: int
    display_resolution: Optional[str] = None
    refresh_rate: Optional[int] = None
    wireless_charging: bool = False
    dimensions: Optional[str] = None
    weight_g: Optional[int] = None
    colors: Optional[List[str]] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PhoneListResponse(BaseModel):
    """Response for phone list."""
    products: List[PhoneResponse]
    count: int


# ============ Chat Schemas ============

class ChatRequest(BaseModel):
    """Request schema for chat message."""
    session_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1, max_length=2000)
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Response schema for chat message."""
    response: str
    products: List[PhoneResponse] = []
    intent: str
    suggestions: List[str] = []
    session_id: str


class MessageResponse(BaseModel):
    """Response for a single message."""
    id: int
    role: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    """Response for conversation history."""
    session_id: str
    messages: List[MessageResponse]


# ============ Product Schemas ============

class SearchRequest(BaseModel):
    """Request schema for product search."""
    query: str = Field(..., min_length=1, max_length=500)
    filters: Optional[Dict[str, Any]] = None


class SearchResponse(BaseModel):
    """Response schema for product search."""
    products: List[PhoneResponse]
    explanation: str
    count: int


class CompareRequest(BaseModel):
    """Request schema for phone comparison."""
    product_ids: List[int] = Field(..., min_items=2, max_items=4)


class ComparisonSpec(BaseModel):
    """Individual specification comparison."""
    spec_name: str
    values: Dict[str, Any]  # phone_id -> value
    winner: Optional[str] = None  # phone_id or "tie"


class CompareResponse(BaseModel):
    """Response schema for phone comparison."""
    phones: List[PhoneResponse]
    comparison: List[ComparisonSpec]
    summary: str
    recommendation: Optional[str] = None


# ============ Health Schemas ============

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    model_loaded: bool
    database_connected: bool
    version: str
