"""
Notion output adapter.

Pushes structured study results into a user-owned Notion database.
Requires NOTION_API_TOKEN and NOTION_DATABASE_ID.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from notion_client import Client

from config.settings import Settings
from utils.logging import get_logger

logger = get_logger(__name__)


def push_to_notion(result: Dict[str, Any], settings: Settings) -> None:
    if not settings.notion_api_token or not settings.notion_database_id:
        raise ValueError("Notion credentials are not configured")

    client = Client(auth=settings.notion_api_token)

    title = result.get("source_file", "Untitled Study Note")
    now = datetime.now(timezone.utc).isoformat()

    # Minimal property set. Schema can be refined once the database is created.
    properties = {
        "Name": {"title": [{"text": {"content": title}}]},
        "Source File": {"rich_text": [{"text": {"content": result.get("source_file", "")}}]},
        "Processing Date": {"date": {"start": now}},
    }

    # Page body as simple paragraphs for now
    children = []
    for heading, key in [
        ("Summary", "summary"),
        ("Key Points", "key_points"),
        ("Definitions", "definitions"),
        ("Flashcards", "flashcards"),
        ("Color-Coded Notes", "color_coded"),
    ]:
        content = result.get(key) or ""
        if not content:
            continue
        children.append(
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {"rich_text": [{"type": "text", "text": {"content": heading}}]},
            }
        )
        # Split long text into manageable paragraph blocks
        for chunk in _chunk_text(content, 1800):
            children.append(
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {"rich_text": [{"type": "text", "text": {"content": chunk}}]},
                }
            )

    client.pages.create(
        parent={"database_id": settings.notion_database_id},
        properties=properties,
        children=children[:100],  # Notion has limits on children per request
    )
    logger.info("Pushed to Notion: %s", title)


def _chunk_text(text: str, size: int) -> list[str]:
    return [text[i : i + size] for i in range(0, len(text), size)] or [""]
