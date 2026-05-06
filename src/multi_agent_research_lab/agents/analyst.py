"""Analyst agent skeleton."""

import logging

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.errors import AgentExecutionError
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient

logger = logging.getLogger(__name__)


class AnalystAgent(BaseAgent):
    """Turns research notes into structured insights."""

    name = "analyst"

    def __init__(self) -> None:
        self.llm_client = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.analysis_notes`."""
        try:
            logger.info("AnalystAgent: analyzing research notes")

            if not state.research_notes:
                state.errors.append("AnalystAgent: No research notes to analyze")
                return state

            system_prompt = """You are a critical analyst. Your task is to analyze research notes and extract structured insights.

Focus on:
- Key claims and their supporting evidence
- Patterns, trends, and relationships
- Strengths and weaknesses of the evidence
- Gaps in information or conflicting viewpoints
- Important implications or conclusions

Provide a clear, analytical perspective that goes beyond summarization."""

            user_prompt = f"""Query: {state.request.query}

Research Notes:
{state.research_notes}

Analyze these research notes and provide structured insights. Identify key claims, evaluate evidence quality, note any patterns or contradictions, and highlight important implications."""

            response = self.llm_client.complete(system_prompt, user_prompt)
            state.analysis_notes = response.content

            # Record agent result
            state.agent_results.append(
                AgentResult(
                    agent=AgentName.ANALYST,
                    content=state.analysis_notes,
                    metadata={
                        "input_tokens": response.input_tokens,
                        "output_tokens": response.output_tokens,
                        "cost_usd": response.cost_usd,
                    },
                )
            )

            state.add_trace_event("analyst_completed", {})
            logger.info("AnalystAgent: completed analysis")

            return state

        except Exception as e:
            error_msg = f"AnalystAgent failed: {e}"
            logger.error(error_msg)
            state.errors.append(error_msg)
            raise AgentExecutionError(error_msg) from e
