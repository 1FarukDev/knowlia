

import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
from urllib.parse import urljoin, urlparse, urlunparse
import time


class WebScraper:
  
    
    def __init__(self, timeout: int = 10):
      
        self.timeout = timeout
        
        self.headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Cache-Control': 'max-age=0',
}
    
    def fetch_page(self, url: str) -> Optional[Dict]:
        try:
            print(f"🌐 Fetching: {url}")
            
            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.timeout,
                allow_redirects=True
            )
            
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            title = None
            if soup.title:
                title = soup.title.string.strip()
            
            if not title and soup.h1:
                title = soup.h1.get_text().strip()
            
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
        
        results = []
        
        for i, url in enumerate(urls):
            result = self.fetch_page(url)
            results.append(result)
            
            if i < len(urls) - 1 and delay > 0:
                print(f"⏳ Waiting {delay}s before next request...")
                time.sleep(delay)
        
        return results
    
    def is_valid_url(self, url: str) -> bool:
      
        try:
            parsed = urlparse(url)
            return bool(parsed.scheme) and bool(parsed.netloc)
        except Exception:
            return False
    def extract_links(self, html: str, base_url: str) -> list:
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        for link_tag in soup.find_all('a', href=True):
            href = link_tag['href']
            absolute_url = urljoin(base_url, href)
            parsed_url = urlparse(absolute_url)
            clean_url = urlunparse((
                                    parsed_url.scheme,
                                    parsed_url.netloc,
                                    parsed_url.path,
                                    parsed_url.params,
                                    parsed_url.query,
                                    ''
                                    ))
            links.append(clean_url)
        return links
    def get_domain(self, url: str) -> str:
    
        parsed = urlparse(url)
        return parsed.netloc

web_scraper = WebScraper()