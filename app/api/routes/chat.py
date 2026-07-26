from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.services.rag_service import rag_service


router = APIRouter(prefix="/chat", tags=["Chat"])


class Message(BaseModel):
    role: str 
    content: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "role": "user",
                "content": "What is the pricing?"
            }
        }
class ChatRequest(BaseModel):
    question: str
    conversation_history: Optional[List[Message]] = []
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What features does it include?",
                "conversation_history": [
                    {
                        "role": "user",
                        "content": "What is the pricing?"
                    },
                    {
                        "role": "assistant",
                        "content": "Our basic plan is $99/month"
                    }
                ]
            }
        }


class ChatResponse(BaseModel):  
    question: str
    answer: str
    sources: List[str]
    chunks_used: int
    model: Optional[str] = None


@router.post("/", response_model=ChatResponse)
async def ask_question(request: ChatRequest):
    try:
       
        if not request.question or len(request.question.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Question cannot be empty"
            )
        history = [
            {"role": msg.role, "content": msg.content} for msg in request.conversation_history
        ]
        result = rag_service.answer_question_with_history(request.question, history)
        
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
    try:
        if not request.question or len(request.question.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Question cannot be empty"
            )
        
        result = rag_service.answer_question(request.question)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate answer: {str(e)}"
        )