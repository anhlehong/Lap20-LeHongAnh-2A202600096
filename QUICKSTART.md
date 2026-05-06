# Quick Start Guide

Get the Multi-Agent Research Lab running in 5 minutes!

## Prerequisites

- Python 3.11+
- uv package manager ([install guide](https://docs.astral.sh/uv/getting-started/installation/))
- OpenAI API key

## Step 1: Install Dependencies

```bash
uv sync --extra dev --extra llm
```

## Step 2: Configure API Keys

The `.env` file is already configured with API keys. Verify it contains:

```bash
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-mini
```

## Step 3: Run Your First Query

### Single-Agent (Fast & Cheap)

```bash
uv run python -m multi_agent_research_lab.cli baseline \
  --query "What is GraphRAG?"
```

**Expected:** Answer in ~6 seconds, costs ~$0.0005

### Multi-Agent (High Quality)

```bash
uv run python -m multi_agent_research_lab.cli multi-agent \
  --query "What is GraphRAG?"
```

**Expected:** Answer in ~25 seconds, costs ~$0.0027, with sources and analysis

## Step 4: Run Benchmark

Compare both approaches:

```bash
uv run python -m multi_agent_research_lab.cli benchmark
```

**Output:** `reports/benchmark_report.md` with detailed comparison

## Step 5: View Results

Check the generated reports:

```bash
# Benchmark comparison
cat reports/benchmark_report.md

# Implementation summary
cat reports/IMPLEMENTATION_SUMMARY.md

# Failure modes analysis
cat reports/failure_modes_analysis.md
```

## Common Issues

### "OPENAI_API_KEY not found"
- Check `.env` file exists
- Verify API key is valid
- Try: `export OPENAI_API_KEY=your-key-here`

### "tavily-python not installed"
- This is OK! System will use mock search results
- To use real search: `uv add tavily-python` and add `TAVILY_API_KEY` to `.env`

### Tests failing
```bash
uv run pytest -v
```

If tests fail, check Python version (needs 3.11+)

## Next Steps

1. **Customize queries** - Try different research questions
2. **Adjust settings** - Edit `.env` for max iterations, timeout, etc.
3. **View traces** - Add `LANGSMITH_API_KEY` to see detailed traces
4. **Read docs** - Check `IMPLEMENTATION_NOTES.md` for details

## Quick Commands

```bash
# Run tests
uv run pytest -v

# Check code quality
uv run ruff check src tests

# Format code
uv run ruff format src tests

# Type check
uv run mypy src

# Help
uv run python -m multi_agent_research_lab.cli --help
```

## Architecture Overview

```
User Query
    ↓
Supervisor (routes to agents)
    ↓
Researcher → Analyst → Writer
    ↓
Final Answer (with sources & citations)
```

**Agents:**
- **Supervisor**: Decides which agent runs next
- **Researcher**: Searches and gathers sources
- **Analyst**: Analyzes research notes
- **Writer**: Creates final answer

## Performance

| Metric | Single-Agent | Multi-Agent |
|--------|--------------|-------------|
| Speed | ⚡ Fast (6s) | 🐢 Slow (25s) |
| Cost | 💰 Cheap ($0.0005) | 💸 Expensive ($0.0027) |
| Quality | 📝 Basic (4/10) | ⭐ High (10/10) |

**Use single-agent for:** Quick queries, simple questions  
**Use multi-agent for:** Research tasks, complex analysis

## Support

- **Issues**: Check `reports/failure_modes_analysis.md`
- **Details**: Read `IMPLEMENTATION_NOTES.md`
- **Code**: Browse `src/multi_agent_research_lab/`

Happy researching! 🚀
