from openai import OpenAI
from typing import List, Dict
from app.core.config import settings
from app.rag.prompts import RAGPrompts  # NEW IMPORT


class Generator:

    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.LLM_MODEL
        self.temperature = settings.TEMPERATURE
        self.max_tokens = settings.MAX_TOKENS
        self.prompts = RAGPrompts()  
    
    def generate_answer(self, question: str, context_chunks: List[Dict]) -> Dict:
        context = self._build_context(context_chunks)
        
        system_prompt = self.prompts.get_system_prompt()
        user_prompt = self.prompts.get_user_prompt(context, question)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        answer = response.choices[0].message.content.strip()
        sources = self._extract_sources(context_chunks)
        
        return {
            'answer': answer,
            'sources': sources,
            'chunks_used': len(context_chunks),
            'model': self.model
        }
    
    def _build_context(self, chunks: List[Dict]) -> str:
        if not chunks:
            return "No relevant information found."
        
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            content = chunk['content']
            metadata = chunk.get('metadata', {})
            url = metadata.get('url', 'Unknown')
            title = metadata.get('title', '')
            
            source_info = f"Source: {title} ({url})" if title else f"Source: {url}"
            context_parts.append(f"[{i}] {content}\n({source_info})")
        
        return "\n\n".join(context_parts)
    
    def _extract_sources(self, chunks: List[Dict]) -> List[str]:
        sources = []
        seen_urls = set()
        
        for chunk in chunks:
            url = chunk.get('metadata', {}).get('url')
            if url and url not in seen_urls:
                sources.append(url)
                seen_urls.add(url)
        
        return sources


generator = Generator()