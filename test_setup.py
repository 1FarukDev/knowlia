from app.core.config import settings
from app.core.database import init_db

print("🔧 Testing configuration...")
print(f"Database URL: {settings.DATABASE_URL}")
print(f"OpenAI API Key: {settings.OPENAI_API_KEY[:10]}...")  # Only show first 10 chars
print(f"Embedding Model: {settings.EMBEDDING_MODEL}")
print(f"LLM Model: {settings.LLM_MODEL}")
print(f"Chunk size: {settings.CHUNK_SIZE}")

print("\n🗄️ Initializing database...")
init_db()

print("\n✅ Foundation setup complete!")