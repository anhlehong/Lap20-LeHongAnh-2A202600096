"""Supervisor / router skeleton."""

import logging

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.errors import AgentExecutionError
from multi_agent_research_lab.core.schemas import AgentName
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient

logger = logging.getLogger(__name__)


class SupervisorAgent(BaseAgent):
    """Decides which worker should run next and when to stop."""

    name = "supervisor"

    def __init__(self) -> None:
        self.llm_client = LLMClient()
        self.settings = get_settings()

    def run(self, state: ResearchState) -> ResearchState:
        """Update `state.route_history` with the next route."""
        try:
            logger.info(f"SupervisorAgent: routing (iteration {state.iteration})")

            # Check max iterations
            if state.iteration >= self.settings.max_iterations:
                logger.warning(f"Max iterations ({self.settings.max_iterations}) reached")
                state.record_route("done")
                return state

            # Determine next step based on current state
            next_route = self._decide_next_route(state)
            state.record_route(next_route)

            state.add_trace_event(
                "supervisor_routed", {"route": next_route, "iteration": state.iteration}
            )

            logger.info(f"SupervisorAgent: routed to '{next_route}'")
            return state

        except Exception as e:
            error_msg = f"SupervisorAgent failed: {e}"
            logger.error(error_msg)
            state.errors.append(error_msg)
            raise AgentExecutionError(error_msg) from e

    def _decide_next_route(self, state: ResearchState) -> str:
        """Decide which agent should run next based on current state."""

        # Simple rule-based routing for efficiency
        # For more complex routing, could use LLM

        # If no research notes, need researcher
        if not state.research_notes:
            return AgentName.RESEARCHER

        # If have research but no analysis, need analyst
        if state.research_notes and not state.analysis_notes:
            return AgentName.ANALYST

        # If have research and analysis but no final answer, need writer
        if state.research_notes and state.analysis_notes and not state.final_answer:
            return AgentName.WRITER

        # If we have final answer, we're done
        if state.final_answer:
            return "done"

        # Fallback: use LLM to decide
        return self._llm_based_routing(state)

    def _llm_based_routing(self, state: ResearchState) -> str:
        """Use LLM to decide next route when rules are insufficient."""

        system_prompt = """You are a supervisor agent coordinating a research workflow. Based on the current state, decide which agent should run next.

Available agents:
- researcher: Searches for information and creates research notes
- analyst: Analyzes research notes and extracts insights
- writer: Creates final answer from research and analysis
- done: Workflow is complete

Respond with ONLY the agent name, nothing else."""

        state_summary = f"""Query: {state.request.query}
Iteration: {state.iteration}
Route history: {", ".join(state.route_history)}
Has research notes: {bool(state.research_notes)}
Has analysis notes: {bool(state.analysis_notes)}
Has final answer: {bool(state.final_answer)}
Sources count: {len(state.sources)}
Errors: {len(state.errors)}"""

        user_prompt = f"""{state_summary}

Which agent should run next?"""

        try:
            response = self.llm_client.complete(system_prompt, user_prompt)
            route = response.content.strip().lower()

            # Validate route
            valid_routes = [
                AgentName.RESEARCHER,
                AgentName.ANALYST,
                AgentName.WRITER,
                "done",
            ]
            if route in valid_routes:
                return route

            logger.warning(f"Invalid route from LLM: {route}, defaulting to 'done'")
            return "done"

        except Exception as e:
            logger.error(f"LLM routing failed: {e}, defaulting to 'done'")
            return "done"
