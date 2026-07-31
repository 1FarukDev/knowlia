import cohere
from typing import List, Dict
from app.core.config import settings


class Reranker:
    """
    Reranks retrieved chunks for better relevance.
    
    Uses Cohere's rerank model to score chunks based on
    relevance to the question. This improves answer quality
    by prioritizing the most relevant context.
    
    Flow:
    1. Retrieve 10 chunks from vector search (similarity-based)
    2. Rerank those 10 chunks (relevance-based)
    3. Return top 5 most relevant
    """
    
    def __init__(self):
        """Initialize Cohere client if API key is available."""
        if settings.COHERE_API_KEY:
            self.client = cohere.Client(settings.COHERE_API_KEY)
            self.enabled = True
        else:
            self.enabled = False
            print("⚠️ Cohere API key not found. Reranking disabled.")
    
    
    def rerank(self, query: str, chunks: List[Dict], top_k: int = 5) -> List[Dict]:
        """
        Rerank chunks by relevance to query.
        
        Args:
            query: User's question
            chunks: Retrieved chunks from vector search
            top_k: Number of top chunks to return after reranking
        
        Returns:
            Reranked chunks (best first) with 'rerank_score' added
        
        Example:
            >>> reranker = Reranker()
            >>> chunks = retriever.retrieve("What's the pricing?", top_k=10)
            >>> best_chunks = reranker.rerank("What's the pricing?", chunks, top_k=5)
            >>> print(best_chunks[0]['rerank_score'])
            0.987
        """
        if not self.enabled or not chunks:
            return chunks[:top_k]
        
        # Extract text content from chunks
        documents = [chunk["content"] for chunk in chunks]
        
        # Call Cohere rerank API
        results = self.client.rerank(
            query=query,
            documents=documents,
            top_n=top_k,
            model="rerank-english-v3.0",
        )
        
        # Map results back to original chunks with scores
        reranked_chunks = []
        for result in results.results:
            original_chunk = chunks[result.index]
            original_chunk["rerank_score"] = result.relevance_score
            reranked_chunks.append(original_chunk)
            
        return reranked_chunks


# Create singleton instance
reranker = Reranker()