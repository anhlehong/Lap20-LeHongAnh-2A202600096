#!/usr/bin/env python3
"""Run benchmark on multiple research queries."""

import json
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.evaluation.benchmark import run_benchmark
from multi_agent_research_lab.evaluation.report import render_markdown_report
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow
from multi_agent_research_lab.observability.logging import configure_logging
from multi_agent_research_lab.observability.tracing import setup_tracing
from multi_agent_research_lab.services.llm_client import LLMClient

# Load environment
load_dotenv()
configure_logging("INFO")
setup_tracing()

# Test queries
QUERIES = [
    "Research GraphRAG state-of-the-art and write a 500-word summary",
    "What are the key differences between RAG and GraphRAG?",
    "Explain how knowledge graphs improve retrieval-augmented generation",
    "What are the main challenges in implementing GraphRAG systems?",
    "Compare GraphRAG with traditional vector search approaches",
]


def single_agent_runner(query: str) -> ResearchState:
    """Single-agent baseline."""
    request = ResearchQuery(query=query)
    state = ResearchState(request=request)
    llm_client = LLMClient()

    system_prompt = """You are a research assistant. Answer the user's query with accurate, well-researched information."""
    user_prompt = f"Query: {query}\n\nProvide a comprehensive answer."

    response = llm_client.complete(system_prompt, user_prompt)
    state.final_answer = response.content

    from multi_agent_research_lab.core.schemas import AgentName, AgentResult

    state.agent_results.append(
        AgentResult(
            agent=AgentName.WRITER,
            content=response.content,
            metadata={
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens,
                "cost_usd": response.cost_usd,
            },
        )
    )
    return state


def multi_agent_runner(query: str) -> ResearchState:
    """Multi-agent workflow."""
    state = ResearchState(request=ResearchQuery(query=query))
    workflow = MultiAgentWorkflow()
    return workflow.run(state)


def main():
    """Run benchmarks on multiple queries."""
    print("\n" + "=" * 100)
    print(f"  Multi-Query Benchmark - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 100 + "\n")

    all_metrics = []
    results_detail = []

    for i, query in enumerate(QUERIES, 1):
        print(f"\n{'=' * 100}")
        print(f"Query {i}/{len(QUERIES)}: {query[:60]}...")
        print("=" * 100)

        # Single-agent
        print(f"\n[{i}.1] Running single-agent...")
        _, single_metrics = run_benchmark(f"Q{i}-single", query, single_agent_runner)
        all_metrics.append(single_metrics)
        print(f"  ✓ Completed: {single_metrics.latency_seconds:.2f}s, ${single_metrics.estimated_cost_usd:.4f}, quality={single_metrics.quality_score:.1f}/10")

        # Multi-agent
        print(f"\n[{i}.2] Running multi-agent...")
        _, multi_metrics = run_benchmark(f"Q{i}-multi", query, multi_agent_runner)
        all_metrics.append(multi_metrics)
        print(f"  ✓ Completed: {multi_metrics.latency_seconds:.2f}s, ${multi_metrics.estimated_cost_usd:.4f}, quality={multi_metrics.quality_score:.1f}/10")

        # Store details
        results_detail.append(
            {
                "query": query,
                "single": {
                    "latency": single_metrics.latency_seconds,
                    "cost": single_metrics.estimated_cost_usd,
                    "quality": single_metrics.quality_score,
                },
                "multi": {
                    "latency": multi_metrics.latency_seconds,
                    "cost": multi_metrics.estimated_cost_usd,
                    "quality": multi_metrics.quality_score,
                },
            }
        )

    # Generate report
    print("\n" + "=" * 100)
    print("Generating comprehensive report...")
    print("=" * 100 + "\n")

    report = render_markdown_report(all_metrics)

    # Save report
    output_path = Path("reports/multi_query_benchmark.md")
    output_path.write_text(report)

    # Save JSON details
    json_path = Path("reports/benchmark_results.json")
    json_path.write_text(json.dumps(results_detail, indent=2))

    print(f"✅ Report saved to: {output_path}")
    print(f"✅ JSON data saved to: {json_path}")

    # Summary
    print("\n" + "=" * 100)
    print("SUMMARY")
    print("=" * 100 + "\n")

    single_metrics_list = [m for m in all_metrics if "single" in m.run_name]
    multi_metrics_list = [m for m in all_metrics if "multi" in m.run_name]

    avg_single_latency = sum(m.latency_seconds for m in single_metrics_list) / len(
        single_metrics_list
    )
    avg_multi_latency = sum(m.latency_seconds for m in multi_metrics_list) / len(
        multi_metrics_list
    )

    avg_single_cost = sum(m.estimated_cost_usd or 0 for m in single_metrics_list) / len(
        single_metrics_list
    )
    avg_multi_cost = sum(m.estimated_cost_usd or 0 for m in multi_metrics_list) / len(
        multi_metrics_list
    )

    avg_single_quality = sum(m.quality_score or 0 for m in single_metrics_list) / len(
        single_metrics_list
    )
    avg_multi_quality = sum(m.quality_score or 0 for m in multi_metrics_list) / len(
        multi_metrics_list
    )

    print(f"Queries tested: {len(QUERIES)}")
    print(f"\nAverage Latency:")
    print(f"  Single-agent: {avg_single_latency:.2f}s")
    print(f"  Multi-agent:  {avg_multi_latency:.2f}s")
    print(f"  Difference:   {avg_multi_latency - avg_single_latency:+.2f}s ({((avg_multi_latency / avg_single_latency - 1) * 100):+.1f}%)")

    print(f"\nAverage Cost:")
    print(f"  Single-agent: ${avg_single_cost:.4f}")
    print(f"  Multi-agent:  ${avg_multi_cost:.4f}")
    print(f"  Difference:   ${avg_multi_cost - avg_single_cost:+.4f} ({((avg_multi_cost / avg_single_cost - 1) * 100):+.1f}%)")

    print(f"\nAverage Quality:")
    print(f"  Single-agent: {avg_single_quality:.1f}/10")
    print(f"  Multi-agent:  {avg_multi_quality:.1f}/10")
    print(f"  Difference:   {avg_multi_quality - avg_single_quality:+.1f}")

    print("\n" + "=" * 100 + "\n")


if __name__ == "__main__":
    main()
