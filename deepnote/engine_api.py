"""
Study Forge — Deepnote BYOS engine
===================================
Run on Deepnote with Incoming connections enabled (port 8080).

  python deepnote/engine_api.py

Or from repo root after pip install -r requirements.txt fastapi uvicorn.

Endpoints:
  GET  /health
  POST /forge   JSON: { "text": "...", "filename": "notes.txt" }
                optional header: X-Engine-Token: <ENGINE_AUTH_TOKEN>
"""

from __future__ import annotations

import os
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

# Allow importing Study Forge packages when cwd is deepnote/ or repo root
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="Study Forge Engine", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _check_token(x_engine_token: str | None) -> None:
    expected = os.environ.get("ENGINE_AUTH_TOKEN", "").strip()
    if not expected:
        return  # open on private Deepnote URL; set token for production
    if not x_engine_token or x_engine_token.strip() != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing X-Engine-Token")


class ForgeRequest(BaseModel):
    text: str = Field(..., min_length=10)
    filename: str = "upload.txt"


class ForgeResponse(BaseModel):
    ok: bool
    filename: str
    provider_used: str | None = None
    processed_at: str
    pack: dict
    error: str | None = None


@app.get("/health")
def health():
    return {
        "ok": True,
        "service": "study-forge-deepnote-engine",
        "version": "0.1.0",
        "host": "deepnote",
        "time": datetime.now(timezone.utc).isoformat(),
        "has_groq": bool(os.environ.get("GROQ_API_KEY")),
        "has_lmstudio": bool(os.environ.get("LMSTUDIO_BASE_URL")),
        "token_required": bool(os.environ.get("ENGINE_AUTH_TOKEN", "").strip()),
    }


@app.post("/forge", response_model=ForgeResponse)
def forge(
    body: ForgeRequest,
    x_engine_token: str | None = Header(default=None),
):
    _check_token(x_engine_token)
    text = body.text.strip()
    if len(text) < 10:
        raise HTTPException(status_code=400, detail="text too short")

    processed_at = datetime.now(timezone.utc).isoformat()

    # Prefer full Python pipeline when available
    try:
        pack = _run_pipeline(text, body.filename)
        return ForgeResponse(
            ok=True,
            filename=body.filename,
            provider_used=pack.get("provider_used"),
            processed_at=processed_at,
            pack=pack,
        )
    except Exception as first_err:
        # Fallback: single-shot via env-configured OpenAI-compatible endpoint
        try:
            pack = _run_simple_pack(text, body.filename)
            pack["pipeline_error"] = str(first_err)[:300]
            return ForgeResponse(
                ok=True,
                filename=body.filename,
                provider_used=pack.get("provider_used"),
                processed_at=processed_at,
                pack=pack,
            )
        except Exception as second_err:
            return ForgeResponse(
                ok=False,
                filename=body.filename,
                processed_at=processed_at,
                pack={},
                error=f"pipeline: {first_err!s}; simple: {second_err!s}"[:800],
            )


def _run_pipeline(text: str, filename: str) -> dict:
    """Use existing Study Forge pipeline if imports work."""
    from config.settings import Settings
    from providers.manager import ProviderManager
    from pipeline.processor import process_text  # type: ignore

    settings = Settings.load()
    manager = ProviderManager(settings)
    result = process_text(
        text=text,
        source_name=filename,
        settings=settings,
        providers=manager,
    )
    if isinstance(result, dict):
        return result
    # object with attributes
    return {
        "source_file": filename,
        "summary": getattr(result, "summary", "") or "",
        "key_points": getattr(result, "key_points", "") or "",
        "definitions": getattr(result, "definitions", "") or "",
        "flashcards": getattr(result, "flashcards", []) or [],
        "full_notes": getattr(result, "synthesized", "") or str(result),
        "provider_used": getattr(result, "provider_used", None),
        "host": "deepnote",
    }


def _run_simple_pack(text: str, filename: str) -> dict:
    """Minimal pack via LM Studio or Groq — no full agent graph."""
    import json
    import urllib.request

    system = (
        "You are Study Forge. Build a study pack. Assistive, not homework answers.\n"
        "Use headers: ## Summary, ## Key Points, ## Definitions, ## Flashcards, ## Quiz, ## Study Notes\n"
        "Flashcards as Q: / A: lines. Quiz with A) B) C) D), Hint, Answer, Explanation."
    )
    user = text[:14000]

    lm = (os.environ.get("LMSTUDIO_BASE_URL") or "").rstrip("/")
    if lm:
        url = lm + ("/chat/completions" if "/v1" in lm else "/v1/chat/completions")
        model = os.environ.get("LMSTUDIO_MODEL") or "local-model"
        payload = {
            "model": model,
            "temperature": 0.3,
            "max_tokens": 3200,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        content = data["choices"][0]["message"]["content"]
        return {
            "source_file": filename,
            "full_notes": content,
            "provider_used": "lmstudio",
            "host": "deepnote",
        }

    key = os.environ.get("GROQ_API_KEY") or ""
    if key:
        url = "https://api.groq.com/openai/v1/chat/completions"
        model = os.environ.get("GROQ_MODEL") or "llama-3.1-8b-instant"
        payload = {
            "model": model,
            "temperature": 0.3,
            "max_tokens": 3200,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {key}",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        content = data["choices"][0]["message"]["content"]
        return {
            "source_file": filename,
            "full_notes": content,
            "provider_used": "groq",
            "host": "deepnote",
        }

    raise RuntimeError("Set LMSTUDIO_BASE_URL or GROQ_API_KEY in Deepnote env vars")


if __name__ == "__main__":
    import uvicorn

    # Deepnote incoming connections only expose 8080
    port = int(os.environ.get("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
