from typing import List, Dict, Any
import logging
from transformers import pipeline
from langchain_huggingface import HuggingFacePipeline, HuggingFaceEmbeddings
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from tenacity import retry, stop_after_attempt, wait_exponential
from src.models.config import settings

logger = logging.getLogger(__name__)


class LLMManager:
    def __init__(self):
        self.primary_model = None
        self.embedding_model = None
        self.current_model_name = "huggingface/flan-t5-base"

        self._initialize_models()

    def _initialize_models(self):
        try:
            # ✅ Load a local Hugging Face text generation pipeline (CPU-friendly)
            generation_pipeline = pipeline(
                "text2text-generation",
                model="google/flan-t5-base",  # small and fast
                device=-1  # CPU only
            )

            self.primary_model = HuggingFacePipeline(pipeline=generation_pipeline)
            logger.info("Initialized Hugging Face model: google/flan-t5-base")

            # ✅ Use a SentenceTransformer for embeddings
            self.embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            logger.info("Initialized embedding model: all-MiniLM-L6-v2")

        except Exception as e:
            logger.error(f"Error initializing Hugging Face models: {e}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        try:
            if self.primary_model is None:
                raise ValueError("Primary model not initialized")

            conversation = []
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "system":
                    conversation.append(f"System: {content}")
                elif role == "assistant":
                    conversation.append(f"Assistant: {content}")
                else:
                    conversation.append(f"User: {content}")

            input_text = "\n".join(conversation) + "\nAssistant:"
            response = self.primary_model.invoke(input_text)
            logger.info("Generated response using Hugging Face model")
            return response.strip()

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise

    def generate_embedding(self, text: str) -> List[float]:
        try:
            if self.embedding_model is None:
                raise ValueError("Embedding model not initialized")

            embedding = self.embedding_model.embed_query(text)
            logger.info("Generated embedding with local model")
            return embedding

        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        try:
            if self.embedding_model is None:
                raise ValueError("Embedding model not initialized")

            embeddings = self.embedding_model.embed_documents(texts)
            logger.info(f"Generated {len(embeddings)} embeddings with local model")
            return embeddings

        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise

    def get_current_model_info(self) -> Dict[str, Any]:
        return {
            "primary_model": "google/flan-t5-base",
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "primary_available": self.primary_model is not None,
            "embedding_available": self.embedding_model is not None
        }
