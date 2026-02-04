"""
Executor Agent - Executes structured plans by calling appropriate tools
Implements retry logic and error handling for API calls
"""

import logging
from typing import Any, Dict, Optional
from tools import (
    get_current_weather, get_weather_by_coordinates,
    search_news, get_top_headlines,
    get_random_joke, search_jokes
)

logger = logging.getLogger(__name__)


class ExecutorAgent:
    """
    The Executor Agent is responsible for executing structured plans.
    
    It:
    1. Takes a plan with steps
    2. Executes each step using the appropriate tool
    3. Handles failures with retry logic
    4. Returns results for verification
    """

    def __init__(self):
        """Initialize the Executor Agent."""
        self.max_retries = 3
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

    def execute_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a structured plan.

        Args:
            plan: The execution plan with steps

        Returns:
            Execution result with step_results
        """
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
            
            # Log the result
            if result.get("success"):
                logger.info(f"Step {result.get('step_id')} completed successfully")
            else:
                logger.warning(f"Step {result.get('step_id')} failed: {result.get('error')}")

        # Determine overall success
        successful_steps = sum(1 for r in step_results if r.get("success"))
        total_steps = len(step_results)
        overall_success = successful_steps > 0

        return {
            "success": overall_success,
            "steps_completed": successful_steps,
            "total_steps": total_steps,
            "step_results": step_results
        }

    def _execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single step with retry logic.

        Args:
            step: The step to execute

        Returns:
            Step execution result
        """
        step_id = step.get("step_id")
        tool = step.get("tool", "").lower()
        function = step.get("function", "").lower()
        parameters = step.get("parameters", {})
        action = step.get("action", "Unknown action")

        logger.info(f"Executing step {step_id}: {action}")

        # Try to execute with retries
        for attempt in range(self.max_retries):
            try:
                # Get the handler for this tool and function
                if tool not in self.tool_handlers:
                    return {
                        "step_id": step_id,
                        "tool": tool,
                        "function": function,
                        "action": action,
                        "success": False,
                        "error": f"Unknown tool: {tool}",
                        "attempt": attempt + 1
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
                        "attempt": attempt + 1
                    }

                # Execute the handler
                handler = handlers[function]
                data = handler(parameters)

                return {
                    "step_id": step_id,
                    "tool": tool,
                    "function": function,
                    "action": action,
                    "success": True,
                    "data": data,
                    "attempt": attempt + 1
                }

            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for step {step_id}: {str(e)}")
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

        return {
            "step_id": step_id,
            "tool": tool,
            "function": function,
            "action": action,
            "success": False,
            "error": "Max retries exceeded"
        }

    # Weather tool handlers
    def _execute_weather_city(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute weather query by city."""
        city = params.get("city", "")
        if not city:
            return {"error": "City parameter required"}
        return get_current_weather(city)

    def _execute_weather_coords(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute weather query by coordinates."""
        lat = params.get("lat")
        lon = params.get("lon")
        if lat is None or lon is None:
            return {"error": "Latitude and longitude parameters required"}
        return get_weather_by_coordinates(lat, lon)

    # News tool handlers
    def _execute_search_news(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute news search."""
        query = params.get("query", "")
        limit = params.get("limit", 5)
        language = params.get("language", "en")
        if not query:
            return {"error": "Query parameter required"}
        return search_news(query, limit, language)

    def _execute_top_headlines(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute top headlines query."""
        country = params.get("country", "us")
        category = params.get("category")
        limit = params.get("limit", 5)
        return get_top_headlines(country, category, limit)

    # Jokes tool handlers
    def _execute_random_joke(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute get random joke."""
        return get_random_joke()

    def _execute_search_jokes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute jokes search."""
        query = params.get("query", "")
        limit = params.get("limit", 5)
        if not query:
            return {"error": "Query parameter required"}
        return search_jokes(query, limit)


# Singleton instance
_executor_instance: Optional[ExecutorAgent] = None


def get_executor() -> ExecutorAgent:
    """Get or create the singleton Executor Agent instance."""
    global _executor_instance
    if _executor_instance is None:
        _executor_instance = ExecutorAgent()
    return _executor_instance