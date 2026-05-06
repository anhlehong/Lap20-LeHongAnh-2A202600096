"""Benchmark skeleton for single-agent vs multi-agent."""

import logging
from collections.abc import Callable
from time import perf_counter

from multi_agent_research_lab.core.schemas import BenchmarkMetrics
from multi_agent_research_lab.core.state import ResearchState

logger = logging.getLogger(__name__)

Runner = Callable[[str], ResearchState]


def run_benchmark(
    run_name: str, query: str, runner: Runner
) -> tuple[ResearchState, BenchmarkMetrics]:
    """Measure latency, cost, and quality metrics for a research run."""

    logger.info(f"Starting benchmark: {run_name}")
    started = perf_counter()

    try:
        state = runner(query)
        latency = perf_counter() - started

        # Calculate total cost from agent results
        total_cost = 0.0
        for result in state.agent_results:
            if result.metadata.get("cost_usd"):
                total_cost += result.metadata["cost_usd"]

        # Calculate quality score based on multiple factors
        quality_score = _calculate_quality_score(state)

        # Generate notes
        notes = _generate_notes(state)

        metrics = BenchmarkMetrics(
            run_name=run_name,
            latency_seconds=latency,
            estimated_cost_usd=total_cost if total_cost > 0 else None,
            quality_score=quality_score,
            notes=notes,
        )

        logger.info(
            f"Benchmark completed: {run_name} - "
            f"latency={latency:.2f}s, cost=${total_cost:.4f}, quality={quality_score:.1f}"
        )

        return state, metrics

    except Exception as e:
        latency = perf_counter() - started
        logger.error(f"Benchmark failed: {run_name} - {e}")

        metrics = BenchmarkMetrics(
            run_name=run_name,
            latency_seconds=latency,
            estimated_cost_usd=None,
            quality_score=0.0,
            notes=f"Failed: {str(e)[:100]}",
        )

        # Create empty state with error
        from multi_agent_research_lab.core.schemas import ResearchQuery

        state = ResearchState(request=ResearchQuery(query=query))
        state.errors.append(str(e))

        return state, metrics


def _calculate_quality_score(state: ResearchState) -> float:
    """Calculate quality score (0-10) based on multiple factors."""

    score = 0.0

    # Has final answer (3 points)
    if state.final_answer:
        score += 3.0
        # Bonus for length (reasonable answer should be substantial)
        if len(state.final_answer) > 200:
            score += 1.0

    # Has sources (2 points)
    if state.sources:
        score += 2.0
        # Bonus for multiple sources
        if len(state.sources) >= 3:
            score += 0.5

    # Has research notes (1.5 points)
    if state.research_notes:
        score += 1.5

    # Has analysis notes (1.5 points)
    if state.analysis_notes:
        score += 1.5

    # Penalty for errors (up to -2 points)
    if state.errors:
        score -= min(len(state.errors) * 0.5, 2.0)

    # Bonus for citations in final answer (1 point)
    if state.final_answer and "[Source" in state.final_answer:
        score += 1.0

    # Ensure score is between 0 and 10
    return max(0.0, min(10.0, score))


def _generate_notes(state: ResearchState) -> str:
    """Generate summary notes about the run."""

    notes_parts = []

    if state.errors:
        notes_parts.append(f"{len(state.errors)} errors")

    notes_parts.append(f"{len(state.sources)} sources")
    notes_parts.append(f"{state.iteration} iterations")

    if state.route_history:
        agents_used = set(state.route_history) - {"done"}
        notes_parts.append(f"agents: {', '.join(sorted(agents_used))}")

    return "; ".join(notes_parts)
