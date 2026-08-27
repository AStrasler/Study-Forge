"""
Core processing pipeline.

Processes files sequentially. One failure does not abort the batch.
Always preserves generated results to disk so Notion failures cannot
lose study material.

Also exposes process_text() for HTTP engines (Deepnote) without a path on disk.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from agents import color_coder, definitions, flashcards, judge, key_points, summarizer
from config.settings import Settings
from ingestion.extractors import extract_text
from providers.manager import ProviderManager
from utils.logging import get_logger

logger = get_logger(__name__)

SUPPORTED_SUFFIXES = {
    ".pdf",
    ".docx",
    ".pptx",
    ".txt",
    ".md",
    ".markdown",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".tif",
    ".tiff",
    ".bmp",
    ".gif",
    ".xlsx",
    ".xlsm",
}


def process_text(
    text: str,
    *,
    source_name: str = "upload.txt",
    settings: Optional[Settings] = None,
    providers: Optional[ProviderManager] = None,
    save_local: bool = True,
) -> Dict[str, Any]:
    """Canonical in-memory pipeline entry (Deepnote / API)."""
    if settings is None:
        settings = Settings.load()
    if providers is None:
        providers = ProviderManager(settings)

    body = (text or "").strip()
    if not body:
        raise ValueError(f"No extractable text for {source_name}")

    logger.info("Processing text: %s (%d chars)", source_name, len(body))

    summary = summarizer.run(body, providers)
    points = key_points.run(body, providers)
    cards = flashcards.run(body, providers)
    defs = definitions.run(body, providers)

    agent_outputs = {
        "summary": summary.text,
        "key_points": points.text,
        "flashcards": cards.text,
        "definitions": defs.text,
    }

    synthesized = judge.run(agent_outputs, providers)
    colored_response, color_segments = color_coder.run(synthesized.text, providers)

    result: Dict[str, Any] = {
        "source_file": source_name,
        "summary": summary.text,
        "key_points": points.text,
        "flashcards": cards.text,
        "definitions": defs.text,
        "synthesized": synthesized.text,
        "full_notes": synthesized.text,
        "study_notes": synthesized.text,
        "color_coded_raw": colored_response.text,
        "color_segments": color_segments,
        "provider_used": synthesized.provider,
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "host": "pipeline",
        "assistive": True,
    }

    if save_local:
        local_path = _save_local_result(result, settings)
        result["local_result_path"] = str(local_path)
        logger.info("Saved local result: %s", local_path)

    if settings.notion_api_token and settings.notion_database_id:
        try:
            from output.notion import push_to_notion

            ok = push_to_notion(result, settings)
            result["notion_pushed"] = bool(ok)
        except Exception as exc:
            logger.error("Notion push failed for %s: %s", source_name, exc)
            result["notion_pushed"] = False
            result["notion_error"] = str(exc)
    else:
        result["notion_pushed"] = False

    return result


def process_single_file(path: Path, settings: Settings, manager: ProviderManager) -> Dict[str, Any]:
    """Run the full agent pipeline on one file."""
    logger.info("Processing: %s", path.name)
    text = extract_text(path)
    return process_text(
        text,
        source_name=path.name,
        settings=settings,
        providers=manager,
        save_local=True,
    )


def _save_local_result(result: Dict[str, Any], settings: Settings) -> Path:
    out_dir = Path(settings.output_folder)
    out_dir.mkdir(parents=True, exist_ok=True)

    stem = Path(result.get("source_file", "result")).stem
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    base = out_dir / f"{stem}_{stamp}"

    json_path = base.with_suffix(".json")
    md_path = base.with_suffix(".md")

    with json_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    md_lines = [
        f"# Study Forge Result: {result.get('source_file', '')}",
        f"Processed: {result.get('processed_at', '')}",
        f"Provider: {result.get('provider_used', '')}",
        "",
        "## Summary",
        result.get("summary") or "",
        "",
        "## Key Points",
        result.get("key_points") or "",
        "",
        "## Definitions",
        result.get("definitions") or "",
        "",
        "## Flashcards",
        result.get("flashcards") or "",
        "",
        "## Synthesized",
        result.get("synthesized") or "",
        "",
        "## Color-Coded Segments",
    ]
    for seg in result.get("color_segments") or []:
        md_lines.append(
            f"- **[{seg.get('color')}] {seg.get('category')}**: {seg.get('text')}"
        )

    md_path.write_text("\n".join(md_lines), encoding="utf-8")
    return json_path


def process_input_folder(settings: Settings) -> List[Dict[str, Any]]:
    manager = ProviderManager(settings)
    input_dir = Path(settings.input_folder)
    results: List[Dict[str, Any]] = []

    if not input_dir.exists():
        logger.error("Input folder does not exist: %s", input_dir)
        return results

    files = sorted(
        p for p in input_dir.iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED_SUFFIXES
    )

    if not files:
        logger.warning("No supported files found in %s", input_dir)
        return results

    for path in files:
        try:
            result = process_single_file(path, settings, manager)
            results.append(result)
            logger.info(
                "Finished: %s (provider=%s, local=%s, notion=%s)",
                path.name,
                result.get("provider_used"),
                result.get("local_result_path"),
                result.get("notion_pushed"),
            )
        except Exception as exc:
            logger.error("Failed to process %s: %s", path.name, exc)
            results.append({"source_file": path.name, "error": str(exc)})

    return results
