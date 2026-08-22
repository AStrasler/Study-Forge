"""
Core processing pipeline.

Processes files sequentially. One failure does not abort the batch.
Always preserves generated results to disk so Notion failures cannot
lose study material.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from agents import color_coder, definitions, flashcards, judge, key_points, summarizer
from config.settings import Settings
from ingestion.extractors import extract_text
from providers.manager import ProviderManager
from utils.logging import get_logger

logger = get_logger(__name__)

SUPPORTED_SUFFIXES = {".pdf", ".docx", ".pptx", ".txt", ".md", ".markdown"}


def process_single_file(path: Path, settings: Settings, manager: ProviderManager) -> Dict[str, Any]:
    """Run the full agent pipeline on one file."""
    logger.info("Processing: %s", path.name)

    text = extract_text(path)
    if not text.strip():
        raise ValueError(f"No extractable text in {path.name}")

    summary = summarizer.run(text, manager)
    points = key_points.run(text, manager)
    cards = flashcards.run(text, manager)
    defs = definitions.run(text, manager)

    agent_outputs = {
        "summary": summary.text,
        "key_points": points.text,
        "flashcards": cards.text,
        "definitions": defs.text,
    }

    synthesized = judge.run(agent_outputs, manager)
    colored_response, color_segments = color_coder.run(synthesized.text, manager)

    result: Dict[str, Any] = {
        "source_file": path.name,
        "summary": summary.text,
        "key_points": points.text,
        "flashcards": cards.text,
        "definitions": defs.text,
        "synthesized": synthesized.text,
        "color_coded_raw": colored_response.text,
        "color_segments": color_segments,
        "provider_used": synthesized.provider,
        "processed_at": datetime.now(timezone.utc).isoformat(),
    }

    local_path = _save_local_result(result, settings)
    result["local_result_path"] = str(local_path)
    logger.info("Saved local result: %s", local_path)

    if settings.notion_api_token and settings.notion_database_id:
        try:
            from output.notion import push_to_notion

            ok = push_to_notion(result, settings)
            result["notion_pushed"] = bool(ok)
            if not ok:
                result["notion_error"] = "push_to_notion returned False"
                _save_local_result(result, settings)
        except Exception as exc:
            logger.error("Notion push failed for %s: %s", path.name, exc)
            result["notion_pushed"] = False
            result["notion_error"] = str(exc)
            _save_local_result(result, settings)
    else:
        result["notion_pushed"] = False
        logger.info("Notion not configured — local result only")

    return result


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
