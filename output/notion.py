"""
Notion output adapter.

Pushes structured study results into a user-owned Notion database.
Requires NOTION_API_TOKEN and NOTION_DATABASE_ID.

- Creates the page first, then appends children in batches of ≤90
  so content is never silently truncated at the 100-block API limit.
- Applies the closest supported Notion text/block color for each
  semantic classification. Original hex + category are preserved
  in structured data and shown as labels where useful.
- Source File property uses GitHub raw URL if the file is in the repo.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from notion_client import Client

from config.settings import Settings
from utils.logging import get_logger

logger = get_logger(__name__)

# Notion supports a fixed set of annotation/block colors — not arbitrary hex.
# Map project semantic hex → closest supported Notion color.
# Documented limitation: exact hex cannot be reproduced in Notion's API.
HEX_TO_NOTION_COLOR: Dict[str, str] = {
    "#000000": "default",           # Main Topics / Headers
    "#0000FF": "blue",              # Standard Notes
    "#ADD8E6": "blue_background",   # Scanning Protocols / Positioning
    "#000080": "blue",              # Anatomical Structures / Pathologies
    "#800080": "purple",            # Physics / Math / Formulas
    "#FF69B4": "pink",              # Clinical Red Flags / Safety
    "#008000": "green",             # Professor Tips / Clinical Application
    "#FF0000": "red",               # Corrections / Professor Emphasis
}

BATCH_SIZE = 90  # stay under Notion's 100-children-per-request limit

# Valid Notion colors for validation
VALID_NOTION_COLORS = {
    "default", "gray", "brown", "orange", "yellow",
    "green", "blue", "purple", "pink", "red",
    "gray_background", "brown_background", "orange_background",
    "yellow_background", "green_background", "blue_background",
    "purple_background", "pink_background", "red_background"
}

# GitHub raw URL base for files in this repository
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/AStrasler/Study-Forge/refs/heads/main/input/"


def push_to_notion(result: Dict[str, Any], settings: Settings) -> bool:
    """
    Push study results to Notion.

    Args:
        result: The processed study result dictionary.
        settings: Application settings containing Notion credentials.

    Returns:
        True if successful, False otherwise.
    """
    if not settings.notion_api_token or not settings.notion_database_id:
        logger.error("Notion credentials are not configured")
        return False

    try:
        client = Client(auth=settings.notion_api_token)
        title = result.get("source_file", "Untitled Study Note")
        now = datetime.now(timezone.utc).isoformat()

        # Build properties with correct types
        properties = _build_properties(result, title, now)

        # Build page children
        children = _build_blocks(result)

        # Create page with first batch (or empty if no children yet)
        first_batch = children[:BATCH_SIZE]
        remaining = children[BATCH_SIZE:]

        page = client.pages.create(
            parent={"database_id": settings.notion_database_id},
            properties=properties,
            children=first_batch,
        )
        page_id = page["id"]
        logger.info("Created Notion page %s for %s", page_id, title)

        # Append remaining batches
        offset = 0
        while offset < len(remaining):
            batch = remaining[offset: offset + BATCH_SIZE]
            client.blocks.children.append(block_id=page_id, children=batch)
            offset += BATCH_SIZE
            logger.info(
                "Appended blocks %d–%d to page %s",
                BATCH_SIZE + offset - len(batch) + 1,
                BATCH_SIZE + offset,
                page_id,
            )

        total = len(children)
        logger.info("Pushed to Notion: %s (%d blocks)", title, total)
        return True

    except Exception as e:
        logger.error("Notion push failed: %s", e)
        return False


def _build_properties(result: Dict[str, Any], title: str, now: str) -> Dict[str, Any]:
    """
    Build Notion page properties with correct types.

    The database columns must be:
    - Name (Title)
    - Source File (Files & media)
    - Processing Date (Date)
    """
    properties = {
        "Name": {
            "title": [{"text": {"content": _truncate(title, 2000)}}]
        },
        "Processing Date": {
            "date": {"start": now}
        },
    }

    # Source File — use GitHub raw URL as a file attachment
    source_file = result.get("source_file", "")
    if source_file:
        raw_url = f"{GITHUB_RAW_BASE}{source_file}"
        properties["Source File"] = {
            "files": [
                {
                    "name": source_file,
                    "type": "external",
                    "external": {"url": raw_url}
                }
            ]
        }
        logger.info("Source File URL: %s", raw_url)
    else:
        # Fallback: empty files array if no source file
        properties["Source File"] = {"files": []}

    return properties


def _build_blocks(result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Build Notion blocks from study result."""
    blocks: List[Dict[str, Any]] = []

    # Standard sections (plain text body)
    for heading, key in [
        ("Summary", "summary"),
        ("Key Points", "key_points"),
        ("Definitions", "definitions"),
        ("Flashcards", "flashcards"),
        ("Synthesized Notes", "synthesized"),
    ]:
        content = result.get(key) or ""
        if not content:
            continue
        blocks.append(_heading2(heading))
        for chunk in _chunk_text(content, 1800):
            blocks.append(_paragraph(chunk))

    # Color-coded segments with Notion colors
    segments = result.get("color_segments") or []
    if segments:
        blocks.append(_heading2("Color-Coded Notes"))
        # Legend
        blocks.append(
            _paragraph(
                "Semantic colors mapped to nearest Notion-supported colors. "
                "Original project hex values are preserved in labels.",
                color="gray",
            )
        )
        for seg in segments:
            hex_color = (seg.get("color") or "#0000FF").upper()
            if not hex_color.startswith("#"):
                hex_color = f"#{hex_color}"
            category = seg.get("category") or "Standard Notes"
            text = seg.get("text") or ""
            notion_color = HEX_TO_NOTION_COLOR.get(hex_color, "default")
            notion_color = _validate_notion_color(notion_color)

            label = f"[{hex_color} · {category}] "
            # Label in gray, body in mapped color
            blocks.append(
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": _truncate(label, 500)},
                                "annotations": {
                                    "bold": True,
                                    "italic": False,
                                    "strikethrough": False,
                                    "underline": False,
                                    "code": False,
                                    "color": "gray",
                                },
                            },
                            {
                                "type": "text",
                                "text": {"content": _truncate(text, 1900)},
                                "annotations": {
                                    "bold": False,
                                    "italic": False,
                                    "strikethrough": False,
                                    "underline": False,
                                    "code": False,
                                    "color": (
                                        notion_color
                                        if not notion_color.endswith("_background")
                                        else "default"
                                    ),
                                },
                            },
                        ],
                        "color": (
                            notion_color
                            if notion_color.endswith("_background")
                            else "default"
                        ),
                    },
                }
            )
    elif result.get("color_coded_raw"):
        # Fallback if structured segments missing
        blocks.append(_heading2("Color-Coded Notes"))
        for chunk in _chunk_text(result["color_coded_raw"], 1800):
            blocks.append(_paragraph(chunk))

    return blocks


