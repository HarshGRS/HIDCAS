from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from database import get_db
from services.rag_service import get_or_rebuild_index, query_document, ask_llm
from routes.auth_routes import get_current_user
from models import User, Document, Conversation, Message

router = APIRouter(tags=["Chat"])


class ChatRequest(BaseModel):
    conversation_id: Optional[int] = None  # existing conversation
    document_id: Optional[int] = None
    document_name: Optional[str] = None
    message: str


@router.post("/chat")
def chat_with_document(
    request: ChatRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    doc = None
    conversation = None

    # If existing conversation ID is there, use it
    if request.conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == request.conversation_id,
            Conversation.user_id == user.id
        ).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        doc = conversation.document

    else:
        # New conversation - find document by ID or name
        if request.document_id:
            doc = db.query(Document).filter(
                Document.id == request.document_id
            ).first()
        elif request.document_name:
            doc = db.query(Document).filter(
                Document.filename.ilike(f"%{request.document_name}%"),
                Document.owner_id == user.id
            ).first()

        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        # Check if conversation already exists for this user and document
        conversation = db.query(Conversation).filter(
            Conversation.user_id == user.id,
            Conversation.document_id == doc.id
        ).first()

        # If not, create new conversation
        if not conversation:
            conversation = Conversation(
                user_id=user.id,
                document_id=doc.id
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)

    # RAG — take relevant chunks and ask LLM
    get_or_rebuild_index(doc.id, db)
    relevant_chunks = query_document(doc.id, request.message)

    if not relevant_chunks:
        # Still save message
        db.add(Message(conversation_id=conversation.id, role="user", content=request.message))
        db.add(Message(conversation_id=conversation.id, role="assistant", content="No relevant information found."))
        db.commit()
        return {
            "conversation_id": conversation.id,
            "document_name": doc.filename,
            "answer": "No relevant information found."
        }

    context = "\n\n".join(relevant_chunks)
    answer = ask_llm(context, request.message)

    # Messages save 
    db.add(Message(conversation_id=conversation.id, role="user", content=request.message))
    db.add(Message(conversation_id=conversation.id, role="assistant", content=answer))
    db.commit()

    return {
        "conversation_id": conversation.id,
        "document_name": doc.filename,
        "answer": answer
    }


# Conversations list — for sidebar
@router.get("/conversations")
def get_conversations(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    conversations = db.query(Conversation).filter(
        Conversation.user_id == user.id
    ).order_by(Conversation.created_at.desc()).all()

    return [
        {
            "conversation_id": c.id,
            "document_id": c.document_id,
            "document_name": c.document.filename,
            "created_at": c.created_at
        }
        for c in conversations
    ]


# Messages list for a conversation
@router.get("/conversations/{conversation_id}/messages")
def get_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == user.id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc()).all()

    return [
        {
            "role": m.role,
            "content": m.content,
            "created_at": m.created_at
        }
        for m in messages
    ]


@router.delete("/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == user.id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Delete messages 
    db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).delete()

    # Delete conversation
    db.delete(conversation)
    db.commit()

    return {"message": "Conversation deleted successfully"}