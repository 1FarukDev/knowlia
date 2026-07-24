from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from app.services.crawl_service import crawl_service


router = APIRouter(prefix="/crawl", tags=["Crawl"])


class CrawlRequest(BaseModel):
    """Request model for crawling a single URL"""
    url: HttpUrl  # Validates URL format
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://example.com"
            }
        }


class CrawlMultipleRequest(BaseModel):
    """Request model for crawling multiple URLs"""
    urls: List[HttpUrl]
    delay: Optional[float] = 2.0  # Delay between requests
    
    class Config:
        json_schema_extra = {
            "example": {
                "urls": [
                    "https://example.com/page1",
                    "https://example.com/page2"
                ],
                "delay": 2.0
            }
        }


class CrawlResponse(BaseModel):
    success: bool
    url: str
    title: Optional[str] = None
    chunks_created: int
    message: str


@router.post("/", response_model=CrawlResponse)
async def crawl_url(request: CrawlRequest):
    """
    Crawl and index a single URL.
    
    This endpoint:
    1. Fetches the webpage
    2. Extracts clean text
    3. Chunks the content
    4. Generates embeddings
    5. Stores in vector database
    
    Example:
        POST /crawl
        {
            "url": "https://example.com"
        }
    
    Returns:
        {
            "success": true,
            "url": "https://example.com",
            "title": "Example Domain",
            "chunks_created": 15,
            "message": "Successfully indexed 15 chunks"
        }
    """
    try:
        # Convert HttpUrl to string
        url_str = str(request.url)
        
        # Run crawl pipeline
        result = crawl_service.crawl_and_index_url(url_str)
        
        return CrawlResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to crawl URL: {str(e)}"
        )


@router.post("/multiple")
async def crawl_multiple_urls(request: CrawlMultipleRequest):
    """
    Crawl and index multiple URLs.
    
    Example:
        POST /crawl/multiple
        {
            "urls": [
                "https://example.com/page1",
                "https://example.com/page2"
            ],
            "delay": 2.0
        }
    
    Returns:
        {
            "total_urls": 2,
            "successful": 2,
            "failed": 0,
            "total_chunks": 32,
            "results": [...]
        }
    """
    try:
        # Convert HttpUrl objects to strings
        url_strs = [str(url) for url in request.urls]
        
        # Run batch crawl
        result = crawl_service.crawl_and_index_multiple_urls(
            url_strs,
            delay=request.delay
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to crawl URLs: {str(e)}"
        )


@router.get("/stats")
async def get_crawl_stats():
    """
    Get statistics about the crawled content.
    
    Returns:
        {
            "total_chunks": 150,
            "message": "Vector store contains 150 chunks"
        }
    """
    from app.rag.vector_store import vector_store
    
    total_chunks = vector_store.count()
    
    return {
        "total_chunks": total_chunks,
        "message": f"Vector store contains {total_chunks} chunks"
    }