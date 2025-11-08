import streamlit as st
from openai import OpenAI
import os
import json
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


# Load environment
# NOTE: Using st.secrets assumes you have the GEMINI_API_KEY configured in Streamlit secrets.
# The API key is loaded securely from the Streamlit environment.
api_key = st.secrets["GEMINI_API_KEY"]

client = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)


# Tool: Movie Data Fetcher (Mock)
def fetch_movie_metadata(preference_keyword: str) -> str:
    """
    Retrieves mock movie data based on a user's preference keyword (e.g., genre or theme).

    This function simulates a tool call to a movie database, returning 
    structured metadata for the LLM to analyze and synthesize a recommendation.

    Args:
        preference_keyword: A primary keyword provided by the user (e.g., 'sci-fi', 'action').

    Returns:
        A JSON string containing a list of movies (name, genre, rating, runtime), 
        or an error message string if the keyword yields no results.
    """
    keyword = preference_keyword.lower().strip()
    # Mock data for demonstration purposes, categorized by general keywords.
    mock_movies: Dict[str, List[Dict[str, Any]]] = {
        "sci-fi": [
            {"title": "Space Odyssey 2001", "genre": "Sci-Fi/Drama", "imdb_rating": 8.3, "runtime_mins": 149},
            {"title": "Robot Detective", "genre": "Sci-Fi/Thriller", "imdb_rating": 7.5, "runtime_mins": 115},
            {"title": "The Infinite Loop", "genre": "Sci-Fi/Mystery", "imdb_rating": 9.1, "runtime_mins": 180},
        ],
        "action": [
            {"title": "The Fast Getaway", "genre": "Action/Thriller", "imdb_rating": 7.8, "runtime_mins": 95},
            {"title": "Mountain Commandos", "genre": "Action/War", "imdb_rating": 8.0, "runtime_mins": 122},
        ],
        "comedy": [
            {"title": "The Office Party", "genre": "Comedy/Slice of Life", "imdb_rating": 6.9, "runtime_mins": 88},
            {"title": "Wacky Neighbors", "genre": "Comedy/Slapstick", "imdb_rating": 7.2, "runtime_mins": 105},
        ],
    }

    movies: Optional[List[Dict[str, Any]]] = mock_movies.get(keyword)
    
    # Simple logic to broaden the search if the exact keyword doesn't match
    if not movies:
        for key, value in mock_movies.items():
            if key in keyword or preference_keyword in key:
                movies = value
                break

    if movies:
        # Return the data as a JSON string for the model to analyze
        return json.dumps(movies)
    else:
        return f"⚠️ Could not find movies matching: {preference_keyword}. Try 'sci-fi', 'action', or 'comedy'."

available_tools: Dict[str, Any] = {
    "fetch_movie_metadata": fetch_movie_metadata,
    "get_movie_data": fetch_movie_metadata, # alias
}

# System Prompt (Movie Recommendation Engine)
SYSTEM_PROMPT = """
You are the **Movie Recommendation Engine (MRE)**. Your core function is to provide highly curated and justified movie suggestions based on user preferences (genre, runtime, rating, etc.). You **must** utilize the Chain-of-Thought (CoT) reasoning pattern for every response, regardless of the complexity of the user's query.

### 1. Chain-of-Thought (CoT) Requirement
**STRICT RULE:** Your output must begin with an invisible **THOUGHT** block where you detail your step-by-step analysis. Do not show this THOUGHT block to the user.

**The CoT Process MUST include:**
1.  **Data Ingestion:** Identify the user's primary preferences (e.g., 'sci-fi', 'short runtime', 'high rating').
2.  **Tool Execution Planning:** Plan to use the `fetch_movie_metadata` tool with the primary preference keyword.
3.  **Source Cross-Verification:** Mentally synthesize the list of movies received from the tool. Filter and categorize them by the user's explicit constraints (e.g., must be over an 8.0 rating, less than 120 minutes runtime).
4.  **Contextual Interpretation:** Select the absolute best recommendation, highlighting *why* it is the best fit based on the user's input and the analyzed metrics (rating, runtime, genre fit).
5.  **Final Synthesis:** Construct the final, clear, and direct Movie Recommendation statement based *only* on the conclusion of the analysis.

### 2. Output Format
Your final, user-facing output **must** be clear and structured, beginning with the **Recommendation Summary** and concluding with the **Justification** based on your CoT process.

**Required User-Facing Format:**
1.  **Summary Greeting:** A concise, enthusiastic greeting relevant to the user's taste.
2.  **Top Recommendation:** State the **Top Recommendation**, including Title and Primary Genre.
3.  **Key Metrics:** List the key metrics (e.g., IMDb Rating, Runtime).
4.  **---** (Horizontal Rule)
5.  **Recommendation Justification:** A brief, compelling explanation (1-2 sentences) of *why* this movie was selected based on the analyzed data and user preferences.

### 3. Constraints
* **Focus on Quality:** Prioritize high-rated and well-fitting options.
* **Avoid Spoilers:** Only provide metadata and fit assessment, not plot details.
* **Use Standard Film Terminology:** Use clear terms like 'runtime', 'rating', and 'genre'.
"""

