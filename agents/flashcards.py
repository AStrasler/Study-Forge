"""Flashcards agent — creates Q&A pairs for active recall."""

from __future__ import annotations

from providers.base import ProviderResponse
from providers.manager import ProviderManager

SYSTEM = (
    "You create high-quality flashcards for active recall. "
    "Produce clear Question / Answer pairs based only on the provided material. "
    "Prefer conceptual and applied questions over pure trivia."
)


def run(text: str, manager: ProviderManager) -> ProviderResponse:
    prompt = (
        "Create flashcards (Question / Answer) from the following study material.\n"
        "Format each card as:\nQ: ...\nA: ...\n\n"
        f"Material:\n{text}"
    )
    return manager.generate(prompt, system=SYSTEM)
