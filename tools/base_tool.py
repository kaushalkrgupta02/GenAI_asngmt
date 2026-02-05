# tools/base_tool.py
"""
Base Tool - Abstract base class for all API tools
Provides common HTTP request handling, error management, and caching
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import httpx

logger = logging.getLogger(__name__)


class BaseTool(ABC):
    """
    Abstract base class for all tools.
    
    Provides:
    - Common HTTP request handling
    - Error handling and logging
    - Simple caching mechanism
    - Timeout management
    """

    def __init__(self, api_base: str, timeout: float = 30.0, cache_ttl: int = 300):
        """
        Initialize the Base Tool.
        
        Args:
            api_base: Base URL for the API
            timeout: Request timeout in seconds
            cache_ttl: Cache time-to-live in seconds
        """
        self.api_base = api_base
        self.timeout = timeout
        self.cache_ttl = cache_ttl
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def _validate_api_key(self) -> Optional[str]:
        """
        Validate API key configuration.
        
        Returns:
            Error message if validation fails, None if valid
        """
        pass

    @abstractmethod
    def _prepare_params(self, **kwargs) -> Dict[str, Any]:
        """
        Prepare request parameters for the API.
        
        Should be implemented by subclasses to format params correctly.
        
        Args:
            **kwargs: Tool-specific parameters
            
        Returns:
            Formatted parameters dict
        """
        pass

    def _make_request(
        self,
        endpoint: str,
        params: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
        use_cache: bool = True,
        fallback_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make an HTTP GET request to the API with common error handling.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            headers: Request headers (optional)
            use_cache: Whether to use caching (default True)
            fallback_data: Data to return in case of failure (optional)
            
        Returns:
            API response as dictionary
        """
        # Generate cache key
        cache_key = f"{endpoint}:{str(sorted(params.items()))}"
        
        # Check cache
        if use_cache and cache_key in self.cache:
            cached = self.cache[cache_key]
            if time.time() - cached['time'] < self.cache_ttl:
                self.logger.debug(f"Cache hit for {endpoint}")
                return cached['data']

        url = f"{self.api_base}/{endpoint}"
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, params=params, headers=headers or {})
                
                # Handle common HTTP errors
                if response.status_code == 401:
                    return {"error": "Unauthorized: Invalid API key"}
                elif response.status_code == 404:
                    return {"error": "Not found: The requested resource doesn't exist"}
                elif response.status_code >= 400:
                    return {"error": f"HTTP error: {response.status_code}"}
                
                data = response.json()
                
                # Cache successful response
                if use_cache:
                    self.cache[cache_key] = {'data': data, 'time': time.time()}
                
                return data

        except httpx.TimeoutException:
            error_msg = f"Timeout requesting {endpoint}"
            self.logger.error(error_msg)
            if fallback_data is not None:
                self.logger.info("Returning fallback data due to timeout")
                return fallback_data
            return {"error": error_msg}
        
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error: {e.response.status_code}"
            self.logger.error(error_msg)
            return {"error": error_msg}
        
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.logger.error(error_msg)
            return {"error": error_msg}

    def _is_cached(self, cache_key: str) -> bool:
        """Check if a cache key exists and is still valid."""
        if cache_key not in self.cache:
            return False
        return time.time() - self.cache[cache_key]['time'] < self.cache_ttl

    def clear_cache(self):
        """Clear the cache."""
        self.cache.clear()
        self.logger.info("Cache cleared")

    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool with given parameters.
        
        Should be implemented by subclasses.
        
        Args:
            **kwargs: Tool-specific parameters
            
        Returns:
            Result dictionary
        """
        pass