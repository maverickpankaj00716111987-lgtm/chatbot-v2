from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import List, Optional
from pydantic import BaseModel
import logging
import shutil
from pathlib import Path
from src.utils.document_processor import DocumentProcessor
from src.utils.llm_manager import LLMManager
from src.utils.conversation_manager import ConversationManager
from src.vector_store.simple_vector_store import SimpleVectorStore
from src.agent.graph import RAGAgent
from src.database.models import Document as DocumentModel, DocumentChunk
from src.database.connection import get_db
from src.models.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

llm_manager = LLMManager()
vector_store = SimpleVectorStore()
rag_agent = RAGAgent(llm_manager, vector_store)
doc_processor = DocumentProcessor(
    chunk_size=settings.chunk_size,
    chunk_overlap=settings.chunk_overlap
)


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    retrieved_docs: List[dict]
    metadata: dict


class SessionResponse(BaseModel):
    session_id: str
    created_at: str
    updated_at: str
    message_count: int
    metadata: dict


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        session_id = request.session_id
        if not session_id:
            session_id = ConversationManager.create_session()
        
        ConversationManager.add_message(session_id, "user", request.message)
        
        conversation_history = ConversationManager.get_conversation_history(session_id)
        
        result = rag_agent.run(
            query=request.message,
            session_id=session_id,
            conversation_history=conversation_history
        )
        
        ConversationManager.add_message(
            session_id,
            "assistant",
            result["response"],
            metadata=result.get("metadata", {})
        )
        
        return ChatResponse(
            response=result["response"],
            session_id=session_id,
            retrieved_docs=result.get("retrieved_docs", []),
            metadata=result.get("metadata", {})
        )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        upload_dir = Path("uploaded_docs")
        upload_dir.mkdir(exist_ok=True)
        
        safe_filename = Path(file.filename).name
        file_path = upload_dir / safe_filename
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        chunks = doc_processor.process_document(str(file_path))
        
        texts = [chunk["content"] for chunk in chunks]
        embeddings = llm_manager.generate_embeddings(texts)
        
        metadata_list = [
            {
                "filename": chunk["filename"],
                "chunk_index": chunk["chunk_index"],
                "start_char": chunk["start_char"],
                "end_char": chunk["end_char"]
            }
            for chunk in chunks
        ]
        
        vector_store.add(embeddings, texts, metadata_list)
        vector_store.save()
        
        with get_db() as db:
            full_text = " ".join(texts)
            doc = DocumentModel(
                filename=safe_filename,
                content=full_text[:10000],
                chunk_count=len(chunks),
                embedding_metadata={"embedding_model": settings.embedding_model}
            )
            db.add(doc)
            db.flush()
            
            for i, chunk in enumerate(chunks):
                doc_chunk = DocumentChunk(
                    document_id=doc.id,
                    chunk_index=i,
                    content=chunk["content"],
                    chunk_metadata=metadata_list[i]
                )
                db.add(doc_chunk)
            
            db.commit()
        
        logger.info(f"Uploaded and processed document: {safe_filename}")
        
        return {
            "filename": safe_filename,
            "chunks_created": len(chunks),
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions", response_model=List[SessionResponse])
async def get_sessions():
    try:
        sessions = ConversationManager.get_all_sessions()
        return sessions
    except Exception as e:
        logger.error(f"Error getting sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    try:
        session = ConversationManager.get_session_details(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/new")
async def create_new_session():
    try:
        session_id = ConversationManager.create_session(
            metadata={"created_via": "api"}
        )
        return {"session_id": session_id}
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents")
async def get_documents():
    try:
        with get_db() as db:
            docs = db.query(DocumentModel).all()
            return [
                {
                    "id": doc.id,
                    "filename": doc.filename,
                    "chunk_count": doc.chunk_count,
                    "uploaded_at": doc.uploaded_at.isoformat()
                }
                for doc in docs
            ]
    except Exception as e:
        logger.error(f"Error getting documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    model_info = llm_manager.get_current_model_info()
    return {
        "status": "healthy",
        "vector_store_size": len(vector_store),
        "models": model_info
    }
