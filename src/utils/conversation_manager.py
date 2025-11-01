from typing import List, Dict, Optional
import logging
from sqlalchemy.orm import Session
from src.database.models import ConversationSession, Message
from src.database.connection import get_db
from datetime import datetime
import uuid
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

logger = logging.getLogger(__name__)


class ConversationManager:
    @staticmethod
    def create_session(metadata: Dict = None) -> str:
        session_id = str(uuid.uuid4())
        
        try:
            with get_db() as db:
                session = ConversationSession(
                    session_id=session_id,
                    session_metadata=metadata or {},
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(session)
                db.commit()
                logger.info(f"Created new session: {session_id}")
                return session_id
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            raise
    
    @staticmethod
    def add_message(session_id: str, role: str, content: str, metadata: Dict = None):
        try:
            with get_db() as db:
                message = Message(
                    session_id=session_id,
                    role=role,
                    content=content,
                    message_metadata=metadata or {},
                    timestamp=datetime.utcnow()
                )
                db.add(message)
                
                session = db.query(ConversationSession).filter_by(session_id=session_id).first()
                if session:
                    session.updated_at = datetime.utcnow()
                
                db.commit()
                logger.info(f"Added {role} message to session {session_id}")
        except Exception as e:
            logger.error(f"Error adding message: {e}")
            raise
    
    @staticmethod
    def get_conversation_history(
        session_id: str,
        limit: Optional[int] = None
    ) -> List[BaseMessage]:
        try:
            with get_db() as db:
                query = db.query(Message).filter_by(session_id=session_id).order_by(Message.timestamp)
                
                if limit:
                    query = query.limit(limit)
                
                messages = query.all()
                
                langchain_messages = []
                for msg in messages:
                    if msg.role == "user":
                        langchain_messages.append(HumanMessage(content=msg.content))
                    elif msg.role == "assistant":
                        langchain_messages.append(AIMessage(content=msg.content))
                
                logger.info(f"Retrieved {len(langchain_messages)} messages for session {session_id}")
                return langchain_messages
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []
    
    @staticmethod
    def get_all_sessions() -> List[Dict]:
        try:
            with get_db() as db:
                sessions = db.query(ConversationSession).order_by(
                    ConversationSession.updated_at.desc()
                ).all()
                
                result = []
                for session in sessions:
                    message_count = db.query(Message).filter_by(
                        session_id=session.session_id
                    ).count()
                    
                    result.append({
                        "session_id": session.session_id,
                        "created_at": session.created_at.isoformat(),
                        "updated_at": session.updated_at.isoformat(),
                        "message_count": message_count,
                        "metadata": session.session_metadata
                    })
                
                logger.info(f"Retrieved {len(result)} sessions")
                return result
        except Exception as e:
            logger.error(f"Error getting all sessions: {e}")
            return []
    
    @staticmethod
    def get_session_details(session_id: str) -> Optional[Dict]:
        try:
            with get_db() as db:
                session = db.query(ConversationSession).filter_by(
                    session_id=session_id
                ).first()
                
                if not session:
                    return None
                
                messages = db.query(Message).filter_by(
                    session_id=session_id
                ).order_by(Message.timestamp).all()
                
                return {
                    "session_id": session.session_id,
                    "created_at": session.created_at.isoformat(),
                    "updated_at": session.updated_at.isoformat(),
                    "metadata": session.session_metadata,
                    "messages": [
                        {
                            "role": msg.role,
                            "content": msg.content,
                            "timestamp": msg.timestamp.isoformat(),
                            "metadata": msg.message_metadata
                        }
                        for msg in messages
                    ]
                }
        except Exception as e:
            logger.error(f"Error getting session details: {e}")
            return None
