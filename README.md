# Deployable RAG API (FastAPI + Chroma + OpenAI/Ollama)

Production-ready starter for a deployable Retrieval-Augmented Generation (RAG) API.

## What improved in this version
- Better API contracts with explicit response models.
- Stable chunk IDs to prevent accidental collisions during repeated ingestion.
- Health endpoint now shows provider + indexed document count.
- Query endpoint supports `top_k` override for per-request retrieval tuning.
- Safer behavior when no context is found (returns a grounded fallback).

## Features
- Ingest raw text into persistent Chroma vector storage.
- Retrieve semantically relevant chunks for a question.
- Generate an answer with OpenAI or Ollama.
- Deploy with Docker Compose in a few commands.

## Quick deploy

1. Create environment file:
   ```bash
   cp .env.example .env
   ```

2. Start services:
   ```bash
   docker compose up --build -d
   ```

3. Pull the Ollama model (if `LLM_PROVIDER=ollama`):
   ```bash
   docker exec -it ollama ollama pull llama3.1:8b
   ```

4. Verify service:
   ```bash
   curl http://localhost:8000/health
   ```

## API examples

### 1) Ingest text
```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "source": "project-docs",
    "text": "RAG combines retrieval and generation to answer using your own data."
  }'
```

### 2) Ask with default retrieval
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is RAG?"}'
```

### 3) Ask with custom top-k
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is RAG?", "top_k": 6}'
```

## Switch providers

### Ollama (default)
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama3.1:8b
```

### OpenAI
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
```

## Local dev
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Tests
```bash
pytest -q
```
