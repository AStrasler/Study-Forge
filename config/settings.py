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
    private_provider: str = "ollama"
    private_model: str = "llama3.2:1b"

    ollama_base_url: str = "http://localhost:11434"

    lmstudio_base_url: str = "http://localhost:1234"
    lmstudio_model: str = "qwen2.5-3b-instruct"

    groq_api_key: Optional[str] = None
    groq_model: str = "llama-3.3-70b-versatile"

    cloudflare_api_token: Optional[str] = None
    cloudflare_account_id: Optional[str] = None
    cloudflare_access_key_id: Optional[str] = None
    cloudflare_secret_access_key: Optional[str] = None
    cloudflare_s3_endpoint: Optional[str] = None

    gemini_api_key: Optional[str] = None
    huggingface_api_key: Optional[str] = None

    provider_fallback_order: List[str] = field(
        default_factory=lambda: ["lmstudio", "ollama", "groq", "cloudflare"]
    )

    notion_api_token: Optional[str] = None
    notion_worker_token: Optional[str] = None
    notion_database_id: Optional[str] = None

    input_folder: str = "./input"
    output_folder: str = "./results"
    provider_timeout: int = 300
    log_level: str = "INFO"

    cloudflare_tunnel_token: Optional[str] = None
    cloudflare_zero_trust_auth_domain: Optional[str] = None

    @classmethod
    def load(cls, env_file: str | Path | None = None) -> "Settings":
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()

        order = os.getenv(
            "PROVIDER_FALLBACK_ORDER",
            "lmstudio,ollama,groq,cloudflare",
        )

        return cls(
            private_provider=os.getenv("PRIVATE_PROVIDER", "ollama").strip().lower(),
            private_model=os.getenv("PRIVATE_MODEL", "llama3.2:1b").strip(),
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/"),
            lmstudio_base_url=os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234").rstrip("/"),
            lmstudio_model=os.getenv("LMSTUDIO_MODEL", "qwen2.5-3b-instruct").strip(),
            groq_api_key=os.getenv("GROQ_API_KEY") or None,
            groq_model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip(),
            cloudflare_api_token=os.getenv("CLOUDFLARE_API_TOKEN") or None,
            cloudflare_account_id=os.getenv("CLOUDFLARE_ACCOUNT_ID") or None,
            cloudflare_access_key_id=os.getenv("CLOUDFLARE_ACCESS_KEY_ID") or None,
            cloudflare_secret_access_key=os.getenv("CLOUDFLARE_SECRET_ACCESS_KEY") or None,
            cloudflare_s3_endpoint=os.getenv("CLOUDFLARE_S3_ENDPOINT") or None,
            gemini_api_key=os.getenv("GEMINI_API_KEY") or None,
            huggingface_api_key=os.getenv("HUGGINGFACE_API_KEY") or None,
            provider_fallback_order=_split_csv(order),
            notion_api_token=os.getenv("NOTION_API_TOKEN") or None,
            notion_worker_token=os.getenv("NOTION_WORKER_TOKEN") or None,
            notion_database_id=os.getenv("NOTION_DATABASE_ID") or None,
            input_folder=os.getenv("INPUT_FOLDER", "./input"),
            output_folder=os.getenv("OUTPUT_FOLDER", "./results"),
            provider_timeout=int(os.getenv("PROVIDER_TIMEOUT", "300")),
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
            cloudflare_tunnel_token=os.getenv("CLOUDFLARE_TUNNEL_TOKEN") or None,
            cloudflare_zero_trust_auth_domain=os.getenv("CLOUDFLARE_ZERO_TRUST_AUTH_DOMAIN") or None,
        )