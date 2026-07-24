"""
Test the complete RAG pipeline: crawl → index → query → answer.
"""

from app.services.crawl_service import crawl_service
from app.services.rag_service import rag_service
from app.rag.vector_store import vector_store

print("🧪 Testing Complete RAG Pipeline\n")

# Test 1: Crawl and index a webpage
print("=" * 60)
print("1️⃣ Crawling and Indexing Webpage")
print("=" * 60)

url = "https://www.farukajibade.com/"
crawl_result = crawl_service.crawl_and_index_url(url)

if crawl_result['success']:
    print(f"\n✅ Successfully crawled and indexed!")
    print(f"   URL: {crawl_result['url']}")
    print(f"   Title: {crawl_result.get('title', 'N/A')}")
    print(f"   Chunks created: {crawl_result['chunks_created']}")
else:
    print(f"\n❌ Failed to crawl: {crawl_result['message']}")
    exit(1)

# Check vector store
total_chunks = vector_store.count()
print(f"\n📊 Vector store now contains {total_chunks} total chunks")

# Test 2: Ask questions
print("\n" + "=" * 60)
print("2️⃣ Asking Questions")
print("=" * 60)

questions = [
    "What is this website about?",
    "Tell me about the domain",
]

for question in questions:
    print(f"\n❓ Question: {question}")
    print("-" * 60)
    
    result = rag_service.answer_question(question)
    
    print(f"\n💡 Answer:\n{result['answer']}\n")
    print(f"📚 Sources:")
    for i, source in enumerate(result['sources'], 1):
        print(f"   [{i}] {source}")
    
    print(f"\n📊 Stats:")
    print(f"   Chunks used: {result['chunks_used']}")
    print(f"   Model: {result.get('model', 'N/A')}")

print("\n" + "=" * 60)
print("✅ Complete RAG Pipeline Test Passed!")
print("=" * 60)