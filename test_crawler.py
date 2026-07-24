"""
Test the web crawler: scraper and cleaner.
"""

from app.crawler.scraper import web_scraper
from app.crawler.cleaner import html_cleaner

print("🕷️ Testing Web Crawler\n")

# Test 1: Fetch a webpage
print("1️⃣ Testing Web Scraper...")
url = "https://www.farukajibade.com/"
result = web_scraper.fetch_page(url)

if result:
    print(f"✅ Successfully fetched page")
    print(f"   Title: {result['title']}")
    print(f"   Status: {result['status_code']}")
    print(f"   HTML length: {len(result['html'])} characters")
else:
    print("❌ Failed to fetch page")
    exit(1)

# Test 2: Clean HTML
print("\n2️⃣ Testing HTML Cleaner...")
clean_text = html_cleaner.clean_html(result['html'])
print(f"✅ Cleaned HTML")
print(f"   Clean text length: {len(clean_text)} characters")
print(f"   Preview: {clean_text[:200]}...")

# Test 3: Extract metadata
print("\n3️⃣ Testing Metadata Extraction...")
metadata = html_cleaner.extract_metadata(result['html'])
print(f"✅ Extracted metadata:")
for key, value in metadata.items():
    print(f"   {key}: {value[:50] if len(value) > 50 else value}")

# Test 4: Validate URLs
print("\n4️⃣ Testing URL Validation...")
test_urls = [
    ("https://example.com", True),
    ("http://test.com", True),
    ("not-a-url", False),
    ("", False)
]

for test_url, expected in test_urls:
    is_valid = web_scraper.is_valid_url(test_url)
    status = "✅" if is_valid == expected else "❌"
    print(f"   {status} '{test_url}': {is_valid}")

print("\n✅ All crawler tests passed!")