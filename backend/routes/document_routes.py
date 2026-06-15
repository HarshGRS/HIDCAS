from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from services.text_extraction import (
    extract_text_from_pdf,
    extract_text_from_image,
    extract_text_from_docx,
    extract_text_from_excel
)
from database import get_db
from models import Document, User
from services.rbac import require_permission
from routes.auth_routes import get_current_user
import os
import shutil
import uuid
from services.rag_service import build_index, extract_project_info
from models import Document, User, Project

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("/")
def get_documents(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # Check if user has view_all_documents permission
    try:
        require_permission("view_all_documents")(user=user, db=db)
        return db.query(Document).all()
    except:
        # Otherwise return only their documents
        return db.query(Document).filter(
            Document.owner_id == user.id
        ).all()
    

UPLOAD_FOLDER = "uploads"
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png", "doc", "docx", "xlsx"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("upload_document"))
):
    # 🔹 Check extension
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only PDF, JPG, PNG, DOC allowed."
        )

    # 🔹 Check file size
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File too large. Max size is 50MB."
        )

    # 🔹 Unique filename
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)

    # 🔹 Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    extracted_text = ""

    if file_extension == "pdf":
        extracted_text = extract_text_from_pdf(file_path)
    elif file_extension in ["jpg", "jpeg", "png"]:
        extracted_text = extract_text_from_image(file_path)
    elif file_extension in ["doc", "docx"]:
        extracted_text = extract_text_from_docx(file_path)
    elif file_extension == "xlsx":
        extracted_text = extract_text_from_excel(file_path)


    # 🔹 Save metadata in DB
    new_doc = Document(
        filename=file.filename,
        file_path=file_path,
        file_size=file_size,
        file_type=file_extension,
        owner_id=user.id,
        content=extracted_text
    )
    print("File extension:", file_extension)
    print("File path:", file_path)
    print("Extracted text length:", len(extracted_text))

    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    from services.rag_service import build_index
    build_index(new_doc.id, extracted_text)

    if extracted_text:
        project_info = extract_project_info(extracted_text)
        new_project = Project(
        document_id=new_doc.id,
        company_name=project_info.get("company_name", ""),
        project_name=project_info.get("project_name", ""),
        location=project_info.get("location", ""),
        year=project_info.get("year", ""),
        budget=project_info.get("budget", ""),
        loan_amount=project_info.get("loan_amount", "")
        )
        db.add(new_project)
        db.commit()

    return {"message": "File uploaded successfully"} 


from typing import List
from schemas import DocumentResponse

@router.get("/list", response_model=List[DocumentResponse])
def list_documents(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("view_documents"))
):
    query = db.query(Document)

    # If user does NOT have permission to view all documents,
    # restrict to only their own documents
    if not user.has_permission("view_all_documents"):
        query = query.filter(Document.owner_id == user.id)

    documents = (
        query
        .order_by(Document.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return documents


from fastapi.responses import FileResponse
from fastapi import HTTPException
import os

@router.get("/{doc_id}/download")
def download_document(
    doc_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("view_documents"))
):
    document = db.query(Document).filter(Document.id == doc_id).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Check if user owns document
    if document.owner_id != user.id:

        # Check if user has global permission
        permissions = [perm.name for perm in user.role.permissions]

        if "view_all_documents" not in permissions:
            raise HTTPException(status_code=403, detail="Not authorized")

    if not os.path.exists(document.file_path):
        raise HTTPException(status_code=404, detail="File not found on server")

    return FileResponse(
        path=document.file_path,
        filename=document.filename,
        media_type="application/octet-stream"
    )

from fastapi import HTTPException
import os
from models import Document, Project, Conversation, Message

@router.delete("/{doc_id}")
def delete_document(
    doc_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("delete_document"))
):
    document = db.query(Document).filter(Document.id == doc_id).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if document.owner_id != user.id:
        permissions = [rp.permission.name for rp in user.role.role_permissions]
        if "delete_all_documents" not in permissions:
            raise HTTPException(status_code=403, detail="Not authorized")

    # Conversations and messages delete 
    conversations = db.query(Conversation).filter(
        Conversation.document_id == doc_id
    ).all()

    for conv in conversations:
        db.query(Message).filter(
            Message.conversation_id == conv.id
        ).delete()
        db.delete(conv)

    # Project delete 
    db.query(Project).filter(Project.document_id == doc_id).delete()

    # Delete from file disk
    if os.path.exists(document.file_path):
        os.remove(document.file_path)

    # Doc delete 
    db.delete(document)
    db.commit()

    return {"message": "Document deleted successfully"}


@router.get("/{doc_id}/project")
def get_project_info(
    doc_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(
        Project.document_id == doc_id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project info not found")

    return {
        "document_id": doc_id,
        "company_name": project.company_name,
        "project_name": project.project_name,
        "location": project.location,
        "year": project.year,
        "budget": project.budget,
        "loan_amount": project.loan_amount
    }


@router.get("/search")
def search_documents(
    q: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    has_all_access = False
    if user.role:
        permissions = [rp.permission.name for rp in user.role.role_permissions]
        has_all_access = "view_all_documents" in permissions

    if has_all_access:
        documents = db.query(Document).filter(
            Document.filename.ilike(f"%{q}%")
        ).all()
    else:
        documents = db.query(Document).filter(
            Document.filename.ilike(f"%{q}%"),
            Document.owner_id == user.id
        ).all()

    return [
        {"id": doc.id, "filename": doc.filename}
        for doc in documents
    ]