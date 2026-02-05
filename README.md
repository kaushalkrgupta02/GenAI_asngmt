# AI Ops Assistant

## Overview
The AI Ops Assistant is a versatile system designed to handle a wide range of user queries by leveraging multiple agents and tools. It integrates various APIs to provide information on weather, news, jokes, and more. The system is built with a modular architecture, allowing for easy extension and maintenance. This is runnig on Streamlit for a user-friendly interface, and it utilizes the Groq LLM for natural language understanding and response generation.

---

## Setup Instructions
1. Clone the repository:
   ```bash
   git clone https://github.com/kaushalkrgupta02/GenAI_asngmt.git
   cd GenAI_asngmt
   ```
2. Create and activate a virtual environment (Optional if you have already Python environment set up):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install the required dependencies:
   ```bash
    pip install -r requirements.txt
   ```
4. Set up environment variables:
    - copy the `.env.example` file to `.env` and **fill in the required API keys and configurations**.

    ```bash
    cp .env.example .env # On Windows use `copy .env.example .env`
    ```
5. Run the application:
    ```bash
    streamlit run main.py
    ```

---

## Architecture
The AI Ops Assistant is built as a multi-agent system featuring three specialized agents that collaborate to process user queries efficiently and reliably. It utilizes base classes for modularity and extensibility.

- **Base Agent** (`agents/base_agent.py`): Provides a common foundation for all agents, handling initialization, LLM client setup, and shared utilities.
- **Planner Agent** (`agents/planner.py`):
  - Transforms natural language user input into a structured JSON execution plan.
  - Leverages the Groq LLM to analyze queries, identify necessary tools (weather, news, jokes), and determine parameters.
  - Validates plans against available tools to ensure feasibility.
- **Executor Agent** (`agents/executor.py`):
  - Executes plan steps in sequence, invoking the appropriate API tools.
  - Implements retry logic with up to 3 attempts on failures, using exponential backoff.
  - Handles errors and provides detailed step results.
- **Verifier Agent** (`agents/verifier.py`):
  - Validates execution results for completeness and accuracy.
  - Formats outputs into user-friendly responses using the Groq LLM for quality assurance.
  - Identifies missing information and suggests retries if needed.

**Tools**:
- **Base Tool** (`tools/base_tool.py`): Defines the core structure for tool implementations, including API key validation, caching, and error handling.
- `tools/weather_tool.py`: Integrates with OpenWeatherMap API to fetch current weather data by city name or geographic coordinates, including temperature, humidity, conditions, and wind speed.
- `tools/news_tool.py`: Connects to NewsAPI for searching news articles or retrieving top headlines by category, country, or query.
- `tools/jokes_tool.py`: Interfaces with JokeAPI to retrieve random jokes or search for jokes based on keywords.

**LLM Client** (`llm/llm_client.py`): Provides a unified interface for the Groq LLM provider, supporting JSON-mode outputs for structured plan generation, result verification, and parameter extraction.


---

## Integrated APIs
- **OpenWeatherMap API**:
  - Retrieves current weather by city name or coordinates.
  - Returns: temperature (C/F), humidity, conditions, wind speed.
  - Source: https://openweathermap.org/api
- **NewsAPI**:
  - Retrieves the latest news headlines, searches news articles, and gets top headlines by country/category.
  - Returns: title, source, description, URL, publish date.
  - Source: https://newsapi.org/
- **JokeAPI**:
  - Provides random jokes and searches jokes without an API key (free).
  - Source: https://icanhazdadjoke.com/api

---

## Example Prompts 
1. "tell me a joke contains "dreams" and weather of noida"
2. "Give me the top 5 news headlines in technology."
3. "Tell me a random joke."
4. "Search for jokes about programmers and tell me about gta 6"
5. "What happened to dating sites of India?"

---

## Known Limitations / Tradeoffs
- Statelessness: The system treats each query as a new session; it does not currently maintain conversation history (context) between turns.
- API Dependency: Response accuracy and latency are directly tied to the uptime and rate limits of the third-party APIs (OpenWeatherMap, NewsAPI).
- Reasoning Depth: While capable of "what" and "find" queries, deeply analytical queries ("Why is the sky blue?") are limited by the tools available, defaulting to general LLM knowledge which may lack real-time citation.
- Rate Limiting: Heavy usage may trigger API rate limits on the free tiers of the integrated services.
