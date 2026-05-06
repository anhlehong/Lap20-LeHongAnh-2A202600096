"""Search client abstraction for ResearcherAgent."""

import logging

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.schemas import SourceDocument

logger = logging.getLogger(__name__)


class SearchClient:
    """Provider-agnostic search client skeleton."""

    def __init__(self) -> None:
        settings = get_settings()
        self.tavily_api_key = settings.tavily_api_key
        self.use_mock = not self.tavily_api_key

        if self.use_mock:
            logger.warning("TAVILY_API_KEY not found, using mock search results")

    def search(self, query: str, max_results: int = 5) -> list[SourceDocument]:
        """Search for documents relevant to a query."""
        if self.use_mock:
            return self._mock_search(query, max_results)

        try:
            from tavily import TavilyClient

            client = TavilyClient(api_key=self.tavily_api_key)
            response = client.search(query=query, max_results=max_results)

            results = []
            for item in response.get("results", []):
                results.append(
                    SourceDocument(
                        title=item.get("title", "Untitled"),
                        url=item.get("url"),
                        snippet=item.get("content", ""),
                        metadata={"score": item.get("score", 0.0)},
                    )
                )
            return results

        except ImportError:
            logger.warning("tavily-python not installed, falling back to mock search")
            return self._mock_search(query, max_results)
        except Exception as e:
            logger.error(f"Tavily search failed: {e}, falling back to mock")
            return self._mock_search(query, max_results)

    def _mock_search(self, query: str, max_results: int) -> list[SourceDocument]:
        """Return mock search results for testing without API keys."""
        mock_results = [
            SourceDocument(
                title=f"Mock Result 1: {query}",
                url="https://example.com/article1",
                snippet=f"This is a mock search result about {query}. GraphRAG combines knowledge graphs with retrieval-augmented generation for improved context understanding.",
                metadata={"score": 0.95, "mock": True},
            ),
            SourceDocument(
                title=f"Mock Result 2: State-of-the-art in {query}",
                url="https://example.com/article2",
                snippet=f"Recent advances in {query} show promising results. The approach uses graph structures to enhance semantic search and reasoning capabilities.",
                metadata={"score": 0.88, "mock": True},
            ),
            SourceDocument(
                title=f"Mock Result 3: {query} Applications",
                url="https://example.com/article3",
                snippet=f"Practical applications of {query} in enterprise settings demonstrate significant improvements in information retrieval accuracy and relevance.",
                metadata={"score": 0.82, "mock": True},
            ),
            SourceDocument(
                title=f"Mock Result 4: {query} Research Paper",
                url="https://arxiv.org/example",
                snippet=f"Academic research on {query} explores novel architectures combining graph neural networks with large language models for enhanced reasoning.",
                metadata={"score": 0.75, "mock": True},
            ),
            SourceDocument(
                title=f"Mock Result 5: {query} Implementation Guide",
                url="https://example.com/guide",
                snippet=f"Step-by-step guide to implementing {query} systems, covering data modeling, indexing strategies, and query optimization techniques.",
                metadata={"score": 0.70, "mock": True},
            ),
        ]

        return mock_results[:max_results]
