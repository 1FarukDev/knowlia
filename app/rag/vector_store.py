import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Optional
from app.core.config import settings
import uuid


class VectorStore:
   
    
    def __init__(self):
       
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_DATA_PATH,
            settings=ChromaSettings(
                anonymized_telemetry=False,
            )
        )
        self.collection = self.client.get_or_create_collection(
            name=settings.COLLECTION_NAME,
            metadata={"description": "Knowlia RAG knowledge base"}
        )
    
    def add_chunks(
        self,
        chunks: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict],
        ids: Optional[List[str]] = None
    ) -> None:
 
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in chunks]
        
        self.collection.add(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas
        )
        
        print(f"✅ Added {len(chunks)} chunks to vector store")
    
    def search(
        self,
        query_embedding: List[float],
        top_k: int = None
    ) -> Dict:
        if top_k is None:
            top_k = settings.TOP_K_RESULTS
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        return {
            "documents": results["documents"][0],
            "metadatas": results["metadatas"][0],
            "distances": results["distances"][0]
        }
    
    def count(self) -> int:
        return self.collection.count()
    
    def clear(self) -> None:
        self.client.delete_collection(settings.COLLECTION_NAME)
        self.collection = self.client.get_or_create_collection(
            name=settings.COLLECTION_NAME,
            metadata={"description": "Knowlia RAG knowledge base"}
        )
        print("🗑️ Vector store cleared")
    
    def get_by_metadata(self, metadata_filter: Dict) -> Dict:
        results = self.collection.get(
            where=metadata_filter,
            include=["documents", "metadatas"]
        )
        return results


vector_store = VectorStore()