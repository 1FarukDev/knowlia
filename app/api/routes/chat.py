from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.services.rag_service import rag_service


router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    """Request model for asking questions"""
    question: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is your pricing?"
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat answers"""
    question: str
    answer: str
    sources: List[str]
    chunks_used: int
    model: Optional[str] = None


@router.post("/", response_model=ChatResponse)
async def ask_question(request: ChatRequest):
    """
    Ask a question and get an answer using RAG.
    
    This endpoint:
    1. Converts question to embedding
    2. Searches for relevant chunks
    3. Generates answer using LLM with context
    4. Returns answer with sources
    
    Example:
        POST /chat
        {
            "question": "What is your pricing?"
        }
    
    Returns:
        {
            "question": "What is your pricing?",
            "answer": "Our pricing starts at $99 per month...",
            "sources": ["https://example.com/pricing"],
            "chunks_used": 3,
            "model": "gpt-4o-mini"
        }
    """
    try:
        # Validate question
        if not request.question or len(request.question.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Question cannot be empty"
            )
        
        # Run RAG pipeline
        result = rag_service.answer_question(request.question)
        
        # Return response (excluding retrieved_chunks for API)
        return ChatResponse(
            question=result['question'],
            answer=result['answer'],
            sources=result['sources'],
            chunks_used=result['chunks_used'],
            model=result.get('model')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate answer: {str(e)}"
        )


@router.post("/debug", response_model=dict)
async def ask_question_debug(request: ChatRequest):
    """
    Debug version of chat endpoint - returns full details.
    
    Includes retrieved chunks with scores for debugging.
    
    Example:
        POST /chat/debug
        {
            "question": "What is your pricing?"
        }
    
    Returns full result including retrieved_chunks array.
    """
    try:
        if not request.question or len(request.question.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Question cannot be empty"
            )
        
        # Run RAG pipeline
        result = rag_service.answer_question(request.question)
        
        # Return complete result with chunks
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate answer: {str(e)}"
        )