"""
Chunking module - Splits long text into smaller, manageable chunks.

Why chunk?
- LLMs have token limits
- Embeddings work better on focused text
- Retrieval is more precise with smaller chunks
"""

from typing import List, Dict
from app.core.config import settings


class ChunkingService:
    """
    Service for splitting text into overlapping chunks.
    
    Overlapping ensures that information isn't lost at chunk boundaries.
    """
    
    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None
    ):
        """
        Initialize chunking service.
        
        Args:
            chunk_size: Characters per chunk (default from config)
            chunk_overlap: Overlap between chunks (default from config)
        """
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
    
    def chunk_text(
        self,
        text: str,
        metadata: Dict = None
    ) -> List[Dict]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: The long text to split
            metadata: Optional metadata to attach to each chunk
        
        Returns:
            List of dictionaries, each containing:
            - content: The chunk text
            - metadata: Metadata with chunk_index added
        
        Example:
            Input: "Lorem ipsum dolor sit amet..." (10,000 characters)
            Output: [
                {
                    "content": "Lorem ipsum dolor...",  # First 1000 chars
                    "metadata": {"chunk_index": 0, "url": "..."}
                },
                {
                    "content": "...dolor sit amet...",  # Chars 800-1800 (overlap!)
                    "metadata": {"chunk_index": 1, "url": "..."}
                },
                ...
            ]
        
        Why overlap?
        - If a sentence is split across chunks, overlap keeps it together
        - Improves retrieval quality
        """
        if metadata is None:
            metadata = {}
        
        # Clean the text
        text = text.strip()
        
        # If text is shorter than chunk_size, return as single chunk
        if len(text) <= self.chunk_size:
            return [{
                "content": text,
                "metadata": {**metadata, "chunk_index": 0}
            }]
        
        # Split into chunks with overlap
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(text):
            # Calculate end position
            end = start + self.chunk_size
            
            # Extract chunk
            chunk_text = text[start:end]
            
            # Try to break at sentence boundary (don't split mid-sentence)
            if end < len(text):  # Not the last chunk
                # Look for sentence endings (., !, ?)
                last_period = chunk_text.rfind('. ')
                last_exclaim = chunk_text.rfind('! ')
                last_question = chunk_text.rfind('? ')
                
                # Find the last sentence ending
                last_sentence_end = max(last_period, last_exclaim, last_question)
                
                # If we found a sentence ending, break there
                if last_sentence_end > self.chunk_size * 0.5:  # At least halfway through
                    end = start + last_sentence_end + 2  # +2 to include the punctuation and space
                    chunk_text = text[start:end]
            
            # Add chunk with metadata
            chunks.append({
                "content": chunk_text.strip(),
                "metadata": {
                    **metadata,
                    "chunk_index": chunk_index,
                    "chunk_size": len(chunk_text)
                }
            })
            
            # Move start position (with overlap)
            start = end - self.chunk_overlap
            chunk_index += 1
            
            # Safety check to prevent infinite loop
            if start >= len(text):
                break
        
        return chunks
    
    def chunk_multiple_texts(
        self,
        texts: List[Dict]
    ) -> List[Dict]:
        """
        Chunk multiple texts at once.
        
        Args:
            texts: List of dicts with 'content' and optional 'metadata'
        
        Returns:
            Flattened list of all chunks
        
        Example:
            >>> chunker = ChunkingService()
            >>> texts = [
                {"content": "Page 1 content...", "metadata": {"url": "page1"}},
                {"content": "Page 2 content...", "metadata": {"url": "page2"}}
            ]
            >>> all_chunks = chunker.chunk_multiple_texts(texts)
        """
        all_chunks = []
        
        for text_dict in texts:
            content = text_dict.get("content", "")
            metadata = text_dict.get("metadata", {})
            
            chunks = self.chunk_text(content, metadata)
            all_chunks.extend(chunks)
        
        return all_chunks


# Create singleton instance
chunking_service = ChunkingService()