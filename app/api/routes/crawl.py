from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from app.services.crawl_service import crawl_service
from typing import List, Optional


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

class SiteCrawlRequest(BaseModel):
    url: HttpUrl
    max_pages: Optional[int] = 50
    same_domain_only: Optional[bool] = True
    delay: Optional[float] = 2.0
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://example.com",
                "max_pages": 50,
                "same_domain_only": True,
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

    try:
        url_str = str(request.url)
        
        result = crawl_service.crawl_and_index_url(url_str)
        
        return CrawlResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to crawl URL: {str(e)}"
        )


@router.post("/multiple")
async def crawl_multiple_urls(request: CrawlMultipleRequest):
  
    try:
        url_strs = [str(url) for url in request.urls]
        
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
    
    from app.rag.vector_store import vector_store
    
    total_chunks = vector_store.count()
    
    return {
        "total_chunks": total_chunks,
        "message": f"Vector store contains {total_chunks} chunks"
    }
    
@router.post("/site")
async def crawl_entire_site(request: SiteCrawlRequest):

    try:
        url_str = str(request.url)
        
        result = crawl_service.crawl_entire_site(
            start_url=url_str,
            max_pages=request.max_pages,
            same_domain_only=request.same_domain_only,
            delay=request.delay
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to crawl site: {str(e)}"
        )