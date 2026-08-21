"""
Core processing pipeline.

Processes files sequentially. One failure does not abort the batch.
"""

from __future__ import annotations

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

    # Specialized agents
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

    # Judge / synthesis
    synthesized = judge.run(agent_outputs, manager)

    # Color classification
    colored = color_coder.run(synthesized.text, manager)

    result = {
        "source_file": path.name,
        "summary": summary.text,
        "key_points": points.text,
        "flashcards": cards.text,
        "definitions": defs.text,
        "synthesized": synthesized.text,
        "color_coded": colored.text,
        "provider_used": synthesized.provider,
    }

    # Notion output (optional — only if configured)
    if settings.notion_api_token and settings.notion_database_id:
        try:
            from output.notion import push_to_notion

            push_to_notion(result, settings)
            result["notion_pushed"] = True
        except Exception as exc:
            logger.error("Notion push failed for %s: %s", path.name, exc)
            result["notion_pushed"] = False
            result["notion_error"] = str(exc)
    else:
        result["notion_pushed"] = False

    return result


def process_input_folder(settings: Settings) -> List[Dict[str, Any]]:
    """Process every supported file in the input folder sequentially."""
    manager = ProviderManager(settings)
    input_dir = Path(settings.input_folder)
    results: List[Dict[str, Any]] = []

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
            logger.info("Finished: %s (provider=%s)", path.name, result.get("provider_used"))
        except Exception as exc:
            logger.error("Failed to process %s: %s", path.name, exc)
            results.append(
                {
                    "source_file": path.name,
                    "error": str(exc),
                }
            )
            # Continue with remaining files

    return results
