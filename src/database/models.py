from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class ConversationSession(Base):
    __tablename__ = "conversation_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    session_metadata = Column(JSON, default={})
    
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")
    states = relationship("AgentState", back_populates="session", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), ForeignKey("conversation_sessions.session_id"), nullable=False)
    role = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    message_metadata = Column(JSON, default={})
    
    session = relationship("ConversationSession", back_populates="messages")
    
    __table_args__ = (
        Index("idx_session_timestamp", "session_id", "timestamp"),
    )


class AgentState(Base):
    __tablename__ = "agent_states"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), ForeignKey("conversation_sessions.session_id"), nullable=False)
    state_name = Column(String(100), nullable=False)
    state_data = Column(JSON, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    execution_metadata = Column(JSON, default={})
    
    session = relationship("ConversationSession", back_populates="states")
    
    __table_args__ = (
        Index("idx_session_state_timestamp", "session_id", "state_name", "timestamp"),
    )


class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    embedding_metadata = Column(JSON, default={})
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    chunk_count = Column(Integer, default=0)
    
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding_vector = Column(Text, nullable=True)
    chunk_metadata = Column(JSON, default={})
    
    document = relationship("Document", back_populates="chunks")
    
    __table_args__ = (
        Index("idx_document_chunk", "document_id", "chunk_index"),
    )
