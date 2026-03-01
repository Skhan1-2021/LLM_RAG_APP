# Deployable RAG API (FastAPI + Chroma + OpenAI/Ollama)

This repository now includes a complete Retrieval-Augmented Generation (RAG) backend that you can deploy directly to your own Git repository.

## Features
- Ingest raw text into a persistent vector database (Chroma).
- Retrieve relevant chunks for each question.
- Generate answers using either:
  - **OpenAI** (`LLM_PROVIDER=openai`), or
  - **Ollama local model** (`LLM_PROVIDER=ollama`, default in `.env.example`).
- Dockerized deployment via `docker compose`.

## Quick deploy

1. Copy environment template:
   ```bash
   cp .env.example .env
   ```

2. (Optional) If using OpenAI, set:
   ```env
   LLM_PROVIDER=openai
   OPENAI_API_KEY=your_key_here
   ```

3. Start services:
   ```bash
   docker compose up --build -d
   ```

4. Pull Ollama model (only needed when `LLM_PROVIDER=ollama`):
   ```bash
   docker exec -it ollama ollama pull llama3.1:8b
   ```

5. Health check:
   ```bash
   curl http://localhost:8000/health
   ```

## API usage

### Ingest data
```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "source": "docs",
    "text": "RAG combines retrieval and generation to ground LLM answers in your own data."
  }'
```

### Ask a question
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What does RAG do?"}'
```

## Local development
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Run tests
```bash
pytest
```
