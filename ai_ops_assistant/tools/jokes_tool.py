"""
Jokes API Tool 
Provides random and search dad jokes
"""

import logging
from typing import Any, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

from tools.base_tool import BaseTool

logger = logging.getLogger(__name__)

# Dad Jokes free api
JOKES_API_BASE = "https://icanhazdadjoke.com"


class JokesTool(BaseTool):
    """
    Jokes API Tool 
    
    Provides:
    - Random jokes
    - Search jokes by keyword
    """

    def __init__(self):
        """Initialize the Jokes Tool."""
        super().__init__(api_base=JOKES_API_BASE, timeout=30.0, cache_ttl=600)

    def _validate_api_key(self) -> Optional[str]:
        """
        Validate API key (not required for Dad Jokes API).
        
        Returns:
            None (no API key needed)
        """
        return None

    def _prepare_params(self, **kwargs) -> Dict[str, Any]:
        """
        Prepare request parameters for the Dad Jokes API.
        
        Args:
            **kwargs: Parameters for the request
            
        Returns:
            Formatted parameters
        """
        params = kwargs.copy()
        return params

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute jokes request.
        
        Args:
            **kwargs: Tool-specific parameters (must include 'endpoint')
            
        Returns:
            Jokes data
        """
        endpoint = kwargs.pop("endpoint", "")
        params = self._prepare_params(**kwargs)
        
        headers = {"Accept": "application/json"}
        result = self._make_request(endpoint, params, headers=headers)
        
        return result

    def get_random_joke(self) -> Dict[str, Any]:
        """
        Get a random dad joke.

        Returns:
            Dictionary containing the joke
        """
        logger.info("Getting random dad joke")

        result = self.execute(endpoint="")

        if "error" in result:
            return result

        return {
            "success": True,
            "type": "random",
            "joke": result.get("joke"),
            "id": result.get("id")
        }

    def search_jokes(self, query: str, limit: int = 5) -> Dict[str, Any]:
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

        result = self.execute(
            endpoint="search",
            search=query,
            limit=limit
        )

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


# Create singleton instance
_jokes_tool = JokesTool()


def get_random_joke() -> Dict[str, Any]:
    """Get random joke with fallback."""
    logger.info("Getting random dad joke")
    
    fallback = {
        "success": False,
        "error": "Jokes service unavailable",
        "fallback": True,
        "joke": "Why did the API go to school? To improve its response time!",
        "id": "fallback_001"
    }
    
    result = _jokes_tool.execute(
        endpoint="",
        fallback_data=fallback
    )
    
    if "error" in result:
        return result
    
    return {
        "success": True,
        "type": "random",
        "joke": result.get("joke"),
        "id": result.get("id"),
        "fallback": result.get("fallback", False)
    }


def search_jokes(query: str, limit: int = 5) -> Dict[str, Any]:
    """Search jokes with fallback."""
    logger.info(f"Searching jokes for: {query}")
    
    limit = min(max(1, limit), 30)
    
    fallback = {
        "success": False,
        "error": "Jokes service unavailable",
        "fallback": True,
        "total_results": 0,
        "jokes": [
            {"joke": "Why did the API fail? It had too many issues to handle!", "id": "fallback_001"}
        ]
    }
    
    result = _jokes_tool.execute(
        endpoint="search",
        search=query,
        limit=limit,
        fallback_data=fallback
    )
    
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
        "returned_count": len(jokes),
        "fallback": result.get("fallback", False)
    }


# Tool metadata for the executor
TOOL_INFO = {
    "name": "jokes",
    "description": "Jokes API for getting random jokes and searching",
    "functions": {
        "get_random_joke": {
            "description": "Get a random joke",
            "parameters": [],
            "handler": get_random_joke
        },
        "search_jokes": {
            "description": "Search for jokes by keyword",
            "parameters": ["query", "limit"],
            "handler": search_jokes
        }
    }
}