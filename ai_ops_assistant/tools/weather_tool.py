"""
Weather Tool - Integration with OpenWeatherMap API
Provides current weather information by city name or coordinates
"""

import os
import logging
from typing import Any, Dict, Optional
import httpx
from dotenv import load_dotenv

load_dotenv()

from tools.base_tool import BaseTool

logger = logging.getLogger(__name__)

# OpenWeatherMap API configuration
OPENWEATHER_API_BASE = "https://api.openweathermap.org/data/2.5"
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


class WeatherTool(BaseTool):
    """
    Weather Tool - Integration with OpenWeatherMap API.
    
    Provides:
    - Current weather by city name
    - Current weather by geographic coordinates
    """

    def __init__(self):
        """Initialize the Weather Tool."""
        super().__init__(api_base=OPENWEATHER_API_BASE, timeout=30.0, cache_ttl=300)
        self.api_key = OPENWEATHER_API_KEY

    def _validate_api_key(self) -> Optional[str]:
        """Validate that the API key is configured."""
        if not self.api_key or self.api_key == "your_openweathermap_api_key_here":
            return "OpenWeatherMap API key not configured. Please set OPENWEATHER_API_KEY in your .env file."
        return None

    def _prepare_params(self, **kwargs) -> Dict[str, Any]:
        """
        Prepare request parameters for the OpenWeatherMap API.
        
        Args:
            **kwargs: Parameters for the request
            
        Returns:
            Formatted parameters with API key
        """
        params = kwargs.copy()
        params["appid"] = self.api_key
        return params

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute weather request.
        
        Args:
            **kwargs: Tool-specific parameters
            
        Returns:
            Weather data
        """
        error = self._validate_api_key()
        if error:
            return {"error": error}
        
        params = self._prepare_params(**kwargs)
        return self._make_request("weather", params)

    def get_current_weather_by_city(self, city: str) -> Dict[str, Any]:
        """
        Get current weather for a city.

        Args:
            city: City name (can include country code, e.g., "London,UK")

        Returns:
            Dictionary containing current weather information
        """
        logger.info(f"Getting weather for city: {city}")
        
        fallback = {
        "success": False,
        "error": f"Weather service unavailable for {city}",
        "fallback": True,
        "message": "Please try again later or check weather.com"
        }     

        result = self.execute(
            q=city,
            units="standard",
            fallback_data=fallback  
        )
        
        if "error" in result:
            return result
        
        return self._format_weather_response(result)

    def get_current_weather_by_coordinates(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Get current weather by geographic coordinates.

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            Dictionary containing current weather information
        """
        logger.info(f"Getting weather for coordinates: {lat}, {lon}")

        result = self.execute(lat=lat, lon=lon, units="standard")

        if "error" in result:
            return result

        return self._format_weather_response(result)

    @staticmethod
    def _kelvin_to_celsius(kelvin: float) -> float:
        """Convert Kelvin to Celsius."""
        return round(kelvin - 273.15, 1)

    @staticmethod
    def _kelvin_to_fahrenheit(kelvin: float) -> float:
        """Convert Kelvin to Fahrenheit."""
        return round((kelvin - 273.15) * 9 / 5 + 32, 1)

    def _format_weather_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format the weather API response into a clean structure.

        Args:
            data: Raw API response

        Returns:
            Formatted weather data
        """
        main = data.get("main", {})
        weather = data.get("weather", [{}])[0]
        wind = data.get("wind", {})
        clouds = data.get("clouds", {})
        sys = data.get("sys", {})

        temp_kelvin = main.get("temp", 0)
        feels_like_kelvin = main.get("feels_like", 0)
        temp_min_kelvin = main.get("temp_min", 0)
        temp_max_kelvin = main.get("temp_max", 0)

        return {
            "success": True,
            "location": {
                "city": data.get("name"),
                "country": sys.get("country"),
                "coordinates": {
                    "latitude": data.get("coord", {}).get("lat"),
                    "longitude": data.get("coord", {}).get("lon")
                }
            },
            "weather": {
                "condition": weather.get("main"),
                "description": weather.get("description"),
                "icon": weather.get("icon")
            },
            "temperature": {
                "current": {
                    "celsius": self._kelvin_to_celsius(temp_kelvin),
                    "fahrenheit": self._kelvin_to_fahrenheit(temp_kelvin)
                },
                "feels_like": {
                    "celsius": self._kelvin_to_celsius(feels_like_kelvin),
                    "fahrenheit": self._kelvin_to_fahrenheit(feels_like_kelvin)
                },
                "min": {
                    "celsius": self._kelvin_to_celsius(temp_min_kelvin),
                    "fahrenheit": self._kelvin_to_fahrenheit(temp_min_kelvin)
                },
                "max": {
                    "celsius": self._kelvin_to_celsius(temp_max_kelvin),
                    "fahrenheit": self._kelvin_to_fahrenheit(temp_max_kelvin)
                }
            },
            "humidity": main.get("humidity"),
            "pressure": main.get("pressure"),
            "visibility": data.get("visibility"),
            "wind": {
                "speed_ms": wind.get("speed"),
                "speed_mph": round(wind.get("speed", 0) * 2.237, 1),
                "direction_degrees": wind.get("deg"),
                "gust_ms": wind.get("gust")
            },
            "clouds": {
                "coverage_percent": clouds.get("all")
            },
            "sun": {
                "sunrise_utc": sys.get("sunrise"),
                "sunset_utc": sys.get("sunset")
            },
            "timezone_offset": data.get("timezone")
        }


# Create singleton instance
_weather_tool = WeatherTool()


def get_current_weather(city: str) -> Dict[str, Any]:
    """Get current weather for a city."""
    return _weather_tool.get_current_weather_by_city(city)


def get_weather_by_coordinates(lat: float, lon: float) -> Dict[str, Any]:
    """Get current weather by geographic coordinates."""
    return _weather_tool.get_current_weather_by_coordinates(lat, lon)


# Tool metadata for the executor
TOOL_INFO = {
    "name": "weather",
    "description": "OpenWeatherMap API integration for current weather information",
    "functions": {
        "get_current_weather": {
            "description": "Get current weather for a city",
            "parameters": ["city"],
            "handler": get_current_weather
        },
        "get_weather_by_coordinates": {
            "description": "Get current weather by geographic coordinates",
            "parameters": ["lat", "lon"],
            "handler": get_weather_by_coordinates
        }
    }
}