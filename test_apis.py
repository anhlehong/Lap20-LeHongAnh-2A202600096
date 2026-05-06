#!/usr/bin/env python3
"""Test all API integrations from .env file."""

import os
import sys
from datetime import datetime

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def print_section(title: str) -> None:
    """Print a section header."""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}\n")


def test_openai() -> bool:
    """Test OpenAI API."""
    print_section("Testing OpenAI API")

    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    if not api_key:
        print("❌ OPENAI_API_KEY not found in .env")
        return False

    print(f"✓ API Key found: {api_key[:20]}...")
    print(f"✓ Model: {model}")

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        print("\n🔄 Making test API call...")

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'API test successful' in exactly 3 words."},
            ],
            max_completion_tokens=10,
        )

        content = response.choices[0].message.content
        tokens_used = response.usage.total_tokens if response.usage else 0

        print(f"✅ OpenAI API works!")
        print(f"   Response: {content}")
        print(f"   Tokens used: {tokens_used}")
        return True

    except Exception as e:
        print(f"❌ OpenAI API failed: {e}")
        return False


def test_tavily() -> bool:
    """Test Tavily Search API."""
    print_section("Testing Tavily Search API")

    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        print("⚠️  TAVILY_API_KEY not found in .env (optional)")
        return True  # Not critical

    print(f"✓ API Key found: {api_key[:20]}...")

    try:
        from tavily import TavilyClient

        client = TavilyClient(api_key=api_key)
        print("\n🔄 Making test search...")

        response = client.search(query="AI news", max_results=2)

        results = response.get("results", [])
        print(f"✅ Tavily API works!")
        print(f"   Found {len(results)} results")

        if results:
            print(f"   First result: {results[0].get('title', 'N/A')[:60]}...")

        return True

    except ImportError:
        print("⚠️  tavily-python not installed (run: uv add tavily-python)")
        return True  # Not critical
    except Exception as e:
        print(f"❌ Tavily API failed: {e}")
        return False


def test_langsmith() -> bool:
    """Test LangSmith tracing."""
    print_section("Testing LangSmith Tracing")

    api_key = os.getenv("LANGSMITH_API_KEY")
    project = os.getenv("LANGSMITH_PROJECT", "multi-agent-research-lab")

    if not api_key:
        print("⚠️  LANGSMITH_API_KEY not found in .env (optional)")
        return True  # Not critical

    print(f"✓ API Key found: {api_key[:20]}...")
    print(f"✓ Project: {project}")

    try:
        from langsmith import Client

        client = Client(api_key=api_key)
        print("\n🔄 Testing connection...")

        # Try to list projects
        projects = list(client.list_projects(limit=1))

        print(f"✅ LangSmith API works!")
        print(f"   Connected to LangSmith")
        print(f"   Project URL: https://smith.langchain.com/o/default/projects/p/{project}")

        # Set environment variables for tracing
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = api_key
        os.environ["LANGCHAIN_PROJECT"] = project
        print(f"   ✓ Tracing environment variables set")

        return True

    except ImportError:
        print("⚠️  langsmith not installed (should be in dependencies)")
        return True  # Not critical
    except Exception as e:
        print(f"❌ LangSmith API failed: {e}")
        return False


def test_langfuse() -> bool:
    """Test Langfuse tracing."""
    print_section("Testing Langfuse Tracing")

    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    base_url = os.getenv("LANGFUSE_BASE_URL", "https://cloud.langfuse.com")

    if not secret_key or not public_key:
        print("⚠️  LANGFUSE keys not found in .env (optional)")
        return True  # Not critical

    print(f"✓ Secret Key found: {secret_key[:20]}...")
    print(f"✓ Public Key found: {public_key[:20]}...")
    print(f"✓ Base URL: {base_url}")

    try:
        from langfuse import Langfuse

        client = Langfuse(
            secret_key=secret_key, public_key=public_key, host=base_url, debug=False
        )

        print("\n🔄 Testing connection...")

        # Create a test trace
        trace = client.trace(name="api_test", metadata={"test": True})

        print(f"✅ Langfuse API works!")
        print(f"   Created test trace: {trace.id}")
        print(f"   Dashboard: {base_url}")

        # Flush to ensure trace is sent
        client.flush()

        return True

    except ImportError:
        print("⚠️  langfuse not installed (run: uv add langfuse)")
        return True  # Not critical
    except Exception as e:
        print(f"❌ Langfuse API failed: {e}")
        return False


def test_all() -> None:
    """Run all API tests."""
    print("\n" + "=" * 80)
    print(f"  API Integration Tests - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    results = {
        "OpenAI": test_openai(),
        "Tavily": test_tavily(),
        "LangSmith": test_langsmith(),
        "Langfuse": test_langfuse(),
    }

    # Summary
    print_section("Test Summary")

    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}  {name}")

    total = len(results)
    passed = sum(results.values())
    failed = total - passed

    print(f"\n{'=' * 80}")
    print(f"Total: {total} | Passed: {passed} | Failed: {failed}")
    print(f"{'=' * 80}\n")

    if failed > 0:
        print("⚠️  Some tests failed. Check the output above for details.")
        sys.exit(1)
    else:
        print("🎉 All API tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    test_all()
