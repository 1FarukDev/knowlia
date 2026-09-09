from playwright.sync_api import sync_playwright
from typing import Optional, Dict
import time


class PlaywrightScraper:
    """
    Browser-based scraper for JavaScript-heavy websites.
    
    Uses Playwright to render JS content that requests can't handle.
    Slower than requests but handles Next.js, React, Vue, etc.
    """
    
    def __init__(self, headless: bool = True):
        """
        Initialize Playwright scraper.
        
        Args:
            headless: Run browser in headless mode (no UI)
        """
        self.headless = headless
    
    def fetch_page(self, url: str, wait_for_selector: Optional[str] = None) -> Optional[Dict]:
        """
        Fetch a webpage using Playwright.
        
        Args:
            url: URL to fetch
            wait_for_selector: CSS selector to wait for before capturing
                              (e.g., 'main', '#content', '.pricing-table')
        
        Returns:
            Dictionary with:
            - url: Final URL (after redirects)
            - html: Full rendered HTML
            - title: Page title
        """
        try:
            with sync_playwright() as p:
                # Launch browser
                browser = p.chromium.launch(headless=self.headless)
                page = browser.new_page()
                
                # Set user agent (avoid bot detection)
                page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                
                # Navigate to page
                print(f"   🌐 Loading page with browser...")
                page.goto(url, wait_until='networkidle', timeout=30000)
                
                # Wait for specific selector if provided
                if wait_for_selector:
                    page.wait_for_selector(wait_for_selector, timeout=10000)
                else:
                    # Default: wait a bit for JS to execute
                    time.sleep(2)
                
                # Get page data
                html = page.content()
                title = page.title()
                final_url = page.url
                
                browser.close()
                
                print(f"   ✅ Page rendered: {len(html)} chars")
                
                return {
                    'url': final_url,
                    'html': html,
                    'title': title
                }
                
        except Exception as e:
            print(f"   ❌ Playwright fetch failed: {str(e)}")
            return None


# Singleton instance
playwright_scraper = PlaywrightScraper()