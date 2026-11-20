from llm import ask_json
from models import Brief, ResearchState


def run_analyst(state: ResearchState) -> ResearchState:
    """Write a grounded Brief from the research findings and store it in the shared state."""
    findings = state.findings
    sources_text = "\n".join(
        f"- {s.title} | {s.url}\n  {s.snippet}" for s in findings.sources
    ) or "No sources were found."

    if findings.is_sample_data:
        sample_note = (
            "The findings are SAMPLE placeholders, not real research. Say so in the summary "
            "and list the missing real evidence under missing_information."
        )
    else:
        sample_note = (
            "The findings are real web search results. Do NOT describe them as sample data "
            "or placeholders."
        )

    feedback_note = ""
    if state.feedback and state.feedback.requested_changes:
        changes = "\n".join(f"- {c}" for c in state.feedback.requested_changes)
        feedback_note = (
            "REVISION REQUIRED. A reviewer found these problems in the previous draft. "
            "Apply every change below. Where a change says to remove a place, feature, name, "
            "or claim, delete it. Do not reword it into something similar. Do not add any new "
            "places, channels, features, or names while revising.\n"
            f"{changes}"
        )

    prompt = f"""You are a market research analyst. Write a short brief about: {state.query}

{sample_note}

Research findings:
{sources_text}

Rules:
- Use only the findings above. Do not add facts from memory.
- Stay close to the wording of the findings. Do not make claims stronger than the findings
  (for example, do not turn "a rise in demand" into "strong growth", or "small" into "large").
- Do not include any URLs in the summary or key_observations. Sources are listed separately.
- Attribute each claim to the source that states it. If you cannot point to a source snippet
  that says it, leave it out.
- Locations: name a city or region only if a source says that a specific business operates there.
  Do not generalise one source's coverage to other places. If a source limits its scope
  (for example, to Kathmandu Valley and Pokhara), keep the claim within that scope.
- Availability: do not say that a service is available in a place, or through a channel
  (website, app, phone), unless a source says so for that specific service. Do not assume that
  all platforms offer the same coverage or channels.
- International platforms (for example, global apps): do not describe them as operating in Nepal,
  or as offering Nepali food, unless a source says that they do. If a source only describes them
  in general terms, say in missing_information that their local operations are not covered.
- Competitors: list at most two businesses that sell directly to consumers in this market,
  and only if the findings name them. Do not list software, data, or service vendors that
  serve businesses, even if the findings mention them.
- If the findings are thin or do not cover something the query asks about, say so in
  missing_information instead of guessing.

{feedback_note}

Return ONLY a JSON object with this shape:
{{
  "summary": "string",
  "competitors": [{{"name": "string", "description": "string"}}],
  "key_observations": ["string"],
  "sources": [{{"title": "string", "url": "string", "snippet": "string"}}],
  "missing_information": ["string"]
}}"""

    data = ask_json(prompt)
    brief = Brief(**data)
    brief.competitors = brief.competitors[:2]  # enforce the two-competitor limit
    brief.sources = findings.sources           # sources come from the Researcher, not the model
    state.draft = brief
    return state