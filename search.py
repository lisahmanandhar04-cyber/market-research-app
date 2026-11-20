import os

from dotenv import load_dotenv
from tavily import TavilyClient

from models import ResearchFindings, Source

load_dotenv()

SAMPLE_SOURCES = [
    Source(
        title="[SAMPLE] Food delivery market overview",
        url="https://example.com/sample-1",
        snippet="Placeholder text. Replace with real search results.",
    ),
    Source(
        title="[SAMPLE] Competitor profiles",
        url="https://example.com/sample-2",
        snippet="Placeholder text. Replace with real search results.",
    ),
]

# Phrases that show a page's navigation or template text rather than content.
BOILERPLATE_MARKERS = ("logo of", "edit-link", "download app", "back to blog", "key facts about")
MIN_WORDS = 25


def _is_usable(source: Source) -> bool:
    """Drop results whose snippet is navigation or template text, or too short to use."""
    text = source.snippet.lower()
    if any(marker in text for marker in BOILERPLATE_MARKERS):
        return False
    return len(source.snippet.split()) >= MIN_WORDS


def search_web(query: str, max_results: int = 8) -> ResearchFindings:
    """Return usable real search results from Tavily, or labelled sample data as a fallback."""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return _sample_findings(query, "TAVILY_API_KEY not set. Using sample data.")

    try:
        client = TavilyClient(api_key=api_key)
        response = client.search(query=query, max_results=max_results)
        sources = [
            Source(
                title=item.get("title", "Untitled"),
                url=item.get("url", ""),
                snippet=item.get("content", "")[:500],
            )
            for item in response.get("results", [])
        ]
        usable = [s for s in sources if _is_usable(s)][:5]
        if not usable:
            return _sample_findings(query, "Search returned no usable results. Using sample data.")
        return ResearchFindings(query=query, sources=usable, is_sample_data=False)
    except Exception as exc:
        return _sample_findings(query, f"Search failed ({exc}). Using sample data.")


def _sample_findings(query: str, note: str) -> ResearchFindings:
    return ResearchFindings(
        query=query,
        sources=SAMPLE_SOURCES,
        is_sample_data=True,
        notes=note,
    )