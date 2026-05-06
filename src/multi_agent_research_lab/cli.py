"""Command-line entrypoint for the lab starter."""

import logging
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.evaluation.benchmark import run_benchmark
from multi_agent_research_lab.evaluation.report import render_markdown_report
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow
from multi_agent_research_lab.observability.logging import configure_logging
from multi_agent_research_lab.observability.tracing import setup_tracing
from multi_agent_research_lab.services.llm_client import LLMClient

app = typer.Typer(help="Multi-Agent Research Lab starter CLI")
console = Console()
logger = logging.getLogger(__name__)


def _init() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    setup_tracing()


@app.command()
def baseline(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run a minimal single-agent baseline."""

    _init()
    console.print("[bold blue]Running single-agent baseline...[/bold blue]")

    request = ResearchQuery(query=query)
    state = ResearchState(request=request)

    # Simple single-agent implementation using LLM directly
    try:
        llm_client = LLMClient()

        system_prompt = """You are a research assistant. Answer the user's query with accurate, well-researched information.

Provide a comprehensive response that:
- Addresses the query directly
- Includes relevant facts and context
- Is well-organized and clear
- Is approximately 500 words unless specified otherwise"""

        user_prompt = f"Query: {query}\n\nProvide a comprehensive answer to this query."

        response = llm_client.complete(system_prompt, user_prompt)
        state.final_answer = response.content

        console.print(Panel.fit(state.final_answer, title="Single-Agent Baseline"))
        console.print(
            f"\n[dim]Tokens: {response.input_tokens} in, {response.output_tokens} out | "
            f"Cost: ${response.cost_usd:.4f}[/dim]"
        )

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(code=1) from e


@app.command("multi-agent")
def multi_agent(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run the multi-agent workflow."""

    _init()
    console.print("[bold blue]Running multi-agent workflow...[/bold blue]")

    state = ResearchState(request=ResearchQuery(query=query))
    workflow = MultiAgentWorkflow()

    try:
        result = workflow.run(state)

        # Display results
        console.print("\n[bold green]Workflow completed![/bold green]")
        console.print(f"Iterations: {result.iteration}")
        console.print(f"Route history: {' → '.join(result.route_history)}")

        if result.final_answer:
            console.print(Panel.fit(result.final_answer, title="Final Answer"))
        else:
            console.print("[yellow]No final answer generated[/yellow]")

        if result.errors:
            console.print(f"\n[red]Errors: {len(result.errors)}[/red]")
            for error in result.errors:
                console.print(f"  - {error}")

        # Show cost summary
        total_cost = sum(
            r.metadata.get("cost_usd", 0)
            for r in result.agent_results
            if r.metadata.get("cost_usd")
        )
        console.print(f"\n[dim]Total cost: ${total_cost:.4f}[/dim]")

    except StudentTodoError as exc:
        console.print(Panel.fit(str(exc), title="Expected TODO", style="yellow"))
        raise typer.Exit(code=2) from exc
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(code=1) from e


@app.command()
def benchmark(
    query: Annotated[
        str,
        typer.Option("--query", "-q", help="Research query"),
    ] = "Research GraphRAG state-of-the-art and write a 500-word summary",
    output: Annotated[
        Path,
        typer.Option("--output", "-o", help="Output markdown file"),
    ] = Path("reports/benchmark_report.md"),
) -> None:
    """Run benchmark comparing single-agent vs multi-agent."""

    _init()
    console.print("[bold blue]Running benchmark...[/bold blue]")

    metrics = []

    # Run single-agent baseline
    console.print("\n[cyan]1/2 Running single-agent baseline...[/cyan]")

    def single_agent_runner(q: str) -> ResearchState:
        request = ResearchQuery(query=q)
        state = ResearchState(request=request)
        llm_client = LLMClient()

        system_prompt = """You are a research assistant. Answer the user's query with accurate, well-researched information."""
        user_prompt = f"Query: {q}\n\nProvide a comprehensive answer."

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

    _, single_metrics = run_benchmark("single-agent", query, single_agent_runner)
    metrics.append(single_metrics)
    console.print(f"  ✓ Completed in {single_metrics.latency_seconds:.2f}s")

    # Run multi-agent workflow
    console.print("\n[cyan]2/2 Running multi-agent workflow...[/cyan]")

    def multi_agent_runner(q: str) -> ResearchState:
        state = ResearchState(request=ResearchQuery(query=q))
        workflow = MultiAgentWorkflow()
        return workflow.run(state)

    _, multi_metrics = run_benchmark("multi-agent", query, multi_agent_runner)
    metrics.append(multi_metrics)
    console.print(f"  ✓ Completed in {multi_metrics.latency_seconds:.2f}s")

    # Generate report
    console.print("\n[cyan]Generating report...[/cyan]")
    report = render_markdown_report(metrics)

    # Save report
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report)

    console.print("\n[bold green]✓ Benchmark complete![/bold green]")
    console.print(f"Report saved to: {output}")

    # Display summary
    console.print("\n[bold]Summary:[/bold]")
    console.print(
        f"  Single-agent: {single_metrics.latency_seconds:.2f}s, "
        f"${single_metrics.estimated_cost_usd:.4f}, "
        f"quality={single_metrics.quality_score:.1f}/10"
    )
    console.print(
        f"  Multi-agent:  {multi_metrics.latency_seconds:.2f}s, "
        f"${multi_metrics.estimated_cost_usd:.4f}, "
        f"quality={multi_metrics.quality_score:.1f}/10"
    )


if __name__ == "__main__":
    app()
