# Market Research Brief

A Streamlit app that turns a company or industry into a short, sourced research brief.
Four roles run in order: Orchestrator, Researcher, Analyst, and Critic.

## Setup

Requires Python 3.10 or newer. On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Configure API keys

1. Copy `.env.example` to `.env`.
2. Add your Gemini key from https://aistudio.google.com/apikey as `GEMINI_API_KEY`.
3. Add your Tavily key from https://tavily.com as `TAVILY_API_KEY`.
4. Optional: change `GEMINI_MODELS` to set the order of models to try.

If `TAVILY_API_KEY` is missing or the search fails, the app uses clearly labelled sample data.
The brief then says so at the top of the page.

Never commit `.env`. It is listed in `.gitignore`.

## Run

```powershell
streamlit run app.py
```

Open the link shown in the terminal (usually http://localhost:8501), enter a company or industry,
and click **Start research**. A run usually takes one to three minutes.

To check which Gemini models your key can use, run `python test_models.py`.

## How it works

| Role | File | What it does |
|---|---|---|
| Orchestrator | `workflow.py` | Runs the roles in order and allows one revision |
| Researcher | `agents/researcher.py`, `search.py` | Searches the web and keeps usable results |
| Analyst | `agents/analyst.py` | Writes the brief as JSON from the search results only |
| Critic | `agents/critic.py` | Checks the draft against the results and lists issues |

The roles share one object, `ResearchState`, defined in `models.py` with Pydantic.

Flow: Research → Analyst → Critic. If the Critic rejects the draft, the Analyst revises it once,
and the Critic checks again. The page shows the final brief and any issues the Critic still lists.

## Grounding rules

- Sources come from the search results, not from the model. The model cannot invent URLs.
- The Analyst may use only the search snippets. It is told to avoid stronger wording than the sources use.
- The Critic checks claims, wording, competitors, locations, availability, and product names.
- Competitors are capped at two.

## Reliability

- `llm.py` tries each model in `GEMINI_MODELS` in order. If one is busy (429, 500, 503) or
  unavailable (404), it moves to the next. If all are busy, it waits and tries again, up to three rounds.
- If the model returns malformed JSON, the request is sent once more.
- Errors are shown on the page instead of crashing the app.

## Known limitations

- **Nationwide generalisation.** Some sources cover only the Kathmandu Valley, but the brief sometimes
  describes the market as "Nepal" as a whole. The Critic flags this, and the page shows the flag.
- **Two-competitor cap.** The brief names at most two competitors, so it does not list every company the sources mention.
- **Weaker sources.** Some results are video or social content (for example, a YouTube video and a LinkedIn post).
  They are used only for supporting points.
- **Critic can miss or over-flag.** The Critic is an LLM reviewer. It has approved claims that the snippets do not
  support (for example, a claim about payment methods in one run). It has also rejected claims the sources do support.
  Its remaining issues are shown on the page so the reader can judge them.
- **Snippets, not full pages.** The brief is based on search snippets of up to 500 characters, not full articles.
- **Results vary.** Search results change between runs, so the brief will vary.
- **Shared free tier.** Gemini's free tier is often busy. Runs can be slow or fail. Retrying later usually works.
- **One revision only.** If the Critic still rejects the draft after one revision, the final draft is shown with the Critic's issues.
- **Sources can disagree.** For example, an article and app listings describe Foodmandu's coverage differently.
  The brief notes the disagreement where it can instead of choosing one version.

## Sample output

See `sample_output.md` for a run on **food delivery in Nepal**, including the Critic's remaining issues.

## Files

- `app.py`: Streamlit page
- `workflow.py`: runs the roles in order
- `models.py`: shared data models
- `llm.py`: Gemini calls, model fallback, and retries
- `search.py`: Tavily search with sample-data fallback
- `agents/`: Researcher, Analyst, and Critic
- `test_models.py`: checks which Gemini models your key can use
- `requirements.txt`: Python packages
- `.env.example`: template for API keys and settings
- `sample_output.md`: example run
- `README.md`: this file