from sqlalchemy import Column, Integer, String, Float, Boolean, Text, ForeignKey, DateTime, LargeBinary
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

from app.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()


class Phone(Base):
    """Phone model for storing mobile phone information."""
    __tablename__ = "phones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    brand = Column(String(100), nullable=False, index=True)
    model = Column(String(200), nullable=False)
    price_inr = Column(Integer, nullable=False, index=True)
    display_size = Column(Float)
    display_type = Column(String(50))
    display_resolution = Column(String(50))
    refresh_rate = Column(Integer)
    processor = Column(String(200))
    ram_gb = Column(Integer)
    storage_gb = Column(Integer)
    rear_camera = Column(String(200))
    front_camera = Column(String(100))
    battery_mah = Column(Integer)
    fast_charging_w = Column(Integer)
    wireless_charging = Column(Boolean, default=False)
    os = Column(String(100))
    launch_year = Column(Integer)
    dimensions = Column(String(100))
    weight_g = Column(Integer)
    features = Column(Text)  # JSON array
    colors = Column(Text)  # JSON array
    highlights = Column(Text)
    image_url = Column(String(500))
    specifications = Column(Text)  # Full JSON
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to embeddings
    embeddings = relationship("PhoneEmbedding", back_populates="phone")


class PhoneEmbedding(Base):
    """Phone embedding for semantic search."""
    __tablename__ = "phone_embeddings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    phone_id = Column(Integer, ForeignKey("phones.id"), nullable=False)
    embedding = Column(LargeBinary)  # Serialized numpy array
    model_name = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

    phone = relationship("Phone", back_populates="embeddings")


class Conversation(Base):
    """Conversation session model."""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = relationship("Message", back_populates="conversation")


class Message(Base):
    """Message model for conversation history."""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    message_metadata = Column(Text)  # JSON with intent, products shown, etc.
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")


class QueryAnalytics(Base):
    """Query analytics for monitoring."""
    __tablename__ = "query_analytics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    query = Column(Text, nullable=False)
    intent = Column(String(100))
    products_returned = Column(Integer)
    response_time_ms = Column(Integer)
    was_adversarial = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


async def init_db():
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    """Dependency to get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
