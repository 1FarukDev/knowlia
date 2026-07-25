
from typing import List


class URLFilter:
  
    DEFAULT_SKIP_PATTERNS = [
        
        '/login', '/signin', '/sign-in', '/signup', '/sign-up',
        '/register', '/logout', '/signout', '/sign-out',
        '/auth', '/authentication', '/password', '/reset',
        
        '/account', '/profile', '/dashboard', '/settings',
        '/my-account', '/user', '/member', '/preferences',
        
        '/admin', '/wp-admin', '/administrator',
        '/backend', '/cms', '/manage',
        
        '/cart', '/checkout', '/payment', '/order',
        '/basket', '/wishlist', '/purchase', '/buy',
        
        '/submit', '/post', '/upload', '/delete',
        '/edit', '/update', '/create', '/remove',
        
        '/api/', '/graphql', '/json', '/xml',
        '/rest/', '/v1/', '/v2/', '/v3/',
        
        '.pdf', '.jpg', '.jpeg', '.png', '.gif', '.svg',
        '.css', '.js', '.ico', '.woff', '.ttf', '.otf',
        '.zip', '.tar', '.gz', '.rar',
        '.mp4', '.mp3', '.avi', '.mov', '.wav',
        '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        
        '/share', '/print', '/email', '/subscribe',
        '/feed', '/rss', '/newsletter',
        
        '/search', '/404', '/error', '/not-found',
        '/privacy', '/terms', '/cookie', '/gdpr',
        '/sitemap', '/robots.txt', '/ads.txt',
        '/contact-form', '/apply', '/careers-form',
    ]
    
    DYNAMIC_PARAMS = [
        'session', 'token', 'redirect', 'return',
        'utm_', 'ref', 'source', 'campaign',
        'fbclid', 'gclid', 'msclkid'
    ]
    
    def __init__(self, custom_patterns: List[str] = None):
       
        self.skip_patterns = self.DEFAULT_SKIP_PATTERNS.copy()
        
        if custom_patterns:
            self.skip_patterns.extend(custom_patterns)
    
    def should_skip(self, url: str) -> bool:
       
        url_lower = url.lower()
        
        for pattern in self.skip_patterns:
            if pattern in url_lower:
                return True
        

        if '?' in url:
            for param in self.DYNAMIC_PARAMS:
                if param in url_lower:
                    return True
        
        return False
    
    def filter_urls(self, urls: List[str]) -> List[str]:
       
        return [url for url in urls if not self.should_skip(url)]
    
    def add_patterns(self, patterns: List[str]):
       
        self.skip_patterns.extend(patterns)
    
    def get_skip_reason(self, url: str) -> str:
       
        url_lower = url.lower()
        
        for pattern in self.skip_patterns:
            if pattern in url_lower:
                return f"Contains pattern: {pattern}"
        
        if '?' in url:
            for param in self.DYNAMIC_PARAMS:
                if param in url_lower:
                    return f"Contains dynamic param: {param}"
        
        return ""



url_filter = URLFilter()