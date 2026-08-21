#!/usr/bin/env python3
"""
Study Forge — entry point.

Orchestrates the local-first study-material processing pipeline.
Does not contain business logic; that lives in the package modules.
"""

from __future__ import annotations

import sys
from pathlib import Path

from config.settings import Settings
from pipeline.processor import process_input_folder
from utils.logging import setup_logging, get_logger


def main() -> int:
    settings = Settings.load()
    setup_logging(settings.log_level)
    logger = get_logger(__name__)

    logger.info("Study Forge starting")
    logger.info("Local provider: %s | Model: %s", settings.local_provider, settings.local_model)

    input_path = Path(settings.input_folder)
    if not input_path.exists():
        logger.error("Input folder does not exist: %s", input_path)
        logger.info("Create the folder and place PDF/DOCX/PPTX files inside it.")
        return 1

    try:
        results = process_input_folder(settings)
        logger.info("Processing finished. Files handled: %d", len(results))
        return 0
    except KeyboardInterrupt:
        logger.warning("Interrupted by user")
        return 130
    except Exception as exc:
        logger.exception("Unhandled error: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
