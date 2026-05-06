"""Writer agent skeleton."""

import logging

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.errors import AgentExecutionError
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient

logger = logging.getLogger(__name__)


class WriterAgent(BaseAgent):
    """Produces final answer from research and analysis notes."""

    name = "writer"

    def __init__(self) -> None:
        self.llm_client = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.final_answer`."""
        try:
            logger.info("WriterAgent: creating final answer")

            if not state.research_notes and not state.analysis_notes:
                state.errors.append("WriterAgent: No research or analysis notes available")
                return state

            # Build context from available information
            context_parts = []

            if state.research_notes:
                context_parts.append(f"Research Notes:\n{state.research_notes}")

            if state.analysis_notes:
                context_parts.append(f"\nAnalysis:\n{state.analysis_notes}")

            if state.sources:
                sources_list = "\n".join([f"- {s.title}: {s.url}" for s in state.sources if s.url])
                context_parts.append(f"\nSources:\n{sources_list}")

            context = "\n\n".join(context_parts)

            system_prompt = f"""You are a technical writer creating content for {state.request.audience}. Your task is to synthesize research and analysis into a clear, well-structured answer.

Requirements:
- Write in a clear, engaging style appropriate for the audience
- Include citations to sources using [Source N] format
- Organize information logically with clear sections
- Balance depth with readability
- Highlight key insights and takeaways
- Maintain factual accuracy

Target length: approximately 500 words unless the query specifies otherwise."""

            user_prompt = f"""Query: {state.request.query}

{context}

Write a comprehensive answer to the query based on the research and analysis provided. Include proper citations and organize the content clearly."""

            response = self.llm_client.complete(system_prompt, user_prompt)
            state.final_answer = response.content

            # Record agent result
            state.agent_results.append(
                AgentResult(
                    agent=AgentName.WRITER,
                    content=state.final_answer,
                    metadata={
                        "input_tokens": response.input_tokens,
                        "output_tokens": response.output_tokens,
                        "cost_usd": response.cost_usd,
                    },
                )
            )

            state.add_trace_event("writer_completed", {})
            logger.info("WriterAgent: completed final answer")

            return state

        except Exception as e:
            error_msg = f"WriterAgent failed: {e}"
            logger.error(error_msg)
            state.errors.append(error_msg)
            raise AgentExecutionError(error_msg) from e
