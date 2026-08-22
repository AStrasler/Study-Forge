"""
Notion output adapter.

Pushes structured study results into a user-owned Notion database.
Requires NOTION_API_TOKEN and NOTION_DATABASE_ID.

- Creates the page first, then appends children in batches of ≤90
  so content is never silently truncated at the 100-block API limit.
- Applies the closest supported Notion text/block color for each
  semantic classification. Original hex + category are preserved
  in structured data and shown as labels where useful.
- Property payload is built from the live database schema so column
  names/types (e.g. Source File as files vs rich_text) do not break pushes.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from notion_client import Client

from config.settings import Settings
from utils.logging import get_logger

logger = get_logger(__name__)

HEX_TO_NOTION_COLOR: Dict[str, str] = {
    "#000000": "default",
    "#0000FF": "blue",
    "#ADD8E6": "blue_background",
    "#000080": "blue",
    "#800080": "purple",
    "#FF69B4": "pink",
    "#008000": "green",
    "#FF0000": "red",
}

BATCH_SIZE = 90

VALID_NOTION_COLORS = {
    "default", "gray", "brown", "orange", "yellow",
    "green", "blue", "purple", "pink", "red",
    "gray_background", "brown_background", "orange_background",
    "yellow_background", "green_background", "blue_background",
    "purple_background", "pink_background", "red_background",
}

# Preferred property names in order of preference
TITLE_CANDIDATES = ("Name", "Title", "name", "title")
SOURCE_CANDIDATES = ("Source File", "Source Files", "source_file", "Source")
DATE_CANDIDATES = ("Processing Date", "Date", "Processed", "processing_date")


def push_to_notion(result: Dict[str, Any], settings: Settings) -> bool:
    """
    Push study results to Notion.

    Returns:
        True on success.

    Raises:
        Exception on failure (so the pipeline can record notion_error).
    """
    if not settings.notion_api_token or not settings.notion_database_id:
        raise ValueError("Notion credentials are not configured")

    client = Client(auth=settings.notion_api_token)
    title = result.get("source_file", "Untitled Study Note")
    now = datetime.now(timezone.utc).isoformat()

    schema = _load_schema(client, settings.notion_database_id)
    properties = _build_properties(result, title, now, schema)
    children = _build_blocks(result)

    first_batch = children[:BATCH_SIZE]
    remaining = children[BATCH_SIZE:]

    page = client.pages.create(
        parent={"database_id": settings.notion_database_id},
        properties=properties,
        children=first_batch,
    )
    page_id = page["id"]
    logger.info("Created Notion page %s for %s", page_id, title)

    offset = 0
    while offset < len(remaining):
        batch = remaining[offset : offset + BATCH_SIZE]
        client.blocks.children.append(block_id=page_id, children=batch)
        offset += BATCH_SIZE
        logger.info(
            "Appended blocks %d–%d to page %s",
            BATCH_SIZE + offset - len(batch) + 1,
            BATCH_SIZE + offset,
            page_id,
        )

    logger.info("Pushed to Notion: %s (%d blocks)", title, len(children))
    return True


def _load_schema(client: Client, database_id: str) -> Dict[str, str]:
    """Return map of property name -> Notion property type."""
    db = client.databases.retrieve(database_id=database_id)
    props = db.get("properties") or {}
    schema = {name: (meta.get("type") or "") for name, meta in props.items()}
    logger.info("Notion DB properties: %s", schema)
    return schema


def _find_prop(schema: Dict[str, str], candidates: Tuple[str, ...], allowed_types: Optional[set] = None) -> Optional[Tuple[str, str]]:
    """Find first matching property name in schema (optional type filter)."""
    for name in candidates:
        if name in schema:
            ptype = schema[name]
            if allowed_types is None or ptype in allowed_types:
                return name, ptype
    # Also try case-insensitive match against actual schema keys
    lower_map = {k.lower(): k for k in schema}
    for name in candidates:
        key = lower_map.get(name.lower())
        if key:
            ptype = schema[key]
            if allowed_types is None or ptype in allowed_types:
                return key, ptype
    return None


def _build_properties(
    result: Dict[str, Any],
    title: str,
    now: str,
    schema: Dict[str, str],
) -> Dict[str, Any]:
    properties: Dict[str, Any] = {}

    # Title
    title_match = _find_prop(schema, TITLE_CANDIDATES, {"title"})
    if title_match:
        prop_name, _ = title_match
        properties[prop_name] = {
            "title": [{"text": {"content": _truncate(title, 2000)}}]
        }
    else:
        # Notion always has a title property; fall back to common name
        properties["Name"] = {
            "title": [{"text": {"content": _truncate(title, 2000)}}]
        }

    # Source file
    source_file = result.get("source_file") or ""
    source_match = _find_prop(schema, SOURCE_CANDIDATES, {"files", "rich_text", "url"})
    if source_match and source_file:
        prop_name, ptype = source_match
        if ptype == "files":
            # External file URL — works for remote links; local paths cannot be uploaded via API without multipart
            # Use a placeholder external URL that encodes the filename for traceability
            properties[prop_name] = {
                "files": [
                    {
                        "name": source_file[:100],
                        "type": "external",
                        "external": {
                            "url": f"https://studyforge.local/source/{source_file}"
                        },
                    }
                ]
            }
        elif ptype == "url":
            properties[prop_name] = {"url": f"https://studyforge.local/source/{source_file}"}
        else:
            properties[prop_name] = {
                "rich_text": [{"text": {"content": _truncate(source_file, 2000)}}]
            }

    # Processing date
    date_match = _find_prop(schema, DATE_CANDIDATES, {"date"})
    if date_match:
        prop_name, _ = date_match
        properties[prop_name] = {"date": {"start": now}}

    return properties


def _build_blocks(result: Dict[str, Any]) -> List[Dict[str, Any]]:
    blocks: List[Dict[str, Any]] = []

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

    segments = result.get("color_segments") or []
    if segments:
        blocks.append(_heading2("Color-Coded Notes"))
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
            notion_color = _validate_notion_color(HEX_TO_NOTION_COLOR.get(hex_color, "default"))

            label = f"[{hex_color} · {category}] "
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
        blocks.append(_heading2("Color-Coded Notes"))
        for chunk in _chunk_text(result["color_coded_raw"], 1800):
            blocks.append(_paragraph(chunk))

    return blocks


def _heading2(text: str) -> Dict[str, Any]:
    return {
        "object": "block",
        "type": "heading_2",
        "heading_2": {
            "rich_text": [{"type": "text", "text": {"content": _truncate(text, 2000)}}],
            "color": "default",
        },
    }


def _paragraph(text: str, color: str = "default") -> Dict[str, Any]:
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
    if color in VALID_NOTION_COLORS:
        return color
    return "default"


def _chunk_text(text: str, size: int) -> List[str]:
    if not text:
        return []
    return [text[i : i + size] for i in range(0, len(text), size)]


def _truncate(text: str, max_len: int) -> str:
    if not text:
        return ""
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"
