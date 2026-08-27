"""
Study Forge — Deepnote BYOS engine
===================================
Canonical Python pipeline over HTTP. Port 8080 for Deepnote Incoming connections.

  python deepnote/engine_api.py

Env:
  ENGINE_AUTH_TOKEN   required (fail closed)
  GROQ_API_KEY        preferred inference on Deepnote (no device dependency)
  PROVIDER_FALLBACK_ORDER  default groq,...
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="Study Forge Engine", version="0.2.0")

# Restrict later via ENGINE_CORS_ORIGINS; * only if unset (early BYOS)
_cors = os.environ.get("ENGINE_CORS_ORIGINS", "*").strip()
_origins = [o.strip() for o in _cors.split(",") if o.strip()] if _cors != "*" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

MAX_TEXT_CHARS = int(os.environ.get("ENGINE_MAX_TEXT_CHARS", "200000"))


def _require_token(x_engine_token: str | None) -> None:
    expected = (os.environ.get("ENGINE_AUTH_TOKEN") or "").strip()
    if not expected:
        raise HTTPException(
            status_code=503,
            detail="ENGINE_AUTH_TOKEN is not configured (fail closed)",
        )
    if not x_engine_token or x_engine_token.strip() != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing X-Engine-Token")


class ForgeRequest(BaseModel):
    text: str = Field(..., min_length=10)
    filename: str = "upload.txt"


@app.get("/health")
def health():
    """Operational state only — does not advertise which keys exist."""
    token_ok = bool((os.environ.get("ENGINE_AUTH_TOKEN") or "").strip())
    # Inference ready if any preferred path could work (presence only, not live probe)
    inference = bool(
        (os.environ.get("GROQ_API_KEY") or "").strip()
        or (os.environ.get("LMSTUDIO_BASE_URL") or "").strip()
        or (os.environ.get("OLLAMA_BASE_URL") or "").strip()
    )
    return {
        "ok": token_ok and inference,
        "service": "study-forge-engine",
        "version": "0.2.0",
        "host": "deepnote",
        "pipeline": "ready",
        "inference": "ready" if inference else "not_configured",
        "auth": "ready" if token_ok else "not_configured",
        "time": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/forge")
def forge(
    body: ForgeRequest,
    x_engine_token: str | None = Header(default=None),
):
    _require_token(x_engine_token)

    text = body.text.strip()
    if len(text) < 10:
        raise HTTPException(status_code=400, detail="text too short")
    if len(text) > MAX_TEXT_CHARS:
        raise HTTPException(
            status_code=413,
            detail=f"text exceeds ENGINE_MAX_TEXT_CHARS ({MAX_TEXT_CHARS})",
        )

    try:
        from config.settings import Settings
        from pipeline.processor import process_text
        from providers.manager import ProviderManager

        settings = Settings.load()
        # On Deepnote we usually don't want Notion side-effects unless configured
        manager = ProviderManager(settings)
        pack = process_text(
            text,
            source_name=body.filename or "upload.txt",
            settings=settings,
            providers=manager,
            save_local=True,
        )
        pack["host"] = "deepnote"
        return {
            "ok": True,
            "filename": body.filename,
            "provider_used": pack.get("provider_used"),
            "processed_at": pack.get("processed_at"),
            "pack": pack,
            "error": None,
        }
    except HTTPException:
        raise
    except Exception as exc:
        return {
            "ok": False,
            "filename": body.filename,
            "provider_used": None,
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "pack": {},
            "error": str(exc)[:800],
        }


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
