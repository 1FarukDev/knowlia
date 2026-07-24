"""
Cleaner module - Cleans HTML and extracts readable text.

This module removes:
- Navigation menus
- Ads and scripts
- Footers and sidebars
- Style and formatting tags

Keeping only the main content.
"""

from bs4 import BeautifulSoup, Comment
from typing import Optional
import re


class HTMLCleaner:
    """
    HTML cleaner for extracting readable text from webpages.
    
    Removes noise (nav, ads, scripts) and keeps main content.
    """
    
    # Tags to completely remove (including their content)
    UNWANTED_TAGS = [
        'script', 'style', 'noscript',  # Code/styles
        'nav', 'header', 'footer',       # Navigation
        'aside', 'form',                 # Sidebars, forms
        'iframe', 'object', 'embed',     # Embedded content
        'button', 'input', 'select'      # Interactive elements
    ]
    
    # Class/ID keywords that indicate noise (not main content)
    NOISE_PATTERNS = [
        'nav', 'menu', 'sidebar', 'footer', 'header',
        'advertisement', 'ad-', 'ads', 'promo',
        'social', 'share', 'comment', 'cookie',
        'popup', 'modal', 'banner'
    ]
    
    def clean_html(self, html: str) -> str:
        """
        Clean HTML and extract readable text.
        
        Args:
            html: Raw HTML string
        
        Returns:
            Clean text content (main content only)
        
        Process:
        1. Parse HTML with BeautifulSoup
        2. Remove unwanted tags (scripts, nav, etc.)
        3. Remove elements with noise patterns
        4. Extract text
        5. Clean whitespace
        
        Example:
            >>> cleaner = HTMLCleaner()
            >>> html = "<html><body><nav>Menu</nav><p>Content</p></body></html>"
            >>> cleaner.clean_html(html)
            "Content"
        """
        if not html:
            return ""
        
        # Parse HTML
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove unwanted tags
        for tag_name in self.UNWANTED_TAGS:
            for tag in soup.find_all(tag_name):
                tag.decompose()  # Remove from tree
        
        # Remove HTML comments
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()
        
        # Remove elements with noise patterns in class/id
        for element in soup.find_all(class_=True):
            if self._is_noise_element(element):
                element.decompose()
        
        for element in soup.find_all(id=True):
            if self._is_noise_element(element):
                element.decompose()
        
        # Extract text
        text = soup.get_text(separator=' ', strip=True)
        
        # Clean whitespace
        text = self._clean_whitespace(text)
        
        return text
    
    def _is_noise_element(self, element) -> bool:
        """
        Check if element is likely noise (ads, nav, etc.).
        
        Args:
            element: BeautifulSoup element
        
        Returns:
            True if element matches noise patterns
        """
        # Get class and id attributes
        classes = element.get('class', [])
        element_id = element.get('id', '')
        
        # Convert to lowercase strings
        class_str = ' '.join(classes).lower() if classes else ''
        id_str = element_id.lower() if element_id else ''
        
        # Check if any noise pattern matches
        combined = class_str + ' ' + id_str
        
        for pattern in self.NOISE_PATTERNS:
            if pattern in combined:
                return True
        
        return False
    
    def _clean_whitespace(self, text: str) -> str:
        """
        Clean excessive whitespace from text.
        
        Args:
            text: Text with messy whitespace
        
        Returns:
            Text with normalized whitespace
        
        Example:
            >>> cleaner = HTMLCleaner()
            >>> cleaner._clean_whitespace("Hello    world\\n\\n\\nTest")
            "Hello world\\nTest"
        """
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)
        
        # Replace multiple newlines with max 2
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def extract_metadata(self, html: str) -> dict:
        """
        Extract metadata from HTML (title, description, etc.).
        
        Args:
            html: Raw HTML string
        
        Returns:
            Dictionary with metadata
        
        Example:
            >>> cleaner = HTMLCleaner()
            >>> html = "<html><head><title>Example</title></head></html>"
            >>> metadata = cleaner.extract_metadata(html)
            >>> metadata['title']
            "Example"
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        metadata = {}
        
        # Title
        if soup.title:
            metadata['title'] = soup.title.string.strip()
        
        # Meta description
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        if desc_tag and desc_tag.get('content'):
            metadata['description'] = desc_tag['content'].strip()
        
        # Meta keywords
        keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
        if keywords_tag and keywords_tag.get('content'):
            metadata['keywords'] = keywords_tag['content'].strip()
        
        # Open Graph title (for social media)
        og_title = soup.find('meta', attrs={'property': 'og:title'})
        if og_title and og_title.get('content'):
            metadata['og_title'] = og_title['content'].strip()
        
        return metadata


# Create singleton instance
html_cleaner = HTMLCleaner()