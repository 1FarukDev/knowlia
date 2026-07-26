from typing import Dict, List
from app.rag.retriever import retriever
from app.rag.generator import generator
from openai import OpenAI
from app.core.config import settings

class RAGService:
    
    def answer_question_with_history(
        self,
        question: str,
        history: List[Dict] = None
    ) -> Dict:
       
        print(f"\n💬 Answering question with history: {question}")
        
        if not history or len(history) == 0:
            return self.answer_question(question)
        
        contextualized_question = self._reformulate_with_context(question, history)
        retrieved_chunks = retriever.retrieve(contextualized_question)
        
        if not retrieved_chunks:
            return {
                'question': question,
                'answer': "I don't have any information to answer that question.",
                'sources': [],
                'chunks_used': 0,
                'retrieved_chunks': []
            }
        
        print(f"   Retrieved {len(retrieved_chunks)} chunks")
        
        # Generate answer using original question (not reformulated)
        print("2️⃣ Generating answer with LLM...")
        result = generator.generate_answer(question, retrieved_chunks)
        
        print(f"✅ Answer generated using {result['chunks_used']} chunks")
        
        result['question'] = question
        result['retrieved_chunks'] = retrieved_chunks
        
        return result

    def _reformulate_with_context(self, question: str, history: List[Dict]) -> str:
      
        
        # Use only recent history (last 3 turns = 6 messages)
        recent_history = history[-6:]
        
        # Format conversation history
        context_parts = []
        for msg in recent_history:
            role = "User" if msg['role'] == 'user' else "Assistant"
            context_parts.append(f"{role}: {msg['content']}")
        
        context_str = "\n".join(context_parts)
        
        # Create OpenAI client
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Prompt for reformulation
        prompt = f"""Given this conversation history:

{context_str}

The user now asks: "{question}"

Rewrite this question to be completely standalone. Replace pronouns (it, that, they, etc.) with the actual nouns they refer to. The question should make sense without any conversation history.

Only output the reformulated question, nothing else."""

        # Call LLM to reformulate
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=100
        )
        
        reformulated = response.choices[0].message.content.strip()
        
        # Clean up any quotes
        reformulated = reformulated.strip('"').strip("'")
        
        return reformulated
    
    def answer_question(self, question: str) -> Dict:

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
        for i, chunk in enumerate(retrieved_chunks[:3], 1):  
            print(f"   [{i}] Score: {chunk['score']:.3f} | {chunk['content'][:60]}...")
        
        print("2️⃣ Generating answer with LLM...")
        result = generator.generate_answer(question, retrieved_chunks)
        
        print(f"✅ Answer generated using {result['chunks_used']} chunks")
        
        result['question'] = question
        result['retrieved_chunks'] = retrieved_chunks
        
        return result


rag_service = RAGService()