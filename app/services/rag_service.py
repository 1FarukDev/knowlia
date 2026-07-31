from typing import Dict, List
from app.rag.retriever import retriever
from app.rag.generator import generator
from openai import OpenAI
from app.core.config import settings
from app.rag.prompts import RAGPrompts
from app.rag.reranker import reranker


class RAGService:
    """
    Service that orchestrates the RAG (Retrieval-Augmented Generation) pipeline.
    
    This is the main entry point for answering user questions.
    """
    
    def _rerank_if_enabled(self, query: str, chunks: List[Dict], top_k: int = 5) -> List[Dict]:
        """
        Rerank chunks if reranking is enabled, otherwise return top chunks.
        
        Args:
            query: The query to use for reranking
            chunks: Retrieved chunks from vector search
            top_k: Number of top chunks to return
        
        Returns:
            Reranked chunks or top-k chunks if reranking disabled
        """
        if reranker.enabled:
            print("🔄 Reranking chunks...")
            reranked_chunks = reranker.rerank(
                query=query,
                chunks=chunks,
                top_k=top_k
            )
            print(f"   Top chunk score: {reranked_chunks[0].get('rerank_score', 0):.3f}")
            return reranked_chunks
        else:
            return chunks[:top_k]
    
    def answer_question_with_history(
        self,
        question: str,
        history: List[Dict] = None
    ) -> Dict:
        """
        Answer a question with conversation history for context.
        
        Args:
            question: User's current question
            history: List of previous conversation messages
        
        Returns:
            Dictionary with answer, sources, and metadata
        """
        print(f"\n💬 Answering question with history: {question}")
        
        # If no history, use standard question answering
        if not history or len(history) == 0:
            return self.answer_question(question)
        
        # Reformulate question with conversation context
        contextualized_question = self._reformulate_with_context(question, history)
        
        # Retrieve relevant chunks using contextualized question
        print("1️⃣ Retrieving relevant chunks...")
        retrieved_chunks = retriever.retrieve(contextualized_question, top_k=10)
        
        if not retrieved_chunks:
            return {
                'question': question,
                'answer': "I don't have any information to answer that question.",
                'sources': [],
                'chunks_used': 0,
                'retrieved_chunks': []
            }
        
        print(f"   Retrieved {len(retrieved_chunks)} chunks")
        
        # Step 2: Rerank chunks for better relevance
        reranked_chunks = self._rerank_if_enabled(
            query=contextualized_question,
            chunks=retrieved_chunks,
            top_k=5
        )
        
        # Step 3: Generate answer using original question (not reformulated)
        print("2️⃣ Generating answer with LLM...")
        result = generator.generate_answer(question, reranked_chunks)
        
        print(f"✅ Answer generated using {result['chunks_used']} chunks")
        
        result['question'] = question
        result['retrieved_chunks'] = retrieved_chunks
        
        return result

    def _reformulate_with_context(self, question: str, history: List[Dict]) -> str:
        """
        Reformulate question with conversation context using hardened prompt.
        
        Args:
            question: Current user question
            history: Previous conversation messages
        
        Returns:
            Reformulated standalone question
        """
        # Use only recent history (last 3 turns = 6 messages)
        recent_history = history[-6:]
        
        # Format conversation history
        context_parts = []
        for msg in recent_history:
            role = "User" if msg['role'] == 'user' else "Assistant"
            context_parts.append(f"{role}: {msg['content']}")
        
        context_str = "\n".join(context_parts)
        
        # Get hardened reformulation prompt from prompts.py
        reformulation_prompt = RAGPrompts.get_reformulation_prompt(context_str, question)
        
        # Call OpenAI to reformulate
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": reformulation_prompt}],
            temperature=0.0,
            max_tokens=100
        )
        
        reformulated = response.choices[0].message.content.strip()
        reformulated = reformulated.strip('"').strip("'")
        
        print(f"   📝 Reformulated: {reformulated}")
        
        return reformulated
    
    def answer_question(self, question: str) -> Dict:
        """
        Answer a question using the RAG pipeline.
        
        Complete pipeline:
        1. Retrieve relevant chunks (retriever)
        2. Generate answer using LLM (generator)
        
        Args:
            question: User's question
        
        Returns:
            Dictionary with:
            - question: The original question
            - answer: Generated answer
            - sources: Source URLs used
            - chunks_used: Number of chunks provided as context
            - retrieved_chunks: The actual chunks (for debugging)
        
        Example:
            >>> service = RAGService()
            >>> result = service.answer_question("What is your pricing?")
            >>> print(result['answer'])
            "Our pricing starts at $99 per month for the basic plan..."
        """
        print(f"\n💬 Answering question: {question}")
        
        # Step 1: Retrieve relevant chunks
        print("1️⃣ Retrieving relevant chunks...")
        retrieved_chunks = retriever.retrieve(question, top_k=10)
        
        if not retrieved_chunks:
            return {
                'question': question,
                'answer': "I don't have any information to answer that question. The knowledge base may be empty or doesn't contain relevant content.",
                'sources': [],
                'chunks_used': 0,
                'retrieved_chunks': []
            }
        
        print(f"   Retrieved {len(retrieved_chunks)} chunks")
        for i, chunk in enumerate(retrieved_chunks[:3], 1):  # Show top 3
            print(f"   [{i}] Score: {chunk['score']:.3f} | {chunk['content'][:60]}...")
        
        # Step 2: Rerank chunks for better relevance
        reranked_chunks = self._rerank_if_enabled(
            query=question,
            chunks=retrieved_chunks,
            top_k=5
        )
        
        # Step 3: Generate answer
        print("2️⃣ Generating answer with LLM...")
        result = generator.generate_answer(question, reranked_chunks)
        
        print(f"✅ Answer generated using {result['chunks_used']} chunks")
        
        # Add retrieved chunks to result (for debugging/transparency)
        result['question'] = question
        result['retrieved_chunks'] = retrieved_chunks
        
        return result


# Create singleton instance
rag_service = RAGService()