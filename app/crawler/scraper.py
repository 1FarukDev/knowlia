

import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
from urllib.parse import urljoin, urlparse
import time


class WebScraper:
  
    
    def __init__(self, timeout: int = 10):
        """
        Initialize scraper.
        
        Args:
            timeout: Maximum seconds to wait for response (default 10)
        """
        self.timeout = timeout
        
        # Set user agent (identifies our bot)
        # Some websites block requests without a user agent
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; KnowliaBot/1.0; +https://knowlia.com)'
        }
    
    def fetch_page(self, url: str) -> Optional[Dict]:
        """
        Fetch a webpage and extract basic information.
        
        Args:
            url: The webpage URL to fetch
        
        Returns:
            Dictionary with:
            - url: The final URL (after redirects)
            - title: Page title
            - html: Raw HTML content
            - status_code: HTTP status code
            
            Returns None if fetch fails
        
        Example:
            >>> scraper = WebScraper()
            >>> result = scraper.fetch_page("https://example.com")
            >>> print(result['title'])
            "Example Domain"
        """
        try:
            print(f"🌐 Fetching: {url}")
            
            # Make HTTP GET request
            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.timeout,
                allow_redirects=True  # Follow redirects
            )
            
            # Raise exception for bad status codes (4xx, 5xx)
            response.raise_for_status()
            
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract page title
            title = None
            if soup.title:
                title = soup.title.string.strip()
            
            # If no title tag, try to find h1
            if not title and soup.h1:
                title = soup.h1.get_text().strip()
            
            # Get final URL (after redirects)
            final_url = response.url
            
            result = {
                'url': final_url,
                'title': title,
                'html': response.text,
                'status_code': response.status_code
            }
            
            print(f"✅ Fetched: {title or final_url} ({response.status_code})")
            return result
            
        except requests.exceptions.Timeout:
            print(f"⏱️ Timeout: {url}")
            return None
            
        except requests.exceptions.HTTPError as e:
            print(f"❌ HTTP Error {e.response.status_code}: {url}")
            return None
            
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection Error: {url}")
            return None
            
        except Exception as e:
            print(f"❌ Error fetching {url}: {str(e)}")
            return None
    
    def fetch_multiple_pages(
        self,
        urls: list,
        delay: float = 1.0
    ) -> list:
        """
        Fetch multiple pages with a delay between requests.
        
        Args:
            urls: List of URLs to fetch
            delay: Seconds to wait between requests (be polite!)
        
        Returns:
            List of result dictionaries (None for failed fetches)
        
        Why delay?
        - Prevents overwhelming the server
        - Reduces chance of getting blocked
        - Good web scraping etiquette
        
        Example:
            >>> scraper = WebScraper()
            >>> urls = ["https://example.com/page1", "https://example.com/page2"]
            >>> results = scraper.fetch_multiple_pages(urls, delay=2.0)
        """
        results = []
        
        for i, url in enumerate(urls):
            result = self.fetch_page(url)
            results.append(result)
            
            # Add delay between requests (except after last one)
            if i < len(urls) - 1 and delay > 0:
                print(f"⏳ Waiting {delay}s before next request...")
                time.sleep(delay)
        
        return results
    
    def is_valid_url(self, url: str) -> bool:
        """
        Check if URL is valid and accessible.
        
        Args:
            url: URL to validate
        
        Returns:
            True if URL is valid, False otherwise
        
        Example:
            >>> scraper = WebScraper()
            >>> scraper.is_valid_url("https://example.com")
            True
            >>> scraper.is_valid_url("not-a-url")
            False
        """
        try:
            parsed = urlparse(url)
            # URL must have scheme (http/https) and netloc (domain)
            return bool(parsed.scheme) and bool(parsed.netloc)
        except Exception:
            return False


# Create singleton instance
web_scraper = WebScraper()