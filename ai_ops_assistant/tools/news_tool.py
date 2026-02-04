"""
News Tool - Integration with NewsAPI
Provides news search and top headlines retrieval
"""

import os
import logging
from typing import Any, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

from tools.base_tool import BaseTool

logger = logging.getLogger(__name__)

# NewsAPI configuration
NEWS_API_BASE = "https://newsapi.org/v2"
NEWS_API_KEY = os.getenv("NEWS_API_KEY")


class NewsTool(BaseTool):
    """
    News Tool - Integration with NewsAPI.
    
    Provides:
    - News search by keyword
    - Top headlines by country/category
    """

    def __init__(self):
        """Initialize the News Tool."""
        super().__init__(api_base=NEWS_API_BASE, timeout=30.0, cache_ttl=600)
        self.api_key = NEWS_API_KEY
        self.valid_categories = ["business", "entertainment", "general", "health", "science", "sports", "technology"]

    def _validate_api_key(self) -> Optional[str]:
        """Validate that the API key is configured."""
        if not self.api_key or self.api_key == "your_newsapi_key_here":
            return "NewsAPI key not configured. Please set NEWS_API_KEY in your .env file."
        return None

    def _prepare_params(self, **kwargs) -> Dict[str, Any]:
        """
        Prepare request parameters for the NewsAPI.
        
        Args:
            **kwargs: Parameters for the request
            
        Returns:
            Formatted parameters with API key
        """
        params = kwargs.copy()
        params["apiKey"] = self.api_key
        return params

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute news request.
        
        Args:
            **kwargs: Tool-specific parameters (must include 'endpoint')
            
        Returns:
            News data
        """
        error = self._validate_api_key()
        if error:
            return {"error": error}
        
        endpoint = kwargs.pop("endpoint", "everything")
        params = self._prepare_params(**kwargs)
        result = self._make_request(endpoint, params)
        
        # Handle NewsAPI-specific error responses
        if isinstance(result, dict) and result.get("status") == "error":
            return {"error": result.get("message", "Unknown error from NewsAPI")}
        
        return result

    def _format_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format a single article into a clean structure.

        Args:
            article: Raw article data

        Returns:
            Formatted article
        """
        return {
            "title": article.get("title"),
            "description": article.get("description"),
            "source": article.get("source", {}).get("name"),
            "author": article.get("author"),
            "url": article.get("url"),
            "image_url": article.get("urlToImage"),
            "published_at": article.get("publishedAt"),
            "content_preview": article.get("content")
        }

    def search_news(self, query: str, limit: int = 5, language: str = "en") -> Dict[str, Any]:
        """
        Search for news articles by keyword.

        Args:
            query: Search query string
            limit: Maximum number of results to return (default 5, max 100)
            language: Language code (default "en")

        Returns:
            Dictionary containing search results with articles
        """
        logger.info(f"Searching news for: {query}")

        # Ensure limit is within bounds
        limit = min(max(1, limit), 100)
        
        fallback = {
        "success": False,
        "error": "News service unavailable",
        "fallback": True,
        "message": "Unable to fetch news. Try again later.",
        "articles": []
    }

        result = self.execute(
            endpoint="everything",
            q=query,
            language=language,
            sortBy="publishedAt",
            pageSize=limit,
            fallback_data=fallback
        )

        if "error" in result:
            return result

        articles = [
            self._format_article(article)
            for article in result.get("articles", [])[:limit]
        ]

        return {
            "success": True,
            "query": query,
            "total_results": result.get("totalResults", 0),
            "returned_count": len(articles),
            "articles": articles
        }

    def get_top_headlines(
        self,
        country: str = "us",
        category: Optional[str] = None,
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        Get top news headlines for a country and/or category.

        Args:
            country: Two-letter country code (default "us")
            category: News category (business, entertainment, general, health, science, sports, technology)
            limit: Maximum number of results to return (default 5)

        Returns:
            Dictionary containing top headlines
        """
        logger.info(f"Getting top headlines for country: {country}, category: {category}")

        # Validate category if provided
        if category and category.lower() not in self.valid_categories:
            return {
                "error": f"Invalid category. Must be one of: {', '.join(self.valid_categories)}"
            }

        # Ensure limit is within bounds
        limit = min(max(1, limit), 100)

        params = {
            "endpoint": "top-headlines",
            "country": country,
            "pageSize": limit
        }

        if category:
            params["category"] = category.lower()

        result = self.execute(**params)

        if "error" in result:
            return result

        articles = [
            self._format_article(article)
            for article in result.get("articles", [])[:limit]
        ]

        return {
            "success": True,
            "country": country,
            "category": category,
            "total_results": result.get("totalResults", 0),
            "returned_count": len(articles),
            "articles": articles
        }


# Create singleton instance
_news_tool = NewsTool()


def search_news(query: str, limit: int = 5, language: str = "en") -> Dict[str, Any]:
    """Search for news articles by keyword."""
    return _news_tool.search_news(query, limit, language)


def get_top_headlines(
    country: str = "us",
    category: Optional[str] = None,
    limit: int = 5
) -> Dict[str, Any]:
    """Get top news headlines for a country and/or category."""
    return _news_tool.get_top_headlines(country, category, limit)


# Tool metadata for the executor
TOOL_INFO = {
    "name": "news",
    "description": "NewsAPI integration for searching news and getting headlines",
    "functions": {
        "search_news": {
            "description": "Search for news articles by keyword",
            "parameters": ["query", "limit", "language"],
            "handler": search_news
        },
        "get_top_headlines": {
            "description": "Get top news headlines for a country and/or category",
            "parameters": ["country", "category", "limit"],
            "handler": get_top_headlines
        }
    }
}