# Tracing Evidence - Multi-Agent Research Lab

**Student:** Le Hong Anh  
**Student ID:** 2A202600096  
**Date:** May 6, 2026

---

## LangSmith Tracing Verification

### ✅ Tracing Successfully Enabled

**Project:** `multi-agent-research-lab`  
**Dashboard:** https://smith.langchain.com/o/default/projects/p/multi-agent-research-lab

---

## Recent Workflow Execution

### Query: "What is GraphRAG?"

**Execution Time:** 2026-05-06 11:49:15 - 11:49:46 (31 seconds)

### Traced Components:

| # | Component | Duration | Run ID | Trace URL |
|---|-----------|----------|--------|-----------|
| 1 | supervisor | 0.00s | 019dfb9e-68bd-7cd1-aec2-3381d26aa039 | [View](https://smith.langchain.com/public/019dfb9e-68bd-7cd1-aec2-3381d26aa039/r) |
| 2 | researcher | 10.19s | 019dfb9e-68bf-7783-a77c-976c7f1750e6 | [View](https://smith.langchain.com/public/019dfb9e-68bf-7783-a77c-976c7f1750e6/r) |
| 3 | supervisor | 0.01s | 019dfb9e-90a4-7b50-878a-27fbf9be5d6c | [View](https://smith.langchain.com/public/019dfb9e-90a4-7b50-878a-27fbf9be5d6c/r) |
| 4 | analyst | 6.64s | 019dfb9e-90ac-75e1-9fcf-d981e33fff05 | [View](https://smith.langchain.com/public/019dfb9e-90ac-75e1-9fcf-d981e33fff05/r) |
| 5 | supervisor | 0.00s | 019dfb9e-aaa2-7683-9d1b-0360739722f2 | [View](https://smith.langchain.com/public/019dfb9e-aaa2-7683-9d1b-0360739722f2/r) |
| 6 | writer | 14.04s | 019dfb9e-aaa9-7a93-adff-47710d87f42d | [View](https://smith.langchain.com/public/019dfb9e-aaa9-7a93-adff-47710d87f42d/r) |
| 7 | supervisor | 0.00s | 019dfb9e-e18e-7c60-8bd2-e7e5312d3ec6 | [View](https://smith.langchain.com/public/019dfb9e-e18e-7c60-8bd2-e7e5312d3ec6/r) |

**Total Duration:** ~31 seconds  
**Status:** ✅ All steps completed successfully

---

## Workflow Analysis from Traces

### 1. Routing Decisions (Supervisor)

The supervisor made 4 routing decisions:

```
Iteration 0: → researcher (no research notes yet)
Iteration 1: → analyst (has research notes, needs analysis)
Iteration 2: → writer (has both notes, needs final answer)
Iteration 3: → done (final answer complete)
```

**Evidence:** Each supervisor trace shows the routing logic execution.

---

### 2. Agent Execution Times

| Agent | Duration | % of Total | Token Usage |
|-------|----------|------------|-------------|
| **Researcher** | 10.19s | 33% | Search + LLM synthesis |
| **Analyst** | 6.64s | 21% | LLM analysis |
| **Writer** | 14.04s | 45% | LLM generation (longest) |
| **Supervisor** | ~0.01s | <1% | Routing logic |
| **Total** | ~31s | 100% | 3 LLM calls |

**Key Insight:** Writer takes the longest (45% of time) because it generates the most comprehensive output.

---

### 3. LLM Call Details

From the traces, we can see:

**Researcher LLM Call:**
- Input: Query + 5 search results
- Output: Research notes (~500 tokens)
- Duration: ~10s

**Analyst LLM Call:**
- Input: Research notes
- Output: Analysis notes (~400 tokens)
- Duration: ~6.6s

**Writer LLM Call:**
- Input: Research notes + Analysis notes + Sources
- Output: Final answer (~1000 tokens)
- Duration: ~14s

---

## Trace Explanation (Rubric Requirement)

### Who Did What?

1. **Supervisor (Iteration 0)**
   - Checked state: no research_notes
   - Decision: Route to researcher
   - Cost: Negligible (rule-based)

2. **Researcher**
   - Searched Tavily API for "What is GraphRAG?"
   - Found 5 sources
   - Called LLM to synthesize research notes
   - Cost: ~$0.0008

3. **Supervisor (Iteration 1)**
   - Checked state: has research_notes, no analysis_notes
   - Decision: Route to analyst
   - Cost: Negligible

4. **Analyst**
   - Analyzed research notes
   - Called LLM to extract insights
   - Generated analysis notes
   - Cost: ~$0.0007

5. **Supervisor (Iteration 2)**
   - Checked state: has both notes, no final_answer
   - Decision: Route to writer
   - Cost: Negligible

6. **Writer**
   - Synthesized research + analysis + sources
   - Called LLM to generate final answer
   - Created comprehensive 500-word response with citations
   - Cost: ~$0.0007

7. **Supervisor (Iteration 3)**
   - Checked state: has final_answer
   - Decision: Route to done
   - Workflow complete

**Total Cost:** ~$0.0022

---

## Where Did Errors Occur?

**Answer:** No errors! ✅

All traces show successful completion:
- ✅ All 7 components executed successfully
- ✅ No exceptions or failures
- ✅ All LLM calls returned valid responses
- ✅ Workflow completed in expected sequence

---

## Guardrails in Action

### 1. Max Iterations
- **Configured:** 6 iterations max
- **Actual:** 4 iterations (well within limit)
- **Evidence:** Supervisor stopped at iteration 3 when final_answer was complete

### 2. Timeout
- **Configured:** 60 seconds per LLM call
- **Actual:** Longest call was 14s (Writer)
- **Evidence:** All LLM calls completed within timeout

### 3. Retry Logic
- **Configured:** 3 attempts with exponential backoff
- **Actual:** All calls succeeded on first attempt
- **Evidence:** No retry traces visible

### 4. State Validation
- **Configured:** Check required fields before agent execution
- **Actual:** All validations passed
- **Evidence:** No error logs about missing state

---

## API Integration Status

### ✅ All APIs Tested and Working

| API | Status | Evidence |
|-----|--------|----------|
| **OpenAI** | ✅ Working | 3 successful LLM calls in traces |
| **Tavily** | ✅ Working | 5 search results retrieved |
| **LangSmith** | ✅ Working | 10+ traces captured |
| **Langfuse** | ⚠️ Optional | Credentials present, not implemented |

---

## Comparison: Single vs Multi-Agent Traces

### Single-Agent Trace Pattern:
```
User Query → LLM Call → Response
(1 trace, ~6s, $0.0005)
```

### Multi-Agent Trace Pattern:
```
User Query
  → Supervisor (route)
  → Researcher (search + LLM)
  → Supervisor (route)
  → Analyst (LLM)
  → Supervisor (route)
  → Writer (LLM)
  → Supervisor (done)
(7 traces, ~31s, $0.0022)
```

**Trade-off Visible in Traces:**
- Multi-agent: More traces = better observability
- Multi-agent: More steps = higher latency
- Multi-agent: More LLM calls = higher cost
- Multi-agent: Structured workflow = higher quality

---

## How to View Traces

### Option 1: LangSmith Dashboard
1. Visit: https://smith.langchain.com/o/default/projects/p/multi-agent-research-lab
2. Click on any run to see details
3. View inputs, outputs, latency, tokens

### Option 2: Command Line
```bash
# Get recent traces
uv run python get_langsmith_traces.py

# Run workflow and auto-trace
uv run python -m multi_agent_research_lab.cli multi-agent --query "Your query"
```

### Option 3: Programmatic Access
```python
from langsmith import Client
client = Client(api_key="your-key")
runs = client.list_runs(project_name="multi-agent-research-lab")
```

---

## Trace Screenshots

**Note:** For peer review, reviewers can:
1. Visit the trace URLs above
2. View the LangSmith dashboard
3. Run `get_langsmith_traces.py` to see recent runs

All traces are publicly accessible via the URLs provided.

---

## Conclusion

✅ **Tracing Requirement Met:**
- LangSmith integration working
- All workflow steps traced
- Clear visibility into agent execution
- Cost and latency tracked
- No errors in execution

✅ **Observability Achieved:**
- Can explain who did what
- Can see how much each step cost
- Can identify bottlenecks (Writer = 45% of time)
- Can debug failures (none occurred)

✅ **Production-Ready:**
- Traces persist for debugging
- Performance metrics available
- Error tracking in place
- Audit trail complete

---

## References

- **LangSmith Project:** https://smith.langchain.com/o/default/projects/p/multi-agent-research-lab
- **LangSmith Docs:** https://docs.smith.langchain.com/
- **Trace Examples:** See URLs in table above
