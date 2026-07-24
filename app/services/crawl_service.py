
from typing import Dict, List
from app.crawler.scraper import web_scraper
from app.crawler.cleaner import html_cleaner
from app.rag.chunking import chunking_service
from app.rag.embeddings import embedding_service
from app.rag.vector_store import vector_store
import time

class CrawlService:
   
    
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
                time.sleep(delay)
        
        return {
            'total_urls': len(urls),
            'successful': successful,
            'failed': failed,
            'total_chunks': total_chunks,
            'results': results
        }
    
    def crawl_entire_site(
        self,
        start_url: str,
        max_pages: int = 50,
        same_domain_only: bool = True,
        delay: float = 2.0
    ) -> Dict:
       
       
        to_visit = [start_url]
        visited = set()
        successful = 0
        failed = 0
        total_chunks = 0
        
        start_domain = web_scraper.get_domain(start_url)
        
        while to_visit and successful < max_pages:
            current_url = to_visit.pop(0)
            if current_url in visited:
                continue
            visited.add(current_url)
            print(f"\n[{successful + 1}/{max_pages}] Crawling: {current_url}")
            if same_domain_only:
                current_domain = web_scraper.get_domain(current_url)
                if current_domain != start_domain:
                    print(f"   ⏭️  Skipping (different domain): {current_domain}")
                    continue   
            result = self.crawl_and_index_url(current_url)
            if result['success']:
                successful += 1
                total_chunks += result['chunks_created']
                
                page_data = web_scraper.fetch_page(current_url)
                if page_data:
                    links = web_scraper.extract_links(page_data['html'], current_url)
                    for link in links:
                        if link not in visited and link not in to_visit:
                            if link.startswith('http'):
                                to_visit.append(link)
                                print(f"   🔗 Found: {link}")
            else:
                failed += 1
                print(f"   ❌ Failed: {result['message']}")
            
            if to_visit and successful < max_pages:
                time.sleep(delay)
        
        return {
            'start_url': start_url,
            'pages_crawled': successful,
            'pages_failed': failed,
            'total_chunks': total_chunks,
            'urls_discovered': len(visited) + len(to_visit),
            'urls_remaining': len(to_visit)
        }


crawl_service = CrawlService()