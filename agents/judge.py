"""
Judge / Synthesis agent.

Receives outputs from the specialized agents, compares them,
filters weak or redundant information, reconciles differences,
and produces a coherent final study result.
"""

from __future__ import annotations

from typing import Dict

from providers.base import ProviderResponse
from providers.manager import ProviderManager

SYSTEM = (
    "You are the Judge / Synthesis stage of a multi-agent study pipeline. "
    "You receive outputs from specialized agents (summary, key points, "
    "flashcards, definitions). Your job is to:\n"
    "- compare the outputs\n"
    "- identify conflicts or contradictions\n"
    "- remove weak or redundant information\n"
    "- reconcile differences\n"
    "- produce one coherent, high-quality final study package.\n"
    "Do not simply concatenate the inputs. Synthesize."
)


def run(agent_outputs: Dict[str, str], manager: ProviderManager) -> ProviderResponse:
    sections = []
    for name, content in agent_outputs.items():
        sections.append(f"=== {name.upper()} ===\n{content}")
    combined = "\n\n".join(sections)

    prompt = (
        "Synthesize the following agent outputs into a single coherent study result.\n\n"
        f"{combined}"
    )
    return manager.generate(prompt, system=SYSTEM)
