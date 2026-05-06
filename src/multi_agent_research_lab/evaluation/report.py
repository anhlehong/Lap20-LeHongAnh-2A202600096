"""Benchmark report rendering."""

from datetime import datetime

from multi_agent_research_lab.core.schemas import BenchmarkMetrics


def render_markdown_report(metrics: list[BenchmarkMetrics]) -> str:
    """Render benchmark metrics to markdown with detailed analysis."""

    lines = [
        "# Multi-Agent Research Lab - Benchmark Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Summary",
        "",
    ]

    # Summary statistics
    if metrics:
        avg_latency = sum(m.latency_seconds for m in metrics) / len(metrics)
        total_cost = sum(m.estimated_cost_usd or 0 for m in metrics)
        avg_quality = sum(m.quality_score or 0 for m in metrics) / len(metrics)

        lines.extend(
            [
                f"- **Total Runs:** {len(metrics)}",
                f"- **Average Latency:** {avg_latency:.2f}s",
                f"- **Total Cost:** ${total_cost:.4f}",
                f"- **Average Quality Score:** {avg_quality:.1f}/10",
                "",
            ]
        )

    # Detailed results table
    lines.extend(
        [
            "## Detailed Results",
            "",
            "| Run | Latency (s) | Cost (USD) | Quality | Notes |",
            "|---|---:|---:|---:|---|",
        ]
    )

    for item in metrics:
        cost = "" if item.estimated_cost_usd is None else f"${item.estimated_cost_usd:.4f}"
        quality = "" if item.quality_score is None else f"{item.quality_score:.1f}/10"
        notes = item.notes.replace("|", "\\|")  # Escape pipes in notes
        lines.append(
            f"| {item.run_name} | {item.latency_seconds:.2f} | {cost} | {quality} | {notes} |"
        )

    lines.extend(["", "## Analysis", ""])

    # Compare single-agent vs multi-agent if both present
    single_agent = next((m for m in metrics if "single" in m.run_name.lower()), None)
    multi_agent = next((m for m in metrics if "multi" in m.run_name.lower()), None)

    if single_agent and multi_agent:
        lines.extend(
            [
                "### Single-Agent vs Multi-Agent Comparison",
                "",
                "**Latency:**",
                f"- Single-agent: {single_agent.latency_seconds:.2f}s",
                f"- Multi-agent: {multi_agent.latency_seconds:.2f}s",
                f"- Difference: {multi_agent.latency_seconds - single_agent.latency_seconds:+.2f}s ({((multi_agent.latency_seconds / single_agent.latency_seconds - 1) * 100):+.1f}%)",
                "",
            ]
        )

        if single_agent.estimated_cost_usd and multi_agent.estimated_cost_usd:
            lines.extend(
                [
                    "**Cost:**",
                    f"- Single-agent: ${single_agent.estimated_cost_usd:.4f}",
                    f"- Multi-agent: ${multi_agent.estimated_cost_usd:.4f}",
                    f"- Difference: ${multi_agent.estimated_cost_usd - single_agent.estimated_cost_usd:+.4f} ({((multi_agent.estimated_cost_usd / single_agent.estimated_cost_usd - 1) * 100):+.1f}%)",
                    "",
                ]
            )

        if single_agent.quality_score and multi_agent.quality_score:
            lines.extend(
                [
                    "**Quality:**",
                    f"- Single-agent: {single_agent.quality_score:.1f}/10",
                    f"- Multi-agent: {multi_agent.quality_score:.1f}/10",
                    f"- Difference: {multi_agent.quality_score - single_agent.quality_score:+.1f}",
                    "",
                ]
            )

    lines.extend(
        [
            "## Observations",
            "",
            "### Strengths",
            "- Multi-agent system provides structured workflow with specialized roles",
            "- Clear separation of concerns: research, analysis, and writing",
            "- Traceable decision-making through supervisor routing",
            "",
            "### Trade-offs",
            "- Multi-agent approach typically has higher latency due to multiple LLM calls",
            "- Increased cost from additional agent interactions",
            "- Potential for improved quality through specialized processing",
            "",
            "### Recommendations",
            "- Use multi-agent for complex research tasks requiring deep analysis",
            "- Use single-agent for simple queries where speed is critical",
            "- Consider hybrid approaches for specific use cases",
            "",
        ]
    )

    return "\n".join(lines) + "\n"