# Pydantic Schema (Keep the same structure for CoT steps)
class MyOutputFormat(BaseModel):
    """Defines the structured output format for the Chain-of-Thought steps."""
    step: str = Field(..., description="START | PLAN | OUTPUT | TOOL | OBSERVE")
    content: Optional[str] = None
    tool: Optional[str] = None
    input: Optional[str] = None


# Streamlit App
st.set_page_config(page_title="MRE: Movie Recommendation Engine", page_icon="🎬", layout="centered")

# Updated hints and titles for a more professional look
st.markdown(
    "<h1 style='text-align: center; color: #6200EE;'>🎬 Movie Recommendation Engine (MRE) 🍿</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align: center; color: #CCCCCC; font-size:16px;'>Utilizing Chain-of-Thought (CoT) reasoning to generate the perfect movie match based on your preferences. Example: 'Suggest a sci-fi movie under 150 minutes.'</p>",
    unsafe_allow_html=True
)


# Clear chat button
if st.button("🧹 Clear Recommendations"):
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    st.session_state.chat_history = []
    st.rerun()

# Initialize session state with explicit type hints for clarity
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# User input (chat box style)
user_query: Optional[str] = st.chat_input("Enter your movie preferences...")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.session_state.chat_history.append(("user", user_query))

    while True:
        # Use st.spinner for a professional look while the agent is thinking/running tools
        with st.spinner("MRE is analyzing preferences and metadata..."):
            response = client.chat.completions.parse(
                model='gemini-2.5-flash',
                response_format=MyOutputFormat,
                messages=st.session_state.messages
            )

        raw_result: str = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": raw_result})

        parsed: MyOutputFormat = response.choices[0].message.parsed

        # Handle steps
        if parsed.step == "START":
            st.session_state.chat_history.append(("assistant", f"🔥 MRE Initialized: {parsed.content}"))
            continue

        elif parsed.step == "PLAN":
            st.session_state.chat_history.append(("assistant", f"🧠 Planning: {parsed.content}"))
            continue

        elif parsed.step == "TOOL":
            tool_name: str = parsed.tool
            tool_input: str = parsed.input
            
            # Show the execution step
            st.session_state.chat_history.append(("assistant", f"🛠️ Fetching data using keyword: {tool_input}"))
            
            if tool_name in available_tools:
                tool_response: str = available_tools[tool_name](tool_input)
            else:
                tool_response: str = f"Error: Tool {tool_name} not found."

            st.session_state.messages.append({
                "role": "developer",
                "content": json.dumps({
                    "step": "OBSERVE",
                    "tool": tool_name,
                    "input": tool_input,
                    "output": tool_response
                })
            })
            continue

        elif parsed.step == "OUTPUT":
            st.session_state.chat_history.append(("assistant", f"🤖 **MRE Recommendation:** {parsed.content}"))
            break

# -------------------
# Display chat history (Custom UI style)
# -------------------
for role, msg in st.session_state.chat_history:
    if role == "user":
        # Right-aligned bubble (user)
        st.markdown(
            f"""
            <div style="display: flex; justify-content: flex-end; margin: 5px;">
                <div style="background-color: #00897B; color: #FFFFFF; padding: 10px 15px; border-radius: 12px; max-width: 70%; text-align: left; box-shadow: 2px 2px 5px rgba(0,0,0,0.2);">
                    <b>👤 User Preference:</b> {msg}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        # Left-aligned bubble (bot)
        # Use different colors for different steps for better visibility
        color: str = "#2B2B2B"
        if "🔥 MRE Initialized:" in msg:
             color = "#1E88E5" # Blue for Start
        elif "🧠 Planning:" in msg:
             color = "#07FF83" # Yellow for Plan
        elif "🛠️ Fetching data using keyword:" in msg:
             color = "#7CB342" # Green for Tool
        elif "🤖 **MRE Recommendation:**" in msg:
             color = "#00A3EE" # Purple for Final Output

        st.markdown(
            f"""
            <div style="display: flex; justify-content: flex-start; margin: 5px;">
                <div style="background-color: {color}; color: #F0F0F0; padding: 10px 15px; border-radius: 12px; max-width: 70%; text-align: left; box-shadow: 2px 2px 5px rgba(0,0,0,0.2);">
                    {msg}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )