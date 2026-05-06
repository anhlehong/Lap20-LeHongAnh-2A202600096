# Design Document - Multi-Agent Research System

**Author:** Le Hong Anh  
**Student ID:** 2A202600096  
**Date:** May 6, 2026

---

## Problem

**Task:** Build a research assistant that can handle complex queries like:
> "Research GraphRAG state-of-the-art and write a 500-word summary"

**Requirements:**
- Search for relevant information from multiple sources
- Analyze and synthesize findings
- Generate well-structured, cited answers
- Compare single-agent vs multi-agent approaches

---

## Why Multi-Agent?

### Single-Agent Limitations:
1. **Cognitive overload** - One agent must handle search, analysis, and writing simultaneously
2. **No specialization** - Cannot optimize prompts for different tasks
3. **Poor traceability** - Hard to debug which part failed
4. **Limited quality** - Generic approach vs specialized expertise

### Multi-Agent Benefits:
1. **Separation of concerns** - Each agent focuses on one task
2. **Specialized prompts** - Optimized for search, analysis, or writing
3. **Better debugging** - Clear trace of which agent did what
4. **Higher quality** - Specialized processing at each stage
5. **Parallel potential** - Independent agents can run concurrently (future)

---

## Agent Roles

| Agent | Responsibility | Input | Output | Failure Mode |
|-------|---------------|-------|--------|--------------|
| **Supervisor** | Route to appropriate worker based on state | ResearchState | Updated route_history | Infinite loop, wrong routing |
| **Researcher** | Search for sources and create research notes | Query + max_sources | sources + research_notes | No results, API failure |
| **Analyst** | Analyze research notes and extract insights | research_notes | analysis_notes | Shallow analysis, missing patterns |
| **Writer** | Synthesize final answer with citations | research_notes + analysis_notes + sources | final_answer | Poor structure, missing citations |

### Agent Interaction Flow:

```
User Query
    ↓
Supervisor (decides: researcher)
    ↓
Researcher (searches + synthesizes)
    ↓
Supervisor (decides: analyst)
    ↓
Analyst (analyzes + extracts insights)
    ↓
Supervisor (decides: writer)
    ↓
Writer (creates final answer)
    ↓
Supervisor (decides: done)
    ↓
Return final_answer
```

---

## Shared State

### ResearchState Fields:

| Field | Type | Purpose | Why Needed |
|-------|------|---------|------------|
| `request` | ResearchQuery | Original query + config | All agents need context |
| `iteration` | int | Current iteration count | Prevent infinite loops |
| `route_history` | list[str] | Agent execution sequence | Debugging + tracing |
| `sources` | list[SourceDocument] | Search results | Writer needs for citations |
| `research_notes` | str | Synthesized research | Analyst + Writer need this |
| `analysis_notes` | str | Critical analysis | Writer needs for depth |
| `final_answer` | str | Generated response | Final output |
| `agent_results` | list[AgentResult] | Per-agent outputs + metadata | Cost tracking + debugging |
| `trace` | list[dict] | Event log | Observability |
| `errors` | list[str] | Error messages | Error tracking |

### State Evolution Example:

```python
# Initial state
{
  "request": {"query": "What is GraphRAG?"},
  "iteration": 0,
  "route_history": [],
  "sources": [],
  "research_notes": None,
  ...
}

# After Researcher
{
  "iteration": 1,
  "route_history": ["researcher"],
  "sources": [5 documents],
  "research_notes": "GraphRAG combines...",
  ...
}

# After Analyst
{
  "iteration": 2,
  "route_history": ["researcher", "analyst"],
  "analysis_notes": "Key insights: 1) ...",
  ...
}

# After Writer
{
  "iteration": 3,
  "route_history": ["researcher", "analyst", "writer"],
  "final_answer": "## GraphRAG Overview...",
  ...
}
```

---

## Routing Policy

### Rule-Based Routing (Primary):

```python
def decide_next_route(state):
    # Check max iterations first
    if state.iteration >= MAX_ITERATIONS:
        return "done"
    
    # Sequential workflow
    if not state.research_notes:
        return "researcher"
    
    if state.research_notes and not state.analysis_notes:
        return "analyst"
    
    if state.research_notes and state.analysis_notes and not state.final_answer:
        return "writer"
    
    if state.final_answer:
        return "done"
    
    # Fallback to LLM-based routing
    return llm_decide_route(state)
```

### LangGraph Workflow:

```
┌─────────────┐
│  Supervisor │ ◄──────────┐
└──────┬──────┘            │
       │                   │
   ┌───┴────┬──────┬───────┤
   │        │      │       │
   ▼        ▼      ▼       │
┌──────┐ ┌────┐ ┌──────┐  │
│Resear│ │Anal│ │Writer│  │
│cher  │ │yst │ │      │  │
└───┬──┘ └─┬──┘ └───┬──┘  │
    │      │        │      │
    └──────┴────────┴──────┘
```

**Conditional Edges:**
- Supervisor → Researcher (if no research_notes)
- Supervisor → Analyst (if has research_notes, no analysis_notes)
- Supervisor → Writer (if has both notes, no final_answer)
- Supervisor → END (if final_answer exists OR max iterations)

---

## Guardrails

### 1. Max Iterations
- **Value:** 6 (configurable via `MAX_ITERATIONS`)
- **Purpose:** Prevent infinite routing loops
- **Implementation:** Check in Supervisor before routing
- **Failure behavior:** Force route to "done"

### 2. Timeout
- **Value:** 60 seconds (configurable via `TIMEOUT_SECONDS`)
- **Purpose:** Prevent hanging LLM calls
- **Implementation:** Pass to OpenAI client
- **Failure behavior:** Raise timeout error, caught by retry logic

### 3. Retry Logic
- **Attempts:** 3 with exponential backoff (2s, 4s, 8s)
- **Purpose:** Handle transient API failures
- **Implementation:** `@retry` decorator on LLMClient.complete()
- **Failure behavior:** Raise AgentExecutionError after 3 attempts

### 4. Fallback
- **Search fallback:** Mock results if Tavily API fails
- **Routing fallback:** LLM-based routing if rules insufficient
- **Purpose:** Graceful degradation
- **Implementation:** Try-except blocks with fallback logic

### 5. Validation
- **State validation:** Check required fields before agent execution
  - Analyst checks `if not state.research_notes`
  - Writer checks `if not state.research_notes and not state.analysis_notes`
- **Output validation:** Quality scoring in benchmark (0-10 scale)
- **Purpose:** Catch incomplete state early
- **Failure behavior:** Log error, return state unchanged

---

## Benchmark Plan

### Test Queries:

1. **Simple:** "What is GraphRAG?"
2. **Complex:** "Research GraphRAG state-of-the-art and write a 500-word summary"
3. **Comparative:** "Compare GraphRAG with traditional RAG approaches"

### Metrics:

| Metric | How to Measure | Expected Outcome |
|--------|----------------|------------------|
| **Latency** | Wall-clock time (start to finish) | Multi-agent: 20-30s, Single: 5-10s |
| **Cost** | Sum of token costs from all agents | Multi-agent: $0.002-0.005, Single: $0.0005-0.001 |
| **Quality** | 0-10 score based on:<br>- Has final answer (3pts)<br>- Has sources (2pts)<br>- Has research notes (1.5pts)<br>- Has analysis notes (1.5pts)<br>- Has citations (1pt)<br>- Penalty for errors (-0.5 each) | Multi-agent: 8-10, Single: 3-5 |
| **Source Count** | Number of sources retrieved | Multi-agent: 5, Single: 0 |
| **Iterations** | Number of agent calls | Multi-agent: 4-5, Single: 1 |

### Expected Results:

**Single-Agent:**
- ✅ Fast (6-10s)
- ✅ Cheap ($0.0005)
- ❌ Lower quality (4/10)
- ❌ No sources
- ❌ No structured analysis

**Multi-Agent:**
- ❌ Slower (25-30s)
- ❌ More expensive ($0.0027)
- ✅ Higher quality (10/10)
- ✅ Multiple sources with citations
- ✅ Structured research + analysis + writing

### When to Use Each:

**Use Single-Agent:**
- Simple factual questions
- Speed is critical
- Budget constraints
- No citation requirements

**Use Multi-Agent:**
- Complex research tasks
- Quality over speed
- Need source attribution
- Require structured analysis
- Debugging/traceability important

---

## Tracing Strategy

### LangSmith Integration:

**Setup:**
```python
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = langsmith_key
os.environ["LANGCHAIN_PROJECT"] = "multi-agent-research-lab"
```

**What Gets Traced:**
- All LangGraph node executions
- LLM calls (prompts + responses)
- Token usage per call
- Latency per agent
- State transitions

**Trace URL Format:**
```
https://smith.langchain.com/o/default/projects/p/multi-agent-research-lab/r/{run_id}
```

### Local Logging:

**Structured Logs:**
- Agent start/completion
- Routing decisions
- Error messages
- Performance metrics

**Log Levels:**
- INFO: Agent transitions, routing
- WARNING: Fallbacks, max iterations
- ERROR: Failures, exceptions
- DEBUG: Detailed state changes

---

## Success Criteria

✅ **Functional:**
- All agents execute successfully
- Workflow completes without errors
- Final answer generated with citations

✅ **Quality:**
- Multi-agent quality score ≥ 8/10
- Single-agent quality score ≤ 5/10
- Clear quality improvement demonstrated

✅ **Observability:**
- LangSmith trace available
- All agent transitions logged
- Cost and latency tracked

✅ **Robustness:**
- Handles API failures gracefully
- Respects max iterations
- No infinite loops
- Proper error messages

---

## Conclusion

This design provides a production-ready multi-agent research system with:
- **Clear separation of concerns** across specialized agents
- **Robust guardrails** preventing common failure modes
- **Comprehensive observability** via LangSmith and logging
- **Measurable quality improvements** over single-agent baseline

The trade-off is increased latency and cost, making it suitable for complex research tasks where quality matters more than speed.
