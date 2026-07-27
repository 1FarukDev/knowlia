

from bs4 import BeautifulSoup, Comment
from typing import Optional
import re


class HTMLCleaner:
    
    UNWANTED_TAGS = [
        'script', 'style', 'noscript',  
        'nav', 'header', 'footer',       
        'aside', 'form',                 
        'iframe', 'object', 'embed',     
        'button', 'input', 'select'      
    ]
    
    NOISE_PATTERNS = [
        'nav', 'menu', 'sidebar', 'footer', 'header',
        'advertisement', 'ad-', 'ads', 'promo',
        'social', 'share', 'comment', 'cookie',
        'popup', 'modal', 'banner'
    ]
    
    def clean_html(self, html: str) -> str:
        if not html:
            return ""
        soup = BeautifulSoup(html, 'html.parser')
        for tag_name in self.UNWANTED_TAGS:
            for tag in soup.find_all(tag_name):
                tag.decompose()  
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()
        
        elements_to_remove = []
        for element in soup.find_all(class_=True):
            if self._is_noise_element(element):
                elements_to_remove.append(element)
        
        for element in soup.find_all(id=True):
            if self._is_noise_element(element):
                elements_to_remove.append(element)
                
        for element in elements_to_remove:
            element.decompose()
        
        text = soup.get_text(separator=' ', strip=True)
        text = self._clean_whitespace(text)
        
        return text
    
    def _is_noise_element(self, element) -> bool:
       
        classes = element.get('class', [])
        element_id = element.get('id', '')
        
        class_str = ' '.join(classes).lower() if classes else ''
        id_str = element_id.lower() if element_id else ''
        
        combined = class_str + ' ' + id_str
        
        for pattern in self.NOISE_PATTERNS:
            if pattern in combined:
                return True
        
        return False
    
    def _clean_whitespace(self, text: str) -> str:
        
        text = re.sub(r' +', ' ', text)
        
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        text = text.strip()
        
        return text
    
    def extract_metadata(self, html: str) -> dict:
       
        soup = BeautifulSoup(html, 'html.parser')
        
        metadata = {}
        
        if soup.title:
            metadata['title'] = soup.title.string.strip()
        
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        if desc_tag and desc_tag.get('content'):
            metadata['description'] = desc_tag['content'].strip()
        
        keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
        if keywords_tag and keywords_tag.get('content'):
            metadata['keywords'] = keywords_tag['content'].strip()
        
        og_title = soup.find('meta', attrs={'property': 'og:title'})
        if og_title and og_title.get('content'):
            metadata['og_title'] = og_title['content'].strip()
        
        return metadata


html_cleaner = HTMLCleaner()