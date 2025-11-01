from typing import List, Dict, Optional, Any
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from src.models.config import settings

logger = logging.getLogger(__name__)


class LLMManager:
    def __init__(self):
        self.primary_model = None
        self.fallback_model = None
        self.embedding_model = None
        self.current_model_name = settings.primary_model
        
        self._initialize_models()
    
    def _initialize_models(self):
        try:
            if settings.openai_api_key:
                self.primary_model = ChatOpenAI(
                    model=settings.primary_model,
                    temperature=settings.temperature,
                    max_tokens=settings.max_tokens,
                    api_key=settings.openai_api_key
                )
                self.embedding_model = OpenAIEmbeddings(
                    model=settings.embedding_model,
                    api_key=settings.openai_api_key
                )
                logger.info(f"Initialized primary model: {settings.primary_model}")
            
            if settings.anthropic_api_key:
                self.fallback_model = ChatAnthropic(
                    model=settings.fallback_model,
                    temperature=settings.temperature,
                    max_tokens=settings.max_tokens,
                    api_key=settings.anthropic_api_key
                )
                logger.info(f"Initialized fallback model: {settings.fallback_model}")
                
        except Exception as e:
            logger.error(f"Error initializing models: {e}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def generate_response(
        self,
        messages: List[Dict[str, str]],
        use_fallback: bool = False
    ) -> str:
        try:
            model = self.fallback_model if use_fallback else self.primary_model
            
            if model is None:
                raise ValueError("No model available")
            
            langchain_messages = []
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                
                if role == "system":
                    langchain_messages.append(SystemMessage(content=content))
                elif role == "assistant":
                    langchain_messages.append(AIMessage(content=content))
                else:
                    langchain_messages.append(HumanMessage(content=content))
            
            response = model.invoke(langchain_messages)
            logger.info(f"Generated response using {'fallback' if use_fallback else 'primary'} model")
            return response.content
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            
            if not use_fallback and self.fallback_model is not None:
                logger.info("Attempting fallback model")
                return self.generate_response(messages, use_fallback=True)
            raise
    
    def generate_embedding(self, text: str) -> List[float]:
        try:
            if self.embedding_model is None:
                raise ValueError("Embedding model not initialized")
            
            embedding = self.embedding_model.embed_query(text)
            logger.info("Generated embedding")
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        try:
            if self.embedding_model is None:
                raise ValueError("Embedding model not initialized")
            
            embeddings = self.embedding_model.embed_documents(texts)
            logger.info(f"Generated {len(embeddings)} embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    def get_current_model_info(self) -> Dict[str, Any]:
        return {
            "primary_model": settings.primary_model,
            "fallback_model": settings.fallback_model,
            "embedding_model": settings.embedding_model,
            "primary_available": self.primary_model is not None,
            "fallback_available": self.fallback_model is not None,
            "embedding_available": self.embedding_model is not None
        }