def _heading2(text: str) -> Dict[str, Any]:
    """Create a heading_2 block."""
    return {
        "object": "block",
        "type": "heading_2",
        "heading_2": {
            "rich_text": [{"type": "text", "text": {"content": _truncate(text, 2000)}}],
            "color": "default",
        },
    }


def _paragraph(text: str, color: str = "default") -> Dict[str, Any]:
    """Create a paragraph block with optional color."""
    color = _validate_notion_color(color)
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": _truncate(text, 2000)},
                    "annotations": {
                        "bold": False,
                        "italic": False,
                        "strikethrough": False,
                        "underline": False,
                        "code": False,
                        "color": color if not color.endswith("_background") else "default",
                    },
                }
            ],
            "color": color if color.endswith("_background") else "default",
        },
    }


def _validate_notion_color(color: str) -> str:
    """Ensure the color is a valid Notion color string."""
    if color in VALID_NOTION_COLORS:
        return color
    return "default"


def _chunk_text(text: str, size: int) -> List[str]:
    """Split text into chunks of roughly `size` characters."""
    if not text:
        return []
    return [text[i: i + size] for i in range(0, len(text), size)]


def _truncate(text: str, max_len: int) -> str:
    """Truncate text to max_len with ellipsis."""
    if not text:
        return ""
    if len(text) <= max_len:
        return text
    return text[:max_len - 1] + "…"