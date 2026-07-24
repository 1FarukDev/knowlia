from openai import OpenAI
from typing import List
from app.core.config import settings


class EmbeddingService:
   
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.EMBEDDING_MODEL
    
    def generate_embedding(self, text: str) -> List[float]:
        text = text.replace("\n", " ").strip()
        response = self.client.embeddings.create(
            input=text,
            model=self.model
        )
        embedding = response.data[0].embedding
        
        return embedding
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        cleaned_texts = [text.replace("\n", " ").strip() for text in texts]
        response = self.client.embeddings.create(
            input=cleaned_texts,
            model=self.model
        )
        
       
        embeddings = [item.embedding for item in response.data]
        
        return embeddings



embedding_service = EmbeddingService()