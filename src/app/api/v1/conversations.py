"""Conversations & messaging endpoints + WebSocket."""
import uuid
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query, status
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.db.base import get_db, async_session
from app.models.tables import Coach, Client, Conversation, Message
from app.api.deps import get_current_coach
from app.schemas.conversation import MessageCreate, MessageRead, ConversationRead, PaginatedMessages
from app.services.auth import decode_token
from app.services.websocket import manager

logger = logging.getLogger("mycoach.conversations")
router = APIRouter(prefix="/conversations", tags=["conversations"])


# ── Helper: auto-create conversation on client creation ──────────────
async def ensure_conversation(db: AsyncSession, coach_id: uuid.UUID, client_id: uuid.UUID) -> Conversation:
    """Get or create a conversation for a coach-client pair."""
    result = await db.execute(
        select(Conversation).where(
            Conversation.coach_id == coach_id,
            Conversation.client_id == client_id,
        )
    )
    conv = result.scalar_one_or_none()
    if conv is None:
        conv = Conversation(coach_id=coach_id, client_id=client_id)
        db.add(conv)
        await db.flush()
        await db.refresh(conv)
    return conv


# ── REST endpoints ───────────────────────────────────────────────────

@router.get("", response_model=list[ConversationRead])
async def list_conversations(
    db: AsyncSession = Depends(get_db),
    coach: Coach = Depends(get_current_coach),
):
    """List all conversations for the coach with last message & unread count."""
    # Get conversations
    result = await db.execute(
        select(Conversation).where(Conversation.coach_id == coach.id).order_by(Conversation.created_at.desc())
    )
    conversations = result.scalars().all()

    out = []
    for conv in conversations:
        # Last message
        last_msg_result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conv.id)
            .order_by(Message.created_at.desc())
            .limit(1)
        )
        last_msg = last_msg_result.scalar_one_or_none()

        # Unread count (messages from client that coach hasn't read)
        unread_result = await db.execute(
            select(func.count()).where(
                Message.conversation_id == conv.id,
                Message.sender_type == "client",
                Message.read_at.is_(None),
            )
        )
        unread = unread_result.scalar_one()

        out.append(ConversationRead(
            id=conv.id,
            coach_id=conv.coach_id,
            client_id=conv.client_id,
            created_at=conv.created_at,
            last_message=MessageRead.model_validate(last_msg) if last_msg else None,
            unread_count=unread,
        ))
    return out


@router.get("/{conversation_id}/messages", response_model=PaginatedMessages)
async def list_messages(
    conversation_id: uuid.UUID,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    coach: Coach = Depends(get_current_coach),
):
    """Paginated messages for a conversation."""
    # Verify ownership
    conv = await _get_conversation_or_404(db, conversation_id, coach.id)

    total_result = await db.execute(
        select(func.count()).where(Message.conversation_id == conv.id)
    )
    total_count = total_result.scalar_one()

    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conv.id)
        .order_by(Message.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    messages = result.scalars().all()

    return PaginatedMessages(
        items=[MessageRead.model_validate(m) for m in messages],
        total_count=total_count,
        limit=limit,
        offset=offset,
    )


@router.post("/{conversation_id}/messages", response_model=MessageRead, status_code=status.HTTP_201_CREATED)
async def send_message(
    conversation_id: uuid.UUID,
    body: MessageCreate,
    db: AsyncSession = Depends(get_db),
    coach: Coach = Depends(get_current_coach),
):
    """Send a message (as coach) and broadcast via WS."""
    conv = await _get_conversation_or_404(db, conversation_id, coach.id)

    msg = Message(
        conversation_id=conv.id,
        sender_type="coach",
        sender_id=coach.id,
        content=body.content,
    )
    db.add(msg)
    await db.flush()
    await db.refresh(msg)

    # Broadcast to WS clients
    msg_data = MessageRead.model_validate(msg).model_dump(mode="json")
    await manager.broadcast(conv.id, {"type": "new_message", "data": msg_data})

    return msg


@router.patch("/{conversation_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_as_read(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    coach: Coach = Depends(get_current_coach),
):
    """Mark all unread messages in a conversation as read."""
    conv = await _get_conversation_or_404(db, conversation_id, coach.id)

    result = await db.execute(
        select(Message).where(
            Message.conversation_id == conv.id,
            Message.sender_type == "client",
            Message.read_at.is_(None),
        )
    )
    for msg in result.scalars().all():
        msg.read_at = datetime.now(timezone.utc)
    await db.flush()


async def _get_conversation_or_404(db: AsyncSession, conversation_id: uuid.UUID, coach_id: uuid.UUID) -> Conversation:
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id, Conversation.coach_id == coach_id)
    )
    conv = result.scalar_one_or_none()
    if conv is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return conv


# ── WebSocket ────────────────────────────────────────────────────────

@router.websocket("/ws/{conversation_id}")
async def websocket_endpoint(
    conversation_id: uuid.UUID,
    ws: WebSocket,
    token: str = Query(...),
):
    """WebSocket for real-time messaging on a conversation."""
    # Auth via query param
    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        await ws.close(code=4001, reason="Invalid token")
        return

    coach_id = uuid.UUID(payload["sub"])

    # Verify conversation belongs to coach
    async with async_session() as db:
        result = await db.execute(
            select(Conversation).where(Conversation.id == conversation_id, Conversation.coach_id == coach_id)
        )
        conv = result.scalar_one_or_none()
        if conv is None:
            await ws.close(code=4004, reason="Conversation not found")
            return

    await manager.connect(conversation_id, ws)
    try:
        while True:
            data = await ws.receive_json()
            msg_type = data.get("type", "")

            if msg_type == "pong":
                continue

            if msg_type == "message":
                content = data.get("content", "").strip()
                if not content:
                    continue
                # Save and broadcast
                async with async_session() as db:
                    msg = Message(
                        conversation_id=conversation_id,
                        sender_type="coach",
                        sender_id=coach_id,
                        content=content,
                    )
                    db.add(msg)
                    await db.commit()
                    await db.refresh(msg)
                    msg_data = MessageRead.model_validate(msg).model_dump(mode="json")

                await manager.broadcast(conversation_id, {"type": "new_message", "data": msg_data})

    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error("WS error: %s", e)
    finally:
        manager.disconnect(conversation_id, ws)
