"""LangGraph workflow skeleton."""

import logging
from typing import Any, Literal

from langgraph.graph import END, StateGraph

from multi_agent_research_lab.agents.analyst import AnalystAgent
from multi_agent_research_lab.agents.researcher import ResearcherAgent
from multi_agent_research_lab.agents.supervisor import SupervisorAgent
from multi_agent_research_lab.agents.writer import WriterAgent
from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.schemas import AgentName
from multi_agent_research_lab.core.state import ResearchState

logger = logging.getLogger(__name__)


class MultiAgentWorkflow:
    """Builds and runs the multi-agent graph.

    Keep orchestration here; keep agent internals in `agents/`.
    """

    def __init__(self) -> None:
        self.supervisor = SupervisorAgent()
        self.researcher = ResearcherAgent()
        self.analyst = AnalystAgent()
        self.writer = WriterAgent()
        self.settings = get_settings()

    def build(self) -> StateGraph:
        """Create a LangGraph graph with supervisor-worker pattern."""

        # Create graph with ResearchState
        workflow = StateGraph(ResearchState)

        # Add nodes
        workflow.add_node("supervisor", self._supervisor_node)
        workflow.add_node(AgentName.RESEARCHER, self._researcher_node)
        workflow.add_node(AgentName.ANALYST, self._analyst_node)
        workflow.add_node(AgentName.WRITER, self._writer_node)

        # Set entry point
        workflow.set_entry_point("supervisor")

        # Add conditional edges from supervisor to workers
        workflow.add_conditional_edges(
            "supervisor",
            self._route_decision,
            {
                AgentName.RESEARCHER: AgentName.RESEARCHER,
                AgentName.ANALYST: AgentName.ANALYST,
                AgentName.WRITER: AgentName.WRITER,
                "done": END,
            },
        )

        # Workers return to supervisor
        workflow.add_edge(AgentName.RESEARCHER, "supervisor")
        workflow.add_edge(AgentName.ANALYST, "supervisor")
        workflow.add_edge(AgentName.WRITER, "supervisor")

        return workflow

    def run(self, state: ResearchState) -> ResearchState:
        """Execute the graph and return final state."""
        try:
            logger.info("Starting multi-agent workflow")

            # Build and compile graph
            workflow = self.build()
            app = workflow.compile()

            # Convert state to dict for LangGraph
            state_dict = state.model_dump()

            # Run the graph
            result = app.invoke(state_dict)

            # Convert result back to ResearchState
            final_state = ResearchState(**result)

            logger.info(
                f"Workflow completed: {len(final_state.route_history)} steps, "
                f"{len(final_state.errors)} errors"
            )

            return final_state

        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            state.errors.append(f"Workflow failed: {e}")
            return state

    def _supervisor_node(self, state: ResearchState) -> dict[str, Any]:
        """Supervisor node wrapper."""
        updated_state = self.supervisor.run(state)
        return updated_state.model_dump()

    def _researcher_node(self, state: ResearchState) -> dict[str, Any]:
        """Researcher node wrapper."""
        updated_state = self.researcher.run(state)
        return updated_state.model_dump()

    def _analyst_node(self, state: ResearchState) -> dict[str, Any]:
        """Analyst node wrapper."""
        updated_state = self.analyst.run(state)
        return updated_state.model_dump()

    def _writer_node(self, state: ResearchState) -> dict[str, Any]:
        """Writer node wrapper."""
        updated_state = self.writer.run(state)
        return updated_state.model_dump()

    def _route_decision(
        self, state: ResearchState
    ) -> Literal["researcher", "analyst", "writer", "done"]:
        """Extract routing decision from state."""
        if not state.route_history:
            return "done"

        last_route = state.route_history[-1]

        # Validate route
        if last_route in [AgentName.RESEARCHER, AgentName.ANALYST, AgentName.WRITER, "done"]:
            return last_route  # type: ignore

        logger.warning(f"Invalid route '{last_route}', defaulting to 'done'")
        return "done"
