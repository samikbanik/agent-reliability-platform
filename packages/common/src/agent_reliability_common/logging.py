"""Shared logging configuration."""

import logging

from agent_reliability_common.settings import get_settings


def configure_logging(service_name: str) -> None:
    """Configure a simple structured-enough stdout logger."""
    settings = get_settings()
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format=f"%(asctime)s %(levelname)s [{service_name}] %(name)s: %(message)s",
    )
