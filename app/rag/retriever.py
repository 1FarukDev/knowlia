from typing import List, Dict
from app.rag.embeddings import embedding_service
from app.rag.vector_store import vector_store
from app.core.config import settings


class Retriever:
    """
    Retrieves relevant text chunks for a given question.
    
    Flow:
    1. Convert question to embedding
    2. Search vector store for similar chunks
    3. Return top-K most relevant chunks
    """
    
    def __init__(self, top_k: int = None):
        """
        Initialize retriever.
        
        Args:
            top_k: Number of chunks to retrieve (default from config)
        """
        self.top_k = top_k or settings.TOP_K_RESULTS
    
    def retrieve(self, question: str) -> List[Dict]:
        """
        Retrieve relevant chunks for a question.
        
        Args:
            question: User's question
        
        Returns:
            List of dictionaries with:
            - content: The chunk text
            - metadata: Source info (URL, title, etc.)
            - score: Similarity score (0-1, higher = more relevant)
        
        Example:
            >>> retriever = Retriever()
            >>> results = retriever.retrieve("What is your pricing?")
            >>> print(results[0]['content'])
            "Our pricing starts at $99 per month..."
        """
        # Step 1: Generate embedding for the question
        question_embedding = embedding_service.generate_embedding(question)
        
        # Step 2: Search vector store
        search_results = vector_store.search(
            query_embedding=question_embedding,
            top_k=self.top_k
        )
        
        # Step 3: Format results
        retrieved_chunks = []
        
        for i, (doc, metadata, distance) in enumerate(zip(
            search_results['documents'],
            search_results['metadatas'],
            search_results['distances']
        )):
            # Convert distance to similarity score (0-1)
            # Distance is cosine distance (0 = identical, 2 = opposite)
            # Similarity = 1 - (distance / 2)
            similarity_score = 1 - (distance / 2)
            
            retrieved_chunks.append({
                'content': doc,
                'metadata': metadata,
                'score': similarity_score,
                'rank': i + 1
            })
        
        return retrieved_chunks
    
    def retrieve_with_filter(
        self,
        question: str,
        metadata_filter: Dict
    ) -> List[Dict]:
        """
        Retrieve chunks filtered by metadata.
        
        Useful for searching within specific pages or sources.
        
        Args:
            question: User's question
            metadata_filter: Filter criteria (e.g., {"url": "example.com/pricing"})
        
        Returns:
            Filtered list of relevant chunks
        
        Example:
            >>> retriever = Retriever()
            >>> # Only search pricing page
            >>> results = retriever.retrieve_with_filter(
                "What's the cost?",
                {"url": "example.com/pricing"}
            )
        """
        # Note: ChromaDB's query doesn't support where filters directly
        # So we retrieve all, then filter manually
        # For production, you might want a more efficient approach
        
        all_results = self.retrieve(question)
        
        # Filter by metadata
        filtered_results = []
        for result in all_results:
            match = True
            for key, value in metadata_filter.items():
                if result['metadata'].get(key) != value:
                    match = False
                    break
            
            if match:
                filtered_results.append(result)
        
        return filtered_results[:self.top_k]


# Create singleton instance
retriever = Retriever()