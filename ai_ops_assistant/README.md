### Objective

Build an AI Operations Assistant that accepts a natural-language task, plans steps, calls tools
(APIs), and returns a final structured answer. The system must run locally and demonstrate
agent-based reasoning, LLM usage, and real API integrations.

## Features

### Streamlit UI (`streamlit_app.py`)
A web-based interface providing access to two main functionalities:

#### 1. OpenWeather API Integration
- Input: City name and OpenWeather API key
- Output: Current weather data including temperature, weather description, and location
- API Endpoint: `https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API key}`

#### 2. Dad Jokes Generator
- Search for dad jokes with customizable parameters
- Inputs: Search term (optional), page number, limit (1-30)
- Output: List of dad jokes matching the search criteria
- API Endpoint: `https://icanhazdadjoke.com/search` with query parameters

#### 3. News Search
- Get latest news articles based on search queries
- Input: Topic or keywords to search for
- Output: Up to 5 recent news articles with titles, descriptions, sources, and URLs
- API Endpoint: `https://newsapi.org/v2/everything`

## Installation

2. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Fill in your API keys

3. Run the AI assistant:
   ```bash
   python main.py
   ```

4. Or run the Streamlit web interface:
   ```bash
   streamlit run streamlit_app.py
   ```

## Requirements

- Python 3.7+
- Streamlit
- Requests library
- LangChain
- LangChain-Groq
- Python-dotenv
- OpenWeather API key (get from https://openweathermap.org/api)
- NewsAPI key (get from https://newsapi.org/)
- Groq API key (get from https://console.groq.com/keys)
- Internet connection for API calls

## Project Structure

```
ai_ops_assistant/
├── main.py                 # Main AI assistant CLI application
├── streamlit_app.py        # Streamlit web interface for APIs
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── README.md              # This file
├── agents/                # AI agent implementation
│   ├── __init__.py
│   └── ai_agent.py
├── llm/                   # LLM integration
│   ├── __init__.py
│   └── llm_client.py
└── tools/                 # API tool implementations
    ├── __init__.py
    ├── weather_tool.py
    ├── dad_jokes_tool.py
    └── news_tool.py
```

