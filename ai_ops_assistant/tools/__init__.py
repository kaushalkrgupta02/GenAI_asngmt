"""
Tools Module - External API integrations for the AI Operations Assistant
"""

from .weather_tool import (
    get_current_weather,
    get_weather_by_coordinates,
    TOOL_INFO as WEATHER_TOOL_INFO
)
from .news_tool import (
    search_news,
    get_top_headlines,
    TOOL_INFO as NEWS_TOOL_INFO
)
from .jokes_tool import (
    get_random_joke,
    search_jokes,
    TOOL_INFO as JOKES_TOOL_INFO
)

# Registry of all available tools
TOOLS_REGISTRY = {
    "weather": WEATHER_TOOL_INFO,
    "news": NEWS_TOOL_INFO,
    "jokes": JOKES_TOOL_INFO
}

__all__ = [
    # Weather functions
    "get_current_weather",
    "get_weather_by_coordinates",
    # News functions
    "search_news",
    "get_top_headlines",
    # Jokes functions
    "get_random_joke",
    "search_jokes",
    # Registry
    "TOOLS_REGISTRY"
]