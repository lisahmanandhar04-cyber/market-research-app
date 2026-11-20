from llm import ask_json
from models import CriticFeedback, ResearchState


def run_critic(state: ResearchState) -> ResearchState:
    """Check the draft against the findings and store feedback in the shared state."""
    draft = state.draft
    findings = state.findings
    sources_text = "\n".join(
        f"- {s.title} | {s.url}\n  {s.snippet}" for s in findings.sources
    ) or "No sources were found."

    prompt = f"""You are a strict reviewer of a market research brief.

Research findings (the only allowed evidence):
Findings are sample data: {findings.is_sample_data}
{sources_text}

Draft brief (JSON):
{draft.model_dump_json(indent=2)}

Check the draft:
1. Does every factual claim in the summary and key_observations appear in the findings?
   List each claim or word that does not, for example a term like "retention" that the findings never mention.
2. Does any sentence use wording stronger than the findings? For example, "growth" when a source says
   "rise in demand", or "large" when a source says "small". List each one.
3. Do the summary or key_observations contain any URLs? If so, list them. URLs belong only in sources.
4. Are the competitors named in the findings, and are they businesses that sell directly to consumers
   in this market? List any that are software, data, or service vendors for businesses, or are not named in the findings.
   Do not ask for more than two competitors.
5. Does missing_information state the real gaps in the evidence?
6. If the findings are real (is_sample_data is False), the summary must NOT mention sample data or placeholders.
   If they are sample data, the summary must say so.
7. Locations: every city or region named in the summary or key_observations must appear in a source
   snippet as a place where that same business operates. If a source limits its scope (for example,
   to Kathmandu Valley and Pokhara), any location outside that scope is an issue. List each one.
8. Availability and channels: every claim that a service is available in a place, or through a channel
   (website, app, phone, social media, wallet), must be stated in a source for that same service.
   List each claim that has no matching source.
9. Names: every named product or feature (for example, a wallet or loyalty program name) must appear in a source snippet.
   List each name that does not.

Approve only if all nine checks pass and the issues list is empty. If any issue is listed,
approved must be false. For each issue, write a requested change as a specific edit the Analyst can make,
such as "Remove 'Butwal' and 'Chitwan' from the summary and key_observations, because the source limits
coverage to Kathmandu Valley and Pokhara."
Do not request changes that would add more than two competitors.

Return ONLY a JSON object with this shape:
{{
  "approved": true,
  "issues": ["string"],
  "requested_changes": ["string"]
}}"""

    data = ask_json(prompt)
    state.feedback = CriticFeedback(**data)
    return state