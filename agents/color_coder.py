"""
Color Coder — semantic classification stage.

Receives the Judge's finalized content and classifies segments
according to the project's defined color system.

Returns structured segments so Notion (and other outputs) can apply
real formatting rather than free-form hex text labels alone.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional, Tuple

from providers.base import ProviderResponse
from providers.manager import ProviderManager
from utils.logging import get_logger

logger = get_logger(__name__)

# Exact semantic color system from the project specification
COLOR_MAP: Dict[str, str] = {
    "#000000": "Main Topics / Headers",
    "#0000FF": "Standard Notes",
    "#ADD8E6": "Scanning Protocols / Positioning",
    "#000080": "Anatomical Structures / Pathologies",
    "#800080": "Physics / Math / Formulas",
    "#FF69B4": "Clinical Red Flags / Contraindications / Safety",
    "#008000": "Professor Tips / Clinical Application",
    "#FF0000": "Corrections / Professor Emphasis",
}

VALID_HEX = set(COLOR_MAP.keys())

COLOR_SYSTEM_TEXT = "\n".join(f"{hex_}  {label}" for hex_, label in COLOR_MAP.items())

SYSTEM = (
    "You are a semantic color classifier for study notes. "
    "Classify content according to the exact color system below. "
    "Prefer contextual/semantic judgment over simplistic keyword matching.\n\n"
    f"Color system:\n{COLOR_SYSTEM_TEXT}\n\n"
    "Respond with ONLY a valid JSON array. No markdown fences, no commentary. "
    "Each element must be an object with exactly these keys:\n"
    '  "text": string (the content segment),\n'
    '  "color": string (exact hex from the system, e.g. "#800080"),\n'
    '  "category": string (exact category name from the system)\n'
    "Split the material into meaningful segments. Preserve all important information."
)


def run(synthesized_text: str, manager: ProviderManager) -> Tuple[ProviderResponse, List[Dict[str, str]]]:
    """
    Classify synthesized content.

    Returns:
        (raw ProviderResponse, list of structured segments)
    """
    prompt = (
        "Classify the following finalized study content using the semantic color system. "
        "Preserve the information; only add classification.\n\n"
        f"{synthesized_text}"
    )
    response = manager.generate(prompt, system=SYSTEM)
    segments = _parse_segments(response.text, fallback_text=synthesized_text)
    return response, segments


def _parse_segments(raw: str, fallback_text: str) -> List[Dict[str, str]]:
    """Parse model JSON into validated segments; fall back safely if malformed."""
    text = raw.strip()
    # Strip common markdown fences if the model ignores instructions
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        # Attempt to extract the first JSON array substring
        match = re.search(r"\[.*\]", text, re.DOTALL)
        if not match:
            logger.warning("Color Coder returned non-JSON; using single fallback segment")
            return [_fallback_segment(fallback_text)]
        try:
            data = json.loads(match.group(0))
        except json.JSONDecodeError:
            logger.warning("Color Coder JSON extract failed; using single fallback segment")
            return [_fallback_segment(fallback_text)]

    if not isinstance(data, list):
        logger.warning("Color Coder JSON was not a list; using fallback segment")
        return [_fallback_segment(fallback_text)]

    segments: List[Dict[str, str]] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        seg_text = str(item.get("text") or "").strip()
        if not seg_text:
            continue
        color = str(item.get("color") or "#0000FF").strip().upper()
        if not color.startswith("#"):
            color = f"#{color}"
        # Normalize short hex if needed; otherwise validate against known set
        if color not in VALID_HEX:
            # Try case-insensitive match
            matched = next((h for h in VALID_HEX if h.upper() == color.upper()), None)
            color = matched or "#0000FF"
        category = COLOR_MAP.get(color, item.get("category") or "Standard Notes")
        segments.append({"text": seg_text, "color": color, "category": category})

    if not segments:
        return [_fallback_segment(fallback_text)]
    return segments


def _fallback_segment(text: str) -> Dict[str, str]:
    return {
        "text": text,
        "color": "#0000FF",
        "category": "Standard Notes",
    }
