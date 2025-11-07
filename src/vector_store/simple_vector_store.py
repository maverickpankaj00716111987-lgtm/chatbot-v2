import numpy as np
from typing import List, Dict, Tuple, Optional
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class SimpleVectorStore:
    def __init__(self, dimension: int = 1536, storage_path: str = "vector_store"):
        self.dimension = dimension
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.vectors: np.ndarray = np.array([]).reshape(0, dimension)
        self.documents: List[Dict] = []
        self.metadata: List[Dict] = []
        
        self.load()
    
    def add(self, vectors: List[List[float]], documents: List[str], metadata: List[Dict] = None):
        if metadata is None:
            metadata = [{} for _ in documents]
        
        vectors_array = np.array(vectors)
        
        if self.vectors.size == 0:
            self.vectors = vectors_array
        else:
            self.vectors = np.vstack([self.vectors, vectors_array])
        
        self.documents.extend(documents)
        self.metadata.extend(metadata)
        
        logger.info(f"Added {len(documents)} documents to vector store")
    
    def search(self, query_vector: List[float], k: int = 5) -> List[Tuple[str, float, Dict]]:
        if self.vectors.size == 0:
            logger.warning("Vector store is empty")
            return []
        
        query_array = np.array(query_vector).reshape(1, -1)
        
        similarities = np.dot(self.vectors, query_array.T).flatten()
        norms = np.linalg.norm(self.vectors, axis=1) * np.linalg.norm(query_array)
        cosine_similarities = similarities / (norms + 1e-10)
        
        top_k_indices = np.argsort(cosine_similarities)[-k:][::-1]
        
        results = []
        for idx in top_k_indices:
            results.append((
                self.documents[idx],
                float(cosine_similarities[idx]),
                self.metadata[idx]
            ))
        
        logger.info(f"Retrieved top {k} documents from vector store")
        return results
    
    def save(self):
        try:
            np.save(self.storage_path / "vectors.npy", self.vectors)
            
            with open(self.storage_path / "documents.json", "w") as f:
                json.dump(self.documents, f)
            
            with open(self.storage_path / "metadata.json", "w") as f:
                json.dump(self.metadata, f)
            
            logger.info("Vector store saved successfully")
        except Exception as e:
            logger.error(f"Error saving vector store: {e}")
    
    def load(self):
        try:
            vectors_path = self.storage_path / "vectors.npy"
            docs_path = self.storage_path / "documents.json"
            meta_path = self.storage_path / "metadata.json"
            
            if vectors_path.exists() and docs_path.exists() and meta_path.exists():
                self.vectors = np.load(vectors_path)
                
                with open(docs_path, "r") as f:
                    self.documents = json.load(f)
                
                with open(meta_path, "r") as f:
                    self.metadata = json.load(f)
                
                logger.info(f"Loaded {len(self.documents)} documents from vector store")
        except Exception as e:
            logger.warning(f"Could not load vector store: {e}. Starting fresh.")
    
    def clear(self):
        self.vectors = np.array([]).reshape(0, self.dimension)
        self.documents = []
        self.metadata = []
        logger.info("Vector store cleared")
    
    def __len__(self):
        return len(self.documents)
