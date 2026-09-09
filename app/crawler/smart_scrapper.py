from app.crawler.scraper import web_scraper
from app.crawler.playwright_scraper import playwright_scraper
from typing import Optional, Dict


class SmartScraper:
    """
    Intelligent scraper that automatically detects JS-heavy sites.
    
    Strategy:
    1. Try fast scraper (requests) first
    2. Analyze if content is JS-rendered
    3. Auto-fallback to Playwright if needed
    """
    
    def fetch_page(self, url: str, force_playwright: bool = False) -> Optional[Dict]:
        """
        Fetch page with automatic JS detection.
        
        Args:
            url: URL to fetch
            force_playwright: Skip detection, use Playwright directly
        
        Returns:
            Page data dictionary or None
        """
        if force_playwright:
            print(f"   🎭 Using Playwright (forced)")
            return playwright_scraper.fetch_page(url)
        
        # Try fast scraper first
        print(f"   ⚡ Trying fast scraper...")
        result = web_scraper.fetch_page(url)
        
        if not result:
            return None
        
        # Check if content is JS-rendered
        if self._is_js_rendered(result['html']):
            print(f"   🔄 Detected JS-heavy site, switching to Playwright...")
            return playwright_scraper.fetch_page(url)
        
        print(f"   ✅ Fast scraper worked!")
        return result
    
    def _is_js_rendered(self, html: str) -> bool:
        """
        Detect if page is JavaScript-rendered.
        
        Args:
            html: Raw HTML string
        
        Returns:
            True if page appears to be JS-rendered
        """
        html_lower = html.lower()
        
        # Check 1: Common JS framework shells
        js_framework_indicators = [
            '<div id="__next"',      # Next.js
            '<div id="root"',         # React
            '<div id="app"',          # Vue
            '<div id="___gatsby"',    # Gatsby
        ]
        
        for indicator in js_framework_indicators:
            if indicator in html_lower:
                # Check if it's mostly empty (just the shell)
                if len(html) < 5000:  # Very small HTML = probably just shell
                    return True
        
        # Check 2: Very little actual content
        if len(html) < 1000:
            return True
        
        # Check 3: Ratio of text content to HTML
        text_indicators = ['<p', '<article', '<main', '<section', '<h1', '<h2', '<h3']
        content_tags = sum(html_lower.count(tag) for tag in text_indicators)
        
        # If very few content tags, likely JS-rendered
        if content_tags < 3:
            return True
        
        # Check 4: High script-to-content ratio
        script_count = html_lower.count('<script')
        if script_count > 10 and content_tags < 5:
            return True
        
        # Looks like static content
        return False


# Singleton instance
smart_scraper = SmartScraper()