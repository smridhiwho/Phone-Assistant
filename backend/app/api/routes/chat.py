from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid
import logging

from app.models.database import get_db
from app.models.schemas import (
    ChatRequest, ChatResponse,
    ConversationResponse, MessageResponse
)
from app.core.agent import ShoppingAgent
from app.repositories.conversation_repository import ConversationRepository


logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Send a chat message and get AI response.

    - **session_id**: Unique identifier for the conversation session
    - **message**: The user's message/query
    - **context**: Optional additional context
    """
    logger.info("=" * 60)
    logger.info(f"[CHAT ROUTE] Incoming request")
    logger.info(f"[CHAT ROUTE] Session ID: {request.session_id}")
    logger.info(f"[CHAT ROUTE] User message: {request.message}")
    logger.info(f"[CHAT ROUTE] Context: {request.context}")
    logger.info("=" * 60)

    try:
        agent = ShoppingAgent(db)
        response = await agent.process_message(
            message=request.message,
            session_id=request.session_id,
            context=request.context
        )
        logger.info(f"[CHAT ROUTE] Response intent: {response.intent}")
        logger.info(f"[CHAT ROUTE] Response text (first 200 chars): {response.response[:200]}...")
        logger.info(f"[CHAT ROUTE] Products returned: {len(response.products)}")
        logger.info("=" * 60)
        return response
    except Exception as e:
        logger.error(f"[CHAT ROUTE] Error processing message: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing message: {str(e)}"
        )


@router.get("/history/{session_id}", response_model=ConversationResponse)
async def get_chat_history(
    session_id: str,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """
    Get chat history for a session.

    - **session_id**: The conversation session ID
    - **limit**: Maximum number of messages to return (default: 20)
    """
    conversation_repo = ConversationRepository(db)
    messages = await conversation_repo.get_messages(session_id, limit)

    return ConversationResponse(
        session_id=session_id,
        messages=[
            MessageResponse(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                metadata=None,
                created_at=msg.created_at
            )
            for msg in messages
        ]
    )


@router.post("/session")
async def create_session():
    """
    Create a new chat session.

    Returns a unique session ID for the conversation.
    """
    session_id = str(uuid.uuid4())
    return {"session_id": session_id}


@router.delete("/history/{session_id}")
async def clear_chat_history(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Clear chat history for a session.

    - **session_id**: The conversation session ID to clear
    """
    conversation_repo = ConversationRepository(db)
    success = await conversation_repo.clear_conversation(session_id)

    if success:
        return {"message": "Conversation cleared successfully"}
    else:
        return {"message": "No conversation found for this session"}
