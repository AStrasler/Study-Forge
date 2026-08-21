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
    # Local
    local_provider: str = "ollama"
    local_model: str = "llama3.2"
    ollama_base_url: str = "http://localhost:11434"

    # Cloud BYOK (optional)
    groq_api_key: Optional[str] = None
    cloudflare_api_token: Optional[str] = None
    cloudflare_account_id: Optional[str] = None
    gemini_api_key: Optional[str] = None
    huggingface_api_key: Optional[str] = None

    # Fallback order
    provider_fallback_order: List[str] = field(
        default_factory=lambda: ["ollama", "groq", "cloudflare", "gemini", "huggingface"]
    )

    # Notion
    notion_api_token: Optional[str] = None
    notion_database_id: Optional[str] = None

    # Paths & runtime
    # NOTE: results go to ./results — not ./output — to avoid colliding with the
    # Python package directory named "output/".
    input_folder: str = "./input"
    output_folder: str = "./results"
    provider_timeout: int = 120
    log_level: str = "INFO"

    @classmethod
    def load(cls, env_file: str | Path | None = None) -> "Settings":
        """Load settings from .env (if present) and process environment."""
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()  # looks for .env in cwd and parents

        order = os.getenv("PROVIDER_FALLBACK_ORDER", "ollama,groq,cloudflare,gemini,huggingface")

        return cls(
            local_provider=os.getenv("LOCAL_PROVIDER", "ollama").strip().lower(),
            local_model=os.getenv("LOCAL_MODEL", "llama3.2").strip(),
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/"),
            groq_api_key=os.getenv("GROQ_API_KEY") or None,
            cloudflare_api_token=os.getenv("CLOUDFLARE_API_TOKEN") or None,
            cloudflare_account_id=os.getenv("CLOUDFLARE_ACCOUNT_ID") or None,
            gemini_api_key=os.getenv("GEMINI_API_KEY") or None,
            huggingface_api_key=os.getenv("HUGGINGFACE_API_KEY") or None,
            provider_fallback_order=_split_csv(order),
            notion_api_token=os.getenv("NOTION_API_TOKEN") or None,
            notion_database_id=os.getenv("NOTION_DATABASE_ID") or None,
            input_folder=os.getenv("INPUT_FOLDER", "./input"),
            output_folder=os.getenv("OUTPUT_FOLDER", "./results"),
            provider_timeout=int(os.getenv("PROVIDER_TIMEOUT", "120")),
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        )
