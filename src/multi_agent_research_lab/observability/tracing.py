"""Tracing hooks.

This file intentionally avoids binding to one provider. Students can plug in LangSmith,
Langfuse, OpenTelemetry, or simple JSON traces.
"""

import logging
import os
from collections.abc import Iterator
from contextlib import contextmanager
from time import perf_counter
from typing import Any

logger = logging.getLogger(__name__)


@contextmanager
def trace_span(name: str, attributes: dict[str, Any] | None = None) -> Iterator[dict[str, Any]]:
    """Minimal span context with optional LangSmith integration."""

    started = perf_counter()
    span: dict[str, Any] = {"name": name, "attributes": attributes or {}, "duration_seconds": None}

    # Enable LangSmith tracing if API key is present
    langsmith_enabled = bool(os.getenv("LANGSMITH_API_KEY"))

    try:
        if langsmith_enabled:
            # LangSmith will automatically trace LangChain/LangGraph operations
            # when LANGSMITH_API_KEY and LANGSMITH_PROJECT are set
            logger.debug(f"Tracing span: {name} (LangSmith enabled)")
        else:
            logger.debug(f"Tracing span: {name} (local only)")

        yield span

    finally:
        span["duration_seconds"] = perf_counter() - started
        logger.debug(
            f"Span '{name}' completed in {span['duration_seconds']:.3f}s",
            extra={"span": span},
        )


def setup_tracing() -> None:
    """Initialize tracing providers based on environment variables."""
    from multi_agent_research_lab.core.config import get_settings

    settings = get_settings()
    langsmith_key = settings.langsmith_api_key
    langsmith_project = settings.langsmith_project

    if langsmith_key:
        # LangSmith tracing is automatically enabled via environment variables
        # No additional setup needed for LangChain/LangGraph
        logger.info(f"LangSmith tracing enabled for project: {langsmith_project}")

        # Set tracing environment variables
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = langsmith_key
        if langsmith_project:
            os.environ["LANGCHAIN_PROJECT"] = langsmith_project
    else:
        logger.info("LangSmith tracing disabled (no API key found)")

    # Langfuse integration (optional)
    langfuse_secret = os.getenv("LANGFUSE_SECRET_KEY")
    langfuse_public = os.getenv("LANGFUSE_PUBLIC_KEY")
    if langfuse_secret and langfuse_public:
        logger.info("Langfuse credentials detected (integration not fully implemented)")
        # Could add Langfuse callback handler here


def get_trace_url(run_id: str | None = None) -> str | None:
    """Get trace URL for the current run if available."""

    langsmith_project = os.getenv("LANGSMITH_PROJECT")
    if run_id and langsmith_project:
        return f"https://smith.langchain.com/o/default/projects/p/{langsmith_project}/r/{run_id}"

    return None
