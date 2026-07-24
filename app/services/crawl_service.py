"""
Crawl Service - Orchestrates the entire crawling pipeline.

Flow: URL → Scrape → Clean → Chunk → Embed → Store
"""

from typing import Dict, List
from app.crawler.scraper import web_scraper
from app.crawler.cleaner import html_cleaner
from app.rag.chunking import chunking_service
from app.rag.embeddings import embedding_service
from app.rag.vector_store import vector_store


class CrawlService:
    """
    Service that orchestrates the full crawl-to-storage pipeline.
    
    This is the main entry point for adding new content to the knowledge base.
    """
    
    def crawl_and_index_url(self, url: str) -> Dict:
        """
        Crawl a URL and index it in the vector store.
        
        Complete pipeline:
        1. Fetch webpage (scraper)
        2. Clean HTML (cleaner)
        3. Split into chunks (chunking)
        4. Generate embeddings (embeddings)
        5. Store in vector DB (vector_store)
        
        Args:
            url: The webpage URL to crawl
        
        Returns:
            Dictionary with:
            - success: Boolean
            - url: The crawled URL
            - chunks_created: Number of chunks stored
            - message: Status message
        
        Example:
            >>> service = CrawlService()
            >>> result = service.crawl_and_index_url("https://example.com")
            >>> print(result['chunks_created'])
            15
        """
        print(f"\n🚀 Starting crawl pipeline for: {url}")
        
        # Step 1: Fetch the webpage
        print("1️⃣ Fetching webpage...")
        page_data = web_scraper.fetch_page(url)
        
        if not page_data:
            return {
                'success': False,
                'url': url,
                'chunks_created': 0,
                'message': "Failed to fetch webpage"
            }
        
        # Step 2: Clean HTML
        print("2️⃣ Cleaning HTML...")
        clean_text = html_cleaner.clean_html(page_data['html'])
        
        if not clean_text or len(clean_text) < 100:
            return {
                'success': False,
                'url': url,
                'chunks_created': 0,
                'message': "Insufficient content after cleaning"
            }
        
        print(f"   Extracted {len(clean_text)} characters of clean text")
        
        # Step 3: Chunk the text
        print("3️⃣ Chunking text...")
        metadata = {
            'url': page_data['url'],
            'title': page_data.get('title', 'Untitled')
        }
        
        chunks = chunking_service.chunk_text(clean_text, metadata)
        print(f"   Created {len(chunks)} chunks")
        
        # Step 4: Generate embeddings
        print("4️⃣ Generating embeddings...")
        chunk_texts = [chunk['content'] for chunk in chunks]
        embeddings = embedding_service.generate_embeddings_batch(chunk_texts)
        print(f"   Generated {len(embeddings)} embeddings")
        
        # Step 5: Store in vector database
        print("5️⃣ Storing in vector database...")
        chunk_metadatas = [chunk['metadata'] for chunk in chunks]
        
        vector_store.add_chunks(
            chunks=chunk_texts,
            embeddings=embeddings,
            metadatas=chunk_metadatas
        )
        
        print(f"✅ Pipeline complete! Indexed {len(chunks)} chunks from {url}")
        
        return {
            'success': True,
            'url': page_data['url'],
            'title': page_data.get('title'),
            'chunks_created': len(chunks),
            'message': f"Successfully indexed {len(chunks)} chunks"
        }
    
    def crawl_and_index_multiple_urls(
        self,
        urls: List[str],
        delay: float = 2.0
    ) -> Dict:
        """
        Crawl and index multiple URLs.
        
        Args:
            urls: List of URLs to crawl
            delay: Delay between requests (seconds)
        
        Returns:
            Dictionary with summary statistics
        
        Example:
            >>> service = CrawlService()
            >>> urls = ["https://example.com/page1", "https://example.com/page2"]
            >>> result = service.crawl_and_index_multiple_urls(urls)
            >>> print(result['total_chunks'])
            32
        """
        results = []
        total_chunks = 0
        successful = 0
        failed = 0
        
        for url in urls:
            result = self.crawl_and_index_url(url)
            results.append(result)
            
            if result['success']:
                successful += 1
                total_chunks += result['chunks_created']
            else:
                failed += 1
            
            # Add delay between URLs (except last one)
            if url != urls[-1]:
                import time
                time.sleep(delay)
        
        return {
            'total_urls': len(urls),
            'successful': successful,
            'failed': failed,
            'total_chunks': total_chunks,
            'results': results
        }


# Create singleton instance
crawl_service = CrawlService()