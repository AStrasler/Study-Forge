"""
Color Coder — semantic classification stage.

Receives the Judge's finalized content and classifies segments
according to the project's defined color system.
"""

from __future__ import annotations

from providers.base import ProviderResponse
from providers.manager import ProviderManager

# Exact semantic color system from the project specification
COLOR_SYSTEM = """
Hex               Meaning
#000000           Main Topics / Headers
#0000FF           Standard Notes
#ADD8E6           Scanning Protocols / Positioning
#000080           Anatomical Structures / Pathologies
#800080           Physics / Math / Formulas
#FF69B4           Clinical Red Flags / Contraindications / Safety
#008000           Professor Tips / Clinical Application
#FF0000           Corrections / Professor Emphasis
"""

SYSTEM = (
    "You are a semantic color classifier for study notes. "
    "Classify content according to the exact color system below. "
    "Prefer contextual/semantic judgment over simplistic keyword matching. "
    "Return the content with clear color labels (use the hex codes).\n\n"
    f"Color system:\n{COLOR_SYSTEM}"
)


def run(synthesized_text: str, manager: ProviderManager) -> ProviderResponse:
    prompt = (
        "Classify the following finalized study content using the semantic color system. "
        "Preserve the information; only add classification.\n\n"
        f"{synthesized_text}"
    )
    return manager.generate(prompt, system=SYSTEM)
