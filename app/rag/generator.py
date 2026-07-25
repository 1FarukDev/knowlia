
from openai import OpenAI
from typing import List, Dict
from app.core.config import settings


class Generator:
    """
    Generates answers using OpenAI LLM with retrieved context.
    
    This is where the magic happens - combining retrieved knowledge
    with LLM intelligence to generate accurate answers.
    """
    
    def __init__(self):
        """Initialize OpenAI client"""
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.LLM_MODEL  # "gpt-4o-mini"
        self.temperature = settings.TEMPERATURE  # 0.1 (factual)
        self.max_tokens = settings.MAX_TOKENS  # 1000
    
    def generate_answer(
        self,
        question: str,
        context_chunks: List[Dict]
    ) -> Dict:
        """
        Generate an answer using LLM with retrieved context.
        
        Args:
            question: User's question
            context_chunks: List of relevant chunks from retriever
        
        Returns:
            Dictionary with:
            - answer: The generated answer
            - sources: List of source URLs
            - chunks_used: Number of chunks provided as context
        
        Example:
            >>> generator = Generator()
            >>> chunks = [
                {"content": "Pricing starts at $99", "metadata": {"url": "..."}},
                {"content": "We offer 3 plans", "metadata": {"url": "..."}}
            ]
            >>> result = generator.generate_answer("What's the pricing?", chunks)
            >>> print(result['answer'])
            "Our pricing starts at $99 per month..."
        """
        # Build context from retrieved chunks
        context = self._build_context(context_chunks)
        
        # Build the prompt
        prompt = self._build_prompt(question, context)
        
        # Call OpenAI API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": self._get_system_prompt()
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        # Extract answer
        answer = response.choices[0].message.content.strip()
        
        # Extract unique source URLs
        sources = self._extract_sources(context_chunks)
        
        return {
            'answer': answer,
            'sources': sources,
            'chunks_used': len(context_chunks),
            'model': self.model
        }
    
    def _get_system_prompt(self) -> str:
       
        return """You are a helpful AI assistant for Knowlia, a knowledge base assistant.

Your role:
- Answer questions based ONLY on the provided context
- Be accurate and precise
- If the context doesn't contain enough information, say "I don't have enough information to answer that question based on the available content."
- Do not make up information
- Cite sources when possible
- Be concise but complete

Important:
- Never hallucinate or invent information
- Only use facts from the provided context
- If uncertain, acknowledge it
- Do not add "(Source: ...)" or any links in the answer text"""
    
    def _build_context(self, chunks: List[Dict]) -> str:
        """
        Build context string from retrieved chunks.
        
        Args:
            chunks: List of chunk dictionaries
        
        Returns:
            Formatted context string
        """
        if not chunks:
            return "No relevant information found."
        
        context_parts = []
        
        for i, chunk in enumerate(chunks, 1):
            content = chunk['content']
            metadata = chunk.get('metadata', {})
            
            # Format: [1] content (Source: URL)
            url = metadata.get('url', 'Unknown')
            title = metadata.get('title', '')
            
            source_info = f"Source: {title} ({url})" if title else f"Source: {url}"
            
            context_parts.append(f"[{i}] {content}\n({source_info})")
        
        return "\n\n".join(context_parts)
    
    def _build_prompt(self, question: str, context: str) -> str:
        """
        Build the final prompt for the LLM.
        
        Args:
            question: User's question
            context: Formatted context from chunks
        
        Returns:
            Complete prompt string
        """
        prompt = f"""Based on the following context, please answer the question.

Context:
{context}

Question: {question}

Answer:"""
        
        return prompt
    
    def _extract_sources(self, chunks: List[Dict]) -> List[str]:
        """
        Extract unique source URLs from chunks.
        
        Args:
            chunks: List of chunk dictionaries
        
        Returns:
            List of unique source URLs
        """
        sources = []
        seen_urls = set()
        
        for chunk in chunks:
            url = chunk.get('metadata', {}).get('url')
            if url and url not in seen_urls:
                sources.append(url)
                seen_urls.add(url)
        
        return sources


# Create singleton instance
generator = Generator()