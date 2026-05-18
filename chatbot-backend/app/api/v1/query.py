from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.user import User
from app.models.chat import Chat
from app.models.message import Message
from app.schemas.query import QueryRequest, QueryResponse
from app.core.security import get_current_user
from app.services.rag import retrieve_and_query, stream_rag_query

router = APIRouter()

@router.post("/", response_model=QueryResponse)
async def query_documents(
    query_data: QueryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if query_data.chat_id:
        result = await db.execute(select(Chat).where(Chat.id == query_data.chat_id))
        chat = result.scalar_one_or_none()
        if not chat or chat.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    else:
        new_chat = Chat(user_id=current_user.id, title=query_data.query[:50])
        db.add(new_chat)
        await db.commit()
        await db.refresh(new_chat)
        query_data.chat_id = new_chat.id
    
    user_message = Message(
        chat_id=query_data.chat_id,
        role="user",
        content=query_data.query
    )
    db.add(user_message)
    await db.commit()
    
    answer, sources = await retrieve_and_query(
        query=query_data.query,
        user_id=current_user.id,
        file_ids=query_data.file_ids,
        db=db
    )
    
    assistant_message = Message(
        chat_id=query_data.chat_id,
        role="assistant",
        content=answer,
        sources=sources
    )
    db.add(assistant_message)
    await db.commit()
    await db.refresh(assistant_message)
    
    return QueryResponse(
        answer=answer,
        sources=sources,
        chat_id=query_data.chat_id,
        message_id=assistant_message.id
    )

@router.get("/stream")
async def stream_query(
    query: str,
    chat_id: int = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if chat_id:
        result = await db.execute(select(Chat).where(Chat.id == chat_id))
        chat = result.scalar_one_or_none()
        if not chat or chat.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    else:
        new_chat = Chat(user_id=current_user.id, title=query[:50])
        db.add(new_chat)
        await db.commit()
        await db.refresh(new_chat)
        chat_id = new_chat.id
    
    user_message = Message(chat_id=chat_id, role="user", content=query)
    db.add(user_message)
    await db.commit()
    
    return StreamingResponse(
        stream_rag_query(query, current_user.id, chat_id, db),
        media_type="text/event-stream"
    )
