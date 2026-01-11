from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import json

from app.models.database import Conversation, Message


class ConversationRepository:
    """Repository for conversation data operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_conversation(self, session_id: str) -> Conversation:
        """Get existing conversation or create new one."""
        result = await self.db.execute(
            select(Conversation).where(Conversation.session_id == session_id)
        )
        conversation = result.scalar_one_or_none()

        if not conversation:
            conversation = Conversation(session_id=session_id)
            self.db.add(conversation)
            await self.db.commit()
            await self.db.refresh(conversation)

        return conversation

    async def get_conversation(self, session_id: str) -> Optional[Conversation]:
        """Get conversation by session ID."""
        result = await self.db.execute(
            select(Conversation).where(Conversation.session_id == session_id)
        )
        return result.scalar_one_or_none()

    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[dict] = None
    ) -> Message:
        """Add a message to a conversation."""
        conversation = await self.get_or_create_conversation(session_id)

        message = Message(
            conversation_id=conversation.id,
            role=role,
            content=content,
            message_metadata=json.dumps(metadata) if metadata else None
        )
        self.db.add(message)
        conversation.last_activity = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def get_messages(
        self,
        session_id: str,
        limit: int = 20
    ) -> List[Message]:
        """Get messages for a conversation."""
        conversation = await self.get_conversation(session_id)
        if not conversation:
            return []

        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        messages = result.scalars().all()
        return list(reversed(messages))

    async def get_conversation_history(
        self,
        session_id: str,
        limit: int = 10
    ) -> List[dict]:
        """Get formatted conversation history for context."""
        messages = await self.get_messages(session_id, limit)
        return [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

    async def clear_conversation(self, session_id: str) -> bool:
        """Clear all messages in a conversation."""
        conversation = await self.get_conversation(session_id)
        if not conversation:
            return False

        result = await self.db.execute(
            select(Message).where(Message.conversation_id == conversation.id)
        )
        messages = result.scalars().all()

        for message in messages:
            await self.db.delete(message)

        await self.db.commit()
        return True
