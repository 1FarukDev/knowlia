

from app.rag.embeddings import embedding_service
from app.rag.chunking import chunking_service
from app.rag.vector_store import vector_store

print("🧪 Testing Core RAG Components\n")

# Test 1: Generate an embedding
print("1️⃣ Testing Embeddings...")
text = "What is the pricing for your service?"
embedding = embedding_service.generate_embedding(text)
print(f"✅ Generated embedding with {len(embedding)} dimensions")
print(f"   First 5 values: {embedding[:5]}")

# Test 2: Chunk some text
print("\n2️⃣ Testing Chunking...")
long_text = """
Our company offers three pricing tiers. The Basic plan costs $99 per month 
and includes 10GB storage and email support. The Pro plan is $299 per month 
with 100GB storage, priority support, and advanced analytics. The Enterprise 
plan is custom priced and includes unlimited storage, dedicated support, and 
custom integrations. All plans come with a 14-day free trial.
"""
chunks = chunking_service.chunk_text(
    long_text,
    metadata={"url": "example.com/pricing", "title": "Pricing"}
)
print(f"✅ Split text into {len(chunks)} chunks")
for i, chunk in enumerate(chunks):
    print(f"   Chunk {i}: {chunk['content'][:50]}...")

# Test 3: Store chunks in vector database
print("\n3️⃣ Testing Vector Store...")
# Generate embeddings for each chunk
chunk_texts = [c["content"] for c in chunks]
chunk_embeddings = embedding_service.generate_embeddings_batch(chunk_texts)
chunk_metadatas = [c["metadata"] for c in chunks]

# Add to vector store
vector_store.add_chunks(
    chunks=chunk_texts,
    embeddings=chunk_embeddings,
    metadatas=chunk_metadatas
)
print(f"✅ Vector store now has {vector_store.count()} chunks")

# Test 4: Search for similar chunks
print("\n4️⃣ Testing Similarity Search...")
question = "How much does the Pro plan cost?"
question_embedding = embedding_service.generate_embedding(question)

results = vector_store.search(question_embedding, top_k=2)

print(f"✅ Found {len(results['documents'])} relevant chunks for: '{question}'")
for i, (doc, metadata, distance) in enumerate(zip(
    results['documents'],
    results['metadatas'],
    results['distances']
)):
    print(f"\n   Result {i+1} (similarity: {1 - distance:.3f}):")
    print(f"   {doc[:100]}...")
    print(f"   Source: {metadata.get('url', 'N/A')}")

print("\n✅ All core RAG components working!")