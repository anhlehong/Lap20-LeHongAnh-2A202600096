#!/usr/bin/env python3
"""Get recent LangSmith traces for the project."""

import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from langsmith import Client

# Load environment variables
load_dotenv()


def get_recent_traces(limit: int = 10) -> None:
    """Get and display recent traces from LangSmith."""

    api_key = os.getenv("LANGSMITH_API_KEY")
    project = os.getenv("LANGSMITH_PROJECT", "multi-agent-research-lab")

    if not api_key:
        print("❌ LANGSMITH_API_KEY not found in .env")
        return

    print(f"\n{'=' * 100}")
    print(f"  LangSmith Traces - Project: {project}")
    print(f"{'=' * 100}\n")

    try:
        client = Client(api_key=api_key)

        # Get recent runs
        runs = list(client.list_runs(project_name=project, limit=limit))

        if not runs:
            print("⚠️  No traces found. Run a workflow first!")
            return

        print(f"Found {len(runs)} recent traces:\n")

        for i, run in enumerate(runs, 1):
            # Format timestamp
            start_time = run.start_time
            if start_time:
                time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
            else:
                time_str = "N/A"

            # Calculate duration
            duration = "N/A"
            if run.end_time and run.start_time:
                delta = run.end_time - run.start_time
                duration = f"{delta.total_seconds():.2f}s"

            # Get status
            status = "✅" if run.error is None else "❌"

            # Build trace URL
            trace_url = f"https://smith.langchain.com/public/{run.id}/r"

            print(f"{i}. {status} {run.name}")
            print(f"   Time: {time_str}")
            print(f"   Duration: {duration}")
            print(f"   Run ID: {run.id}")
            print(f"   URL: {trace_url}")

            # Show inputs if available
            if run.inputs:
                query = run.inputs.get("request", {}).get("query", "N/A")
                if query != "N/A":
                    print(f"   Query: {query[:60]}...")

            # Show error if any
            if run.error:
                print(f"   Error: {run.error[:100]}...")

            print()

        # Show project URL
        print(f"{'=' * 100}")
        print(f"Project Dashboard: https://smith.langchain.com/o/default/projects/p/{project}")
        print(f"{'=' * 100}\n")

    except Exception as e:
        print(f"❌ Failed to get traces: {e}")


if __name__ == "__main__":
    get_recent_traces(limit=10)
