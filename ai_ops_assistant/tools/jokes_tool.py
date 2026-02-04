"""
Dad Jokes Tool - Integration with icanhazdadjoke.com API
Provides random and search dad jokes
"""

import os
import logging
from typing import Any, Dict, Optional
import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Dad Jokes API configuration
DAD_JOKES_API_BASE = "https://icanhazdadjoke.com"


def _make_request(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Make a request to the Dad Jokes API.

    Args:
        endpoint: API endpoint
        params: Query parameters

    Returns:
        API response as dictionary
    """
    url = f"{DAD_JOKES_API_BASE}/{endpoint}"
    headers = {"Accept": "application/json"}

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(url, params=params or {}, headers=headers)

            if response.status_code == 404:
                return {"error": "No jokes found for that query."}

            response.raise_for_status()
            return response.json()

    except httpx.TimeoutException:
        logger.error(f"Timeout requesting {endpoint}")
        return {"error": "Request timed out"}
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error: {e}")
        return {"error": f"HTTP error: {e.response.status_code}"}
    except Exception as e:
        logger.error(f"Request failed: {e}")
        return {"error": str(e)}


def get_random_joke() -> Dict[str, Any]:
    """
    Get a random dad joke.

    Returns:
        Dictionary containing the joke
    """
    logger.info("Getting random dad joke")

    result = _make_request("")

    if "error" in result:
        return result

    return {
        "success": True,
        "type": "random",
        "joke": result.get("joke"),
        "id": result.get("id")
    }


def search_jokes(query: str, limit: int = 5) -> Dict[str, Any]:
    """
    Search for dad jokes by keyword.

    Args:
        query: Search query string
        limit: Maximum number of results (default 5)

    Returns:
        Dictionary containing search results
    """
    logger.info(f"Searching dad jokes for: {query}")

    limit = min(max(1, limit), 30)

    params = {
        "search": query,
        "limit": limit
    }

    result = _make_request("search", params)

    if "error" in result:
        return result

    jokes = []
    for item in result.get("results", [])[:limit]:
        jokes.append({
            "joke": item.get("joke"),
            "id": item.get("id")
        })

    return {
        "success": True,
        "type": "search",
        "query": query,
        "total_results": result.get("total_results", 0),
        "jokes": jokes,
        "returned_count": len(jokes)
    }


# Tool metadata for the executor
TOOL_INFO = {
    "name": "jokes",
    "description": "Dad jokes API for getting random jokes and searching",
    "functions": {
        "get_random_joke": {
            "description": "Get a random dad joke",
            "parameters": [],
            "handler": get_random_joke
        },
        "search_jokes": {
            "description": "Search for dad jokes by keyword",
            "parameters": ["query", "limit"],
            "handler": search_jokes
        }
    }
}