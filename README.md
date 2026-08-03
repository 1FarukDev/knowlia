# Knowlia - AI Knowledge Assistant

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

*A production-quality RAG (Retrieval Augmented Generation) engine built from scratch*

[Features](#features) • [Architecture](#architecture) • [Installation](#installation) • [Usage](#usage) • [API Docs](#api-documentation)

</div>

---

## 📖 About

Knowlia is an AI-powered knowledge assistant that can crawl websites, understand their content, and answer questions about them using advanced RAG techniques. Built without relying on high-level frameworks like LangChain, this project demonstrates a deep understanding of RAG fundamentals.

### What Makes This Different?

- ✅ **Built from scratch** - Every component implemented to understand RAG deeply
- ✅ **Production-ready** - Clean architecture, error handling, and best practices
- ✅ **Modern stack** - FastAPI, OpenAI, Cohere, ChromaDB, Python 3.9+
- ✅ **Two-stage retrieval** - Vector search + reranking for better accuracy
- ✅ **Conversation memory** - Handles follow-up questions with context
- ✅ **Security-first** - Prompt injection hardening and sanitization

---

## 🚀 Features

### Core Functionality
- 🌐 **Website Crawling** - Automatically discover and index entire websites
- 🧹 **Intelligent Cleaning** - Extract meaningful content, remove navigation/scripts
- ✂️ **Smart Chunking** - Break content into optimal chunks with overlap
- 🔢 **Embeddings** - Generate semantic vectors using OpenAI's latest models
- 💾 **Vector Storage** - Efficient similarity search with ChromaDB
- 🎯 **Reranking** - Two-stage retrieval for better relevance (Cohere)
- 🤖 **LLM Generation** - GPT-4o-mini powered answers with source citations
- 💬 **Conversation Memory** - Context-aware follow-up questions

### Technical Features
- ⚡ **Async API** - Built on FastAPI for high performance
- 🛡️ **Prompt Hardening** - Protection against injection attacks
- 🔄 **Question Reformulation** - Uses conversation history for better retrieval
- 🎯 **URL Filtering** - Smart filtering of auth pages, assets, and duplicates
- 📊 **Response Metadata** - Includes sources, chunk count, and model info

---

## 🏗️ Architecture

```
┌─────────────┐
│   Website   │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Web Crawler    │  ← Fetch HTML, extract links
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  HTML Cleaner   │  ← Remove noise, extract text
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Text Chunker   │  ← Split into optimal chunks
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Embeddings     │  ← Generate vectors (OpenAI)
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  ChromaDB       │  ← Store & search vectors
└─────────────────┘
       │
       ▼
┌─────────────────┐
│  User Question  │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Retrieval      │  ← Similarity search (top 10)
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│   Reranker      │  ← Relevance scoring (top 5)
│   (Cohere)      │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  LLM Generator  │  ← GPT-4o-mini
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│     Answer      │
└─────────────────┘
```

### Project Structure

```
app/
├── main.py                 # FastAPI application entry
├── core/
│   └── config.py          # Centralized configuration
├── crawler/
│   ├── scraper.py         # Web scraping logic
│   └── cleaner.py         # HTML cleaning
├── rag/
│   ├── embeddings.py      # OpenAI embeddings service
│   ├── vector_store.py    # ChromaDB wrapper
│   ├── chunking.py        # Text chunking
│   ├── retriever.py       # Similarity search
│   ├── reranker.py        # Cohere reranking
│   ├── generator.py       # LLM answer generation
│   └── prompts.py         # Hardened system prompts
├── services/
│   ├── crawl_service.py   # Crawling orchestration
│   └── rag_service.py     # RAG orchestration
└── api/
    └── routes/
        ├── crawl.py       # Crawling endpoints
        └── chat.py        # Chat endpoints
```

---

## 📦 Installation

### Prerequisites
- Python 3.9+
- OpenAI API key
- Cohere API key (optional, for reranking)

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/1farukdev/knowlia.git
cd knowlia
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and add your API keys:
# - OPENAI_API_KEY (required)
# - COHERE_API_KEY (optional, for reranking)
```

5. **Run the server**
```bash
uvicorn app.main:app --reload --port 8001
```

The API will be available at `http://localhost:8001`

---

## 💻 Usage

### 1. Crawl a Website

```bash
curl -X POST http://localhost:8001/crawl/site \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "max_pages": 50,
    "delay": 2.0
  }'
```

**Response:**
```json
{
  "start_url": "https://example.com",
  "pages_crawled": 15,
  "pages_failed": 0,
  "total_chunks": 87,
  "urls_discovered": 15,
  "urls_remaining": 0
}
```

### 2. Ask Questions

**Simple Question:**
```bash
curl -X POST http://localhost:8001/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What services do you provide?"
  }'
```

**With Conversation History:**
```bash
curl -X POST http://localhost:8001/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the pricing options?",
    "conversation_history": [
      {
        "role": "user",
        "content": "What services do you provide?"
      },
      {
        "role": "assistant",
        "content": "We provide cloud hosting..."
      }
    ]
  }'
```

**Response:**
```json
{
  "question": "What services do you provide?",
  "answer": "The company provides cloud hosting services...",
  "sources": [
    "https://example.com/services",
    "https://example.com/about"
  ],
  "chunks_used": 5,
  "model": "gpt-4o-mini"
}
```

---

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: `http://localhost:8001/docs`
- **ReDoc**: `http://localhost:8001/redoc`

### Endpoints

#### `POST /crawl/url`
Crawl and index a single URL

#### `POST /crawl/site`
Crawl an entire website (follows links)

#### `POST /chat/`
Ask questions about indexed content

---

## 🛠️ Technical Details

### RAG Pipeline

1. **Text Chunking**
   - Chunk size: 1000 tokens
   - Overlap: 200 tokens
   - Preserves metadata (URL, title, chunk index)

2. **Embeddings**
   - Model: `text-embedding-3-small`
   - Dimension: 1536
   - Batch processing for efficiency

3. **Vector Search**
   - Database: ChromaDB
   - Similarity: Cosine similarity
   - Retrieves top-10 similar chunks

4. **Reranking** (Optional)
   - Provider: Cohere Rerank API
   - Model: `rerank-english-v3.0`
   - Re-scores top-10 chunks by relevance
   - Returns top-5 most relevant
   - Gracefully disabled if API key not provided

5. **LLM Generation**
   - Model: `gpt-4o-mini`
   - Temperature: 0.1 (factual answers)
   - Context window: Optimized for token limits

### Conversation Memory

- Reformulates questions using conversation history
- Maintains context across follow-up questions
- LLM-powered query expansion

### Two-Stage Retrieval (Reranking)

Knowlia uses a sophisticated two-stage retrieval process:

1. **Stage 1: Vector Search** - Retrieves 10 semantically similar chunks using embeddings
2. **Stage 2: Reranking** - Re-scores those 10 chunks by relevance using Cohere's specialized model

**Why Reranking Matters:**
- Vector search finds **similar** content (based on embeddings)
- Reranking finds **relevant** content (based on actual question-answer relationship)
- Example: For "What's the pricing?", vector search might return "pricing model", "price history", "pricing page" - all similar, but reranking identifies the pricing page as most relevant

**Result:** ~10-15% improvement in answer quality and accuracy

### Security Features

- **Prompt injection protection** - Sanitizes user inputs
- **System prompt hardening** - Clear boundaries and instructions
- **Source citation enforcement** - Prevents hallucinations

---

## 🔧 Configuration

Key settings in `.env`:

```env
# Required
OPENAI_API_KEY=your_openai_key_here

# Optional - Reranking
COHERE_API_KEY=your_cohere_key_here  # Enables reranking for better quality
USE_RERANKING=True                   # Toggle reranking on/off

# Optional - Model Configuration
LLM_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
CHROMA_PERSIST_DIR=./chroma_data
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=5
RERANK_TOP_K=5
```

---

## 🎯 Roadmap

### Current Features
- ✅ Website crawling
- ✅ Semantic search
- ✅ Conversational Q&A
- ✅ Prompt hardening
- ✅ Reranking for better relevance

### Planned Features
- [ ] Playwright integration (JavaScript-heavy sites)
- [ ] Hybrid search (keyword + semantic)
- [ ] Document preprocessing (PDFs, images)
- [ ] Caching layer (Redis)
- [ ] Rate limiting
- [ ] Docker deployment
- [ ] Frontend UI

---

## 🧠 What I Learned

Building this project taught me:

- **RAG fundamentals** - End-to-end understanding vs black-box frameworks
- **Vector databases** - When to use Chroma vs Pinecone vs pgvector
- **Chunking strategies** - Trade-offs between chunk size and retrieval quality
- **Two-stage retrieval** - Why similarity ≠ relevance, and how reranking fixes this
- **Prompt engineering** - System prompt design and injection prevention
- **Production patterns** - Error handling, async/await, dependency injection

---

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [OpenAI](https://openai.com/) for GPT-4 and embeddings API
- [Cohere](https://cohere.com/) for the rerank API
- [ChromaDB](https://www.trychroma.com/) for the vector database
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework

---

## 📬 Contact

Faruk Ajibade - [@farukdev_](https://twitter.com/farukdev_)

Project Link: [https://github.com/1farukdev/knowlia](https://github.com/1FarukDev/knowlia)

---

<div align="center">

⭐ Star this repo if you found it helpful!

Built with ❤️ while learning AI Engineering

</div>
