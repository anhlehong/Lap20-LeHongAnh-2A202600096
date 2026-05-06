#!/usr/bin/env python3
"""Test Langfuse integration."""

import os
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()


def test_langfuse_connection():
    """Test Langfuse API connection."""
    print("\n" + "=" * 80)
    print("  Testing Langfuse Integration")
    print("=" * 80 + "\n")

    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    base_url = os.getenv("LANGFUSE_BASE_URL", "https://cloud.langfuse.com")

    if not secret_key or not public_key:
        print("❌ LANGFUSE keys not found in .env")
        return False

    print(f"✓ Secret Key: {secret_key[:20]}...")
    print(f"✓ Public Key: {public_key[:20]}...")
    print(f"✓ Base URL: {base_url}")

    try:
        from langfuse import Langfuse

        print("\n🔄 Initializing Langfuse client...")
        client = Langfuse(
            secret_key=secret_key, public_key=public_key, host=base_url
        )

        print("🔄 Creating test trace...")
        # Use correct API
        trace = client.trace(
            id="test-trace-" + datetime.now().strftime("%Y%m%d-%H%M%S"),
            name="test_trace",
            metadata={"test": True, "timestamp": datetime.now().isoformat()},
        )

        print(f"✅ Trace created successfully")

        # Create a span
        print("🔄 Creating test span...")
        span = client.span(
            trace_id=trace.id,
            name="test_span",
            metadata={"test": True},
        )

        print(f"✅ Span created successfully")

        # Flush to ensure data is sent
        print("🔄 Flushing data to Langfuse...")
        client.flush()

        print("\n✅ Langfuse integration working!")
        print(f"   Dashboard: {base_url}")
        print(f"   Check your Langfuse dashboard for the test trace")

        return True

    except ImportError:
        print("❌ langfuse package not installed")
        print("   Run: uv add langfuse")
        return False
    except Exception as e:
        print(f"❌ Langfuse test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_langfuse_callback():
    """Test Langfuse with callback handler."""
    print("\n" + "=" * 80)
    print("  Testing Langfuse Callback Handler")
    print("=" * 80 + "\n")

    try:
        from langfuse.callback import CallbackHandler

        secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        base_url = os.getenv("LANGFUSE_BASE_URL", "https://cloud.langfuse.com")

        if not all([secret_key, public_key]):
            print("❌ Missing required API keys")
            return False

        print("🔄 Creating Langfuse callback handler...")
        handler = CallbackHandler(
            secret_key=secret_key,
            public_key=public_key,
            host=base_url,
        )

        print("✅ Callback handler created successfully")
        print("   This can be used with LangChain/LangGraph")
        print(f"   Dashboard: {base_url}")

        return True

    except ImportError as e:
        print(f"⚠️  Callback handler not available: {e}")
        return False
    except Exception as e:
        print(f"❌ Callback test failed: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print(f"  Langfuse Integration Tests - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    result1 = test_langfuse_connection()
    result2 = test_langfuse_callback()

    print("\n" + "=" * 80)
    print("  Test Summary")
    print("=" * 80 + "\n")

    print(f"{'✅' if result1 else '❌'} Langfuse Connection")
    print(f"{'✅' if result2 else '❌'} Langfuse Callback Handler")

    if result1 or result2:
        print("\n🎉 Langfuse is working! Check your dashboard:")
        print(f"   {os.getenv('LANGFUSE_BASE_URL', 'https://cloud.langfuse.com')}")
    else:
        print("\n⚠️  Langfuse integration needs setup")

    print("\n" + "=" * 80 + "\n")
