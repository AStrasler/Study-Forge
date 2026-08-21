"""Key Points agent — extracts approximately 5–8 important takeaways."""

from __future__ import annotations

from providers.base import ProviderResponse
from providers.manager import ProviderManager

SYSTEM = (
    "You extract the most important takeaways from study material. "
    "Return 5 to 8 clear, non-redundant key points. "
    "Use a numbered list. Do not invent information."
)


def run(text: str, manager: ProviderManager) -> ProviderResponse:
    prompt = f"Extract the key points from the following study material:\n\n{text}"
    return manager.generate(prompt, system=SYSTEM)
