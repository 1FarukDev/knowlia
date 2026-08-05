from rank_bm25 import BM25Okapi
from typing import List, Dict
import nltk
from nltk.tokenize import word_tokenize

# Download tokenizer (run once)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')


class BM25Search:
    """
    Keyword-based search using BM25 algorithm.
    
    BM25 ranks documents by how well they match query keywords.
    Works alongside vector search for hybrid retrieval.
    """
    
    def __init__(self):
        self.bm25 = None
        self.chunks = []
    
    def build_index(self, chunks: List[Dict]):
        """
        Build BM25 index from chunks.
        
        Args:
            chunks: List of chunk dictionaries with 'content' field
        """
        self.chunks = chunks
        # Tokenize all chunk content
        tokenized_chunks = [
            word_tokenize(chunk["content"].lower()) 
            for chunk in chunks
        ]
        self.bm25 = BM25Okapi(tokenized_chunks)
        print(f"✅ BM25 index built with {len(chunks)} chunks")
    
    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        Search chunks using keyword matching.
        
        Args:
            query: User's search query
            top_k: Number of results to return
            
        Returns:
            List of chunks sorted by BM25 score
        """
        if not self.bm25:
            return []
        
        # Tokenize query
        tokenized_query = word_tokenize(query.lower())
        
        # Get scores for all chunks
        scores = self.bm25.get_scores(tokenized_query)
        
        # Get top K indices
        top_indices = sorted(
            range(len(scores)), 
            key=lambda i: scores[i], 
            reverse=True
        )[:top_k]
        
        # Return chunks with scores
        results = []
        for idx in top_indices:
            chunk = self.chunks[idx].copy()
            chunk["bm25_score"] = float(scores[idx])
            results.append(chunk)
        
        return results


# Singleton instance
bm25_search = BM25Search()