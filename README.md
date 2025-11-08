# 🎬 Movie Recommendation Engine (MRE) Agent

This repository contains the Movie Recommendation Engine (MRE): a small Streamlit app that demonstrates an agentic, chain-of-thought (CoT) pattern with structured outputs and a mock "tool" for fetching movie metadata. The app uses the OpenAI-compatible client for Google Gemini (via the compatibility OpenAI-style endpoint) to show how an LLM can plan, call tools, observe results, and synthesize a final recommendation.

## What this project does

- Presents a chat-style Streamlit UI where a user submits movie preferences (e.g., "Recommend a sci-fi under 150 minutes").
- Uses a strict Chain-of-Thought (CoT) process enforced by a Pydantic schema so the assistant returns structured steps (START, PLAN, TOOL, OBSERVE, OUTPUT).
- Demonstrates tool invocation via a local mock function (`fetch_movie_metadata`) that returns JSON metadata for a small set of sample movies.

## Files of interest

- `main.py` — The Streamlit application and the agent logic (CoT, tool wiring, UI).
- `requirements.txt` — Python dependencies used by the project.
- `.streamlit/secrets.toml` (optional) — Where you can put the GEMINI_API_KEY for Streamlit to pick up.

## Quick start (Windows / PowerShell)

1. Open PowerShell in the project directory.

2. (Optional) Activate the included virtual environment `hmenv` if you want to use it:

```powershell
# Activate the virtualenv (PowerShell)
.\hmenv\Scripts\Activate.ps1
```

If PowerShell prevents running scripts, you may need to temporarily allow local script execution (run as Administrator or set for the current user):

```powershell
# Allow execution of activation script for the current user (if blocked)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

3. Install dependencies (inside the venv or your chosen interpreter):

```powershell
pip install -r requirements.txt
```

4. Configure your API key for Gemini (used via the OpenAI-compatible endpoint).

- Preferred (Streamlit secrets): create a directory named `.streamlit` in the project root and a `secrets.toml` file with:

```toml
# .streamlit/secrets.toml
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"
```

- Alternative: export an environment variable in PowerShell before running (the app currently reads `st.secrets['GEMINI_API_KEY']`, so using a Streamlit secret is recommended). If you adapt the code to read `os.environ`, you can set an env var instead:

```powershell
$env:GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"
```

5. Run the Streamlit app:

```powershell
streamlit run main.py
```

Open the displayed URL (usually http://localhost:8501) to interact with the agent.

## How it works (short)

- The assistant must follow a Chain-of-Thought (CoT) pattern. The app enforces structured messages using a Pydantic `MyOutputFormat` model.
- When the model returns a `TOOL` step, the app calls the Python function `fetch_movie_metadata` with the provided keyword. That function returns a JSON string with mock movie metadata.
- The model receives the tool output (in a developer/system message) and continues the CoT flow to a final `OUTPUT` step which the app displays to the user.

## Customizing the mock tool

`fetch_movie_metadata` in `main.py` contains small mock datasets for `sci-fi`, `action`, and `comedy`. You can:

- Replace the mock data with real API calls (e.g., to TMDB or OMDb).
- Return richer metadata (cast, release year, genres) — the LLM can then reason over those fields.

When adding networked tools, be careful to validate and sanitize external responses before sending them back into an LLM loop.

## Troubleshooting

- Activation fails: ensure PowerShell execution policy permits running scripts (see `Set-ExecutionPolicy` above).
- Streamlit can't find secrets: Streamlit loads `.streamlit/secrets.toml` from the project root. Confirm the file exists and is valid TOML.
- Missing dependencies: double-check `pip install -r requirements.txt` completed successfully and that you're using the same Python interpreter as the activated venv.

## Notes and security

- This project stores API keys in Streamlit's `secrets.toml` for convenience. For production or shared repos, never commit secrets to source control. Use environment-specific secrets management.
- The code demonstrates the CoT pattern in an educational context and uses a mock tool. If you wire in external APIs, follow their rate limits and credential best practices.

## License

MIT — LICENSE
