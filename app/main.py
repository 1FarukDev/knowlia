
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import crawl, chat
from app.core.config import settings
from app.rag.vector_store import vector_store
import uvicorn


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered knowledge assistant with RAG",
    version="1.0.0",
    debug=settings.DEBUG
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(crawl.router)
app.include_router(chat.router)


@app.get("/")
async def root():
    return {
        "message": f"{settings.APP_NAME} API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "crawl": "/crawl",
            "chat": "/chat",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Startup event
@app.on_event("startup")
async def startup_event():
    print(f"🚀 {settings.APP_NAME} API starting...")
    print(f"📊 Debug mode: {settings.DEBUG}")
    print(f"🤖 LLM Model: {settings.LLM_MODEL}")
    print(f"📦 Embedding Model: {settings.EMBEDDING_MODEL}")
    
   
    chunk_count = vector_store.count()
    print(f"💾 Vector store: {chunk_count} chunks")
    
    print("✅ API ready!")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    print("👋 Shutting down...")


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.DEBUG
    )