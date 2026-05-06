"""Researcher agent skeleton."""

import logging

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.errors import AgentExecutionError
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.services.search_client import SearchClient

logger = logging.getLogger(__name__)


class ResearcherAgent(BaseAgent):
    """Collects sources and creates concise research notes."""

    name = "researcher"

    def __init__(self) -> None:
        self.search_client = SearchClient()
        self.llm_client = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.sources` and `state.research_notes`."""
        try:
            logger.info(f"ResearcherAgent: searching for '{state.request.query}'")

            # Search for relevant sources
            sources = self.search_client.search(
                query=state.request.query, max_results=state.request.max_sources
            )

            if not sources:
                state.errors.append("ResearcherAgent: No sources found")
                return state

            state.sources = sources

            # Create research notes using LLM
            sources_text = "\n\n".join(
                [
                    f"Source {i + 1}: {s.title}\nURL: {s.url}\nContent: {s.snippet}"
                    for i, s in enumerate(sources)
                ]
            )

            system_prompt = """You are a research assistant. Your task is to synthesize information from multiple sources into concise, well-organized research notes.

Focus on:
- Key facts and findings
- Important concepts and definitions
- Notable trends or patterns
- Credible evidence and data points

Keep notes clear, factual, and well-structured."""

            user_prompt = f"""Query: {state.request.query}

Sources:
{sources_text}

Create comprehensive research notes that synthesize the key information from these sources. Include source references (e.g., [Source 1], [Source 2]) for important claims."""

            response = self.llm_client.complete(system_prompt, user_prompt)
            state.research_notes = response.content

            # Record agent result
            state.agent_results.append(
                AgentResult(
                    agent=AgentName.RESEARCHER,
                    content=state.research_notes,
                    metadata={
                        "sources_count": len(sources),
                        "input_tokens": response.input_tokens,
                        "output_tokens": response.output_tokens,
                        "cost_usd": response.cost_usd,
                    },
                )
            )

            state.add_trace_event("researcher_completed", {"sources": len(sources)})
            logger.info(f"ResearcherAgent: completed with {len(sources)} sources")

            return state

        except Exception as e:
            error_msg = f"ResearcherAgent failed: {e}"
            logger.error(error_msg)
            state.errors.append(error_msg)
            raise AgentExecutionError(error_msg) from e
