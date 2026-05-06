from multi_agent_research_lab.agents import SupervisorAgent
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState


def test_supervisor_routes_correctly() -> None:
    """Test that supervisor agent routes correctly based on state."""
    state = ResearchState(request=ResearchQuery(query="Explain multi-agent systems"))

    # Supervisor should route to researcher first (no research notes yet)
    supervisor = SupervisorAgent()
    result = supervisor.run(state)

    assert result.iteration == 1
    assert len(result.route_history) == 1
    assert result.route_history[0] == "researcher"


def test_supervisor_respects_max_iterations() -> None:
    """Test that supervisor stops at max iterations."""
    state = ResearchState(request=ResearchQuery(query="Test query"))
    state.iteration = 10  # Set to high iteration

    supervisor = SupervisorAgent()
    result = supervisor.run(state)

    # Should route to 'done' when max iterations reached
    assert "done" in result.route_history
