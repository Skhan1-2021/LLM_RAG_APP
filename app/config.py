from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "RAG API"
    collection_name: str = "documents"
    persist_directory: str = "./data/chroma"
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    retrieval_k: int = 4

    llm_provider: str = "ollama"  # openai | ollama
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"

    ollama_base_url: str = "http://ollama:11434"
    ollama_model: str = "llama3.1:8b"


settings = Settings()
