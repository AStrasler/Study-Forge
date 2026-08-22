"""
Centralized configuration loaded from environment variables / .env file.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv


def _split_csv(value: str) -> List[str]:
    return [item.strip().lower() for item in value.split(",") if item.strip()]


@dataclass
class Settings:
    # Local providers
    local_provider: str = "ollama"
    local_model: str = "llama3.2"

    # Ollama
    ollama_base_url: str = "http://localhost:11434"

    # Fox (local inference)
    fox_base_url: str = "http://localhost:8080"
    fox_model: str = "llama3.2:3b"
    fox_timeout: int = 300

    # Mullama (in-process inference)
    mullama_model: str = "llama3.2:3b"
    mullama_gpu_layers: int = 32
    mullama_context_size: int = 2048
    mullama_embedding_model: Optional[str] = None

    # Cloud BYOK (optional)
    groq_api_key: Optional[str] = None
    groq_model: str = "llama-3.3-70b-versatile"
    cloudflare_api_token: Optional[str] = None
    cloudflare_account_id: Optional[str] = None
    gemini_api_key: Optional[str] = None
    huggingface_api_key: Optional[str] = None

    # Fallback order
    provider_fallback_order: List[str] = field(
        default_factory=lambda: ["ollama", "fox", "mullama", "groq", "cloudflare", "gemini", "huggingface"]
    )

    # Notion
    notion_api_token: Optional[str] = None
    notion_database_id: Optional[str] = None

    # Paths & runtime
    input_folder: str = "./input"
    output_folder: str = "./results"
    provider_timeout: int = 300
    log_level: str = "INFO"

    @classmethod
    def load(cls, env_file: str | Path | None = None) -> "Settings":
        """Load settings from .env (if present) and process environment."""
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()

        order = os.getenv("PROVIDER_FALLBACK_ORDER", "ollama,fox,mullama,groq,cloudflare,gemini,huggingface")

        return cls(
            local_provider=os.getenv("LOCAL_PROVIDER", "ollama").strip().lower(),
            local_model=os.getenv("LOCAL_MODEL", "llama3.2").strip(),
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/"),
            fox_base_url=os.getenv("FOX_BASE_URL", "http://localhost:8080").rstrip("/"),
            fox_model=os.getenv("FOX_MODEL", "llama3.2:3b").strip(),
            fox_timeout=int(os.getenv("FOX_TIMEOUT", "300")),
            mullama_model=os.getenv("MULLAMA_MODEL", "llama3.2:3b").strip(),
            mullama_gpu_layers=int(os.getenv("MULLAMA_GPU_LAYERS", "32")),
            mullama_context_size=int(os.getenv("MULLAMA_CONTEXT_SIZE", "2048")),
            mullama_embedding_model=os.getenv("MULLAMA_EMBEDDING_MODEL") or None,
            groq_api_key=os.getenv("GROQ_API_KEY") or None,
            groq_model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip(),
            cloudflare_api_token=os.getenv("CLOUDFLARE_API_TOKEN") or None,
            cloudflare_account_id=os.getenv("CLOUDFLARE_ACCOUNT_ID") or None,
            gemini_api_key=os.getenv("GEMINI_API_KEY") or None,
            huggingface_api_key=os.getenv("HUGGINGFACE_API_KEY") or None,
            provider_fallback_order=_split_csv(order),
            notion_api_token=os.getenv("NOTION_API_TOKEN") or None,
            notion_database_id=os.getenv("NOTION_DATABASE_ID") or None,
            input_folder=os.getenv("INPUT_FOLDER", "./input"),
            output_folder=os.getenv("OUTPUT_FOLDER", "./results"),
            provider_timeout=int(os.getenv("PROVIDER_TIMEOUT", "300")),
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        )