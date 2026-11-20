from agents.analyst import run_analyst
from agents.critic import run_critic
from agents.researcher import run_researcher
from models import ResearchState

MAX_REVISIONS = 1


def run_orchestrator(query: str) -> ResearchState:
    """Start the workflow and run each role in sequence, with at most one revision."""
    query = query.strip()
    if not query:
        raise ValueError("Please enter a company or industry.")

    state = ResearchState(query=query)
    state = run_researcher(state)
    state = run_analyst(state)
    state = run_critic(state)

    while not state.feedback.approved and state.revision_count < MAX_REVISIONS:
        state.revision_count += 1
        state = run_analyst(state)  # uses state.feedback to revise
        state = run_critic(state)

    return state