"""
Executor Agent - Executes structured plans by calling appropriate tools
Implements retry logic and error handling for API calls
"""

import logging
import time
from typing import Any, Dict, Optional
from agents.base_agent import BaseAgent
from tools import (
    get_current_weather, get_weather_by_coordinates,
    search_news, get_top_headlines,
    get_random_joke, search_jokes
)

logger = logging.getLogger(__name__)


class ExecutorAgent(BaseAgent):
    """Executes structured plans by coordinating weather, news, and jokes tools."""

    def __init__(self):
        super().__init__()
        self.max_retries = 3
        self.retry_delay = 1
        self.tool_handlers = {
            "weather": {
                "get_current_weather": self._execute_weather_city,
                "get_weather_by_coordinates": self._execute_weather_coords
            },
            "news": {
                "search_news": self._execute_search_news,
                "get_top_headlines": self._execute_top_headlines
            },
            "jokes": {
                "get_random_joke": self._execute_random_joke,
                "search_jokes": self._execute_search_jokes
            }
        }
        
    def process(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        return self.execute_plan(plan)

    def execute_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Starting plan execution")

        if not plan.get("steps"):
            return {
                "success": False,
                "step_results": [],
                "error": "No steps in plan"
            }

        step_results = []
        for step in plan.get("steps", []):
            result = self._execute_step(step)
            step_results.append(result)
            
            if result.get("success"):
                logger.info(f"Step {result.get('step_id')} completed successfully")
                if result.get("data", {}).get("fallback"):
                    logger.warning(f"Step {result.get('step_id')} used fallback data")
            else:
                logger.warning(f"Step {result.get('step_id')} failed: {result.get('error')}")

        successful_steps = sum(1 for r in step_results if r.get("success"))
        fallback_count = sum(
            1 for r in step_results 
            if r.get("success") and r.get("data", {}).get("fallback") == True
        )

        return {
            "success": successful_steps > 0,
            "steps_completed": successful_steps,
            "total_steps": len(step_results),
            "fallback_count": fallback_count,
            "step_results": step_results
        }

    def _execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        step_id = step.get("step_id")
        tool = step.get("tool", "").lower()
        function = step.get("function", "").lower()
        parameters = step.get("parameters", {})
        action = step.get("action", "Unknown action")

        logger.info(f"Executing step {step_id}: {action}")

        if tool not in self.tool_handlers:
            return {
                "step_id": step_id,
                "tool": tool,
                "function": function,
                "action": action,
                "success": False,
                "error": f"Unknown tool: {tool}",
                "attempt": 0
            }

        handlers = self.tool_handlers[tool]
        if function not in handlers:
            return {
                "step_id": step_id,
                "tool": tool,
                "function": function,
                "action": action,
                "success": False,
                "error": f"Unknown function: {function}",
                "attempt": 0
            }

        for attempt in range(self.max_retries):
            try:
                handler = handlers[function]
                data = handler(parameters)
                
                if isinstance(data, dict) and "error" in data:
                    logger.warning(f"Attempt {attempt + 1} error: {data.get('error')}")
                    
                    if attempt == self.max_retries - 1:
                        return {
                            "step_id": step_id,
                            "tool": tool,
                            "function": function,
                            "action": action,
                            "success": False,
                            "error": data.get("error", "Unknown error"),
                            "attempt": attempt + 1
                        }
                    
                    wait_time = self.retry_delay * (2 ** attempt)
                    time.sleep(wait_time)
                    continue

                return {
                    "step_id": step_id,
                    "tool": tool,
                    "function": function,
                    "action": action,
                    "success": True,
                    "data": data,
                    "attempt": attempt + 1,
                    "fallback": data.get("fallback", False)
                }

            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} exception: {str(e)}")
                
                if attempt == self.max_retries - 1:
                    return {
                        "step_id": step_id,
                        "tool": tool,
                        "function": function,
                        "action": action,
                        "success": False,
                        "error": str(e),
                        "attempt": attempt + 1
                    }
                
                wait_time = self.retry_delay * (2 ** attempt)
                time.sleep(wait_time)

        return {
            "step_id": step_id,
            "tool": tool,
            "function": function,
            "action": action,
            "success": False,
            "error": "Max retries exceeded",
            "attempt": self.max_retries
        }

    def _execute_weather_city(self, params: Dict[str, Any]) -> Dict[str, Any]:
        city = params.get("city", "")
        if not city:
            return {"error": "City parameter required"}
        return get_current_weather(city)

    def _execute_weather_coords(self, params: Dict[str, Any]) -> Dict[str, Any]:
        lat = params.get("lat")
        lon = params.get("lon")
        if lat is None or lon is None:
            return {"error": "Latitude and longitude parameters required"}
        return get_weather_by_coordinates(lat, lon)

    def _execute_search_news(self, params: Dict[str, Any]) -> Dict[str, Any]:
        query = params.get("query", "")
        limit = params.get("limit", 5)
        language = params.get("language", "en")
        if not query:
            return {"error": "Query parameter required"}
        return search_news(query, limit, language)

    def _execute_top_headlines(self, params: Dict[str, Any]) -> Dict[str, Any]:
        country = params.get("country", "us")
        category = params.get("category")
        limit = params.get("limit", 5)
        return get_top_headlines(country, category, limit)

    def _execute_random_joke(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return get_random_joke()

    def _execute_search_jokes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        query = params.get("query", "")
        limit = params.get("limit", 5)
        if not query:
            return {"error": "Query parameter required"}
        return search_jokes(query, limit)


_executor_instance: Optional[ExecutorAgent] = None


def get_executor() -> ExecutorAgent:
    global _executor_instance
    if _executor_instance is None:
        _executor_instance = ExecutorAgent()
    return _executor_instance