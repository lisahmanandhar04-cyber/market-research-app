from models import ResearchState
from search import search_web


def run_researcher(state: ResearchState) -> ResearchState:
    """Find sources for the query and store them in the shared state."""
    state.findings = search_web(state.query)
    return state