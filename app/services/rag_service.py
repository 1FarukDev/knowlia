from typing import Dict
from app.rag.retriever import retriever
from app.rag.generator import generator


class RAGService:
    """
    Service that orchestrates the RAG (Retrieval-Augmented Generation) pipeline.
    
    This is the main entry point for answering user questions.
    """
    
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
        retrieved_chunks = retriever.retrieve(question)
        
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
        
        # Step 2: Generate answer
        print("2️⃣ Generating answer with LLM...")
        result = generator.generate_answer(question, retrieved_chunks)
        
        print(f"✅ Answer generated using {result['chunks_used']} chunks")
        
        # Add retrieved chunks to result (for debugging/transparency)
        result['question'] = question
        result['retrieved_chunks'] = retrieved_chunks
        
        return result


# Create singleton instance
rag_service = RAGService()