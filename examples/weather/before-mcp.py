#!/usr/bin/env python3
"""
Weather MCP Server - Traditional Approach
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is a Model Context Protocol (MCP) server that wraps the wttr.in weather API.
It demonstrates the typical "enterprise" approach to making weather data available
to an AI agent.

Requirements:
- mcp-sdk (pip install mcp-sdk)
- fastapi (pip install fastapi)
- uvicorn (pip install uvicorn)
- requests (pip install requests)

Lines of code: ~247
Dependencies: 4 external packages
Setup time: ~2 hours
Token overhead: ~430 tokens (schema + documentation)
"""

from mcp import Server, Tool, Resource
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
import requests
import json
import uvicorn
from fastapi import FastAPI, HTTPException

# Initialize MCP server
server = Server(name="weather-server", version="1.0.0")

# ============================================================================
# Schema Definitions (required by MCP)
# ============================================================================

class WeatherInput(BaseModel):
    """Input schema for weather query"""
    city: str = Field(..., description="City name (e.g., 'Boston', 'New York')")
    units: Optional[str] = Field("metric", description="Units: 'metric' or 'imperial'")

class WeatherOutput(BaseModel):
    """Output schema for weather data"""
    city: str
    temperature: float
    condition: str
    humidity: int
    wind_speed: float
    units: str

class WeatherError(BaseModel):
    """Error schema"""
    error: str
    message: str
    code: int

# ============================================================================
# API Integration Layer
# ============================================================================

def fetch_weather_data(city: str) -> Dict:
    """
    Fetch weather data from wttr.in API

    Args:
        city: City name

    Returns:
        Parsed weather data

    Raises:
        HTTPException: If API call fails
    """
    try:
        url = f"https://wttr.in/{city}?format=j1"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=504,
            detail="Weather API timeout"
        )
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=502,
            detail=f"Weather API error: {str(e)}"
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Invalid response from weather API"
        )

def parse_weather_response(data: Dict, city: str, units: str) -> WeatherOutput:
    """
    Parse wttr.in response into our schema

    Args:
        data: Raw API response
        city: Original city query
        units: Temperature units

    Returns:
        Structured weather data
    """
    try:
        current = data["current_condition"][0]

        # Convert temperature based on units
        temp_c = float(current["temp_C"])
        if units == "imperial":
            temperature = (temp_c * 9/5) + 32
        else:
            temperature = temp_c

        return WeatherOutput(
            city=city,
            temperature=temperature,
            condition=current["weatherDesc"][0]["value"],
            humidity=int(current["humidity"]),
            wind_speed=float(current["windspeedKmph"]) if units == "metric" else float(current["windspeedMiles"]),
            units=units
        )
    except (KeyError, IndexError, ValueError) as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse weather data: {str(e)}"
        )

# ============================================================================
# MCP Tool Definition
# ============================================================================

@server.tool(
    name="get_weather",
    description="Get current weather conditions for a specified city",
    parameters=WeatherInput.schema()
)
def get_weather(city: str, units: str = "metric") -> WeatherOutput:
    """
    MCP tool for getting weather data

    This is what agents will call via the MCP protocol.

    Args:
        city: City name
        units: Temperature units (metric or imperial)

    Returns:
        Structured weather data

    Raises:
        HTTPException: Various error conditions
    """
    # Validate units
    if units not in ["metric", "imperial"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid units: {units}. Must be 'metric' or 'imperial'"
        )

    # Fetch and parse data
    raw_data = fetch_weather_data(city)
    weather_data = parse_weather_response(raw_data, city, units)

    return weather_data

# ============================================================================
# Resource Providers (for caching, etc.)
# ============================================================================

@server.resource(uri_template="weather://{city}")
def get_weather_resource(city: str) -> Resource:
    """
    Provide weather as a resource (for caching)
    """
    weather_data = get_weather(city=city, units="metric")
    return Resource(
        uri=f"weather://{city}",
        name=f"Weather for {city}",
        description=f"Current weather conditions in {city}",
        mime_type="application/json",
        content=weather_data.json()
    )

# ============================================================================
# Server Lifecycle
# ============================================================================

@server.on_startup
async def startup():
    """Initialize server resources"""
    print("Weather MCP Server starting...")
    print("Available tools: get_weather")
    print("Available resources: weather://{city}")

@server.on_shutdown
async def shutdown():
    """Clean up resources"""
    print("Weather MCP Server shutting down...")

# ============================================================================
# FastAPI Integration (for serving MCP over HTTP)
# ============================================================================

app = FastAPI(
    title="Weather MCP Server",
    description="Model Context Protocol server for weather data",
    version="1.0.0"
)

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "server": "weather-mcp"}

@app.post("/mcp/call-tool")
async def call_tool(request: Dict):
    """
    MCP tool call endpoint

    This is how agents communicate with the server.
    """
    tool_name = request.get("name")
    parameters = request.get("parameters", {})

    if tool_name == "get_weather":
        try:
            result = get_weather(**parameters)
            return {"result": result.dict()}
        except HTTPException as e:
            return {
                "error": {
                    "code": e.status_code,
                    "message": e.detail
                }
            }
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Tool not found: {tool_name}"
        )

# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║                    Weather MCP Server                          ║
    ║                                                                ║
    ║  This server must run continuously for agents to use it.       ║
    ║                                                                ║
    ║  Usage:                                                        ║
    ║    1. Start this server: python before-mcp.py                  ║
    ║    2. Configure your agent to connect to:                      ║
    ║       http://localhost:8080                                    ║
    ║    3. Agent can now call: get_weather(city="Boston")           ║
    ║                                                                ║
    ║  Dependencies: mcp-sdk, fastapi, uvicorn, requests             ║
    ║  Lines of code: 247                                            ║
    ║  Maintenance: Regular updates as MCP spec evolves              ║
    ╚════════════════════════════════════════════════════════════════╝
    """)

    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )

# ============================================================================
# Agent Configuration (for reference)
# ============================================================================
"""
To use this server, your agent needs this configuration:

{
  "mcpServers": {
    "weather": {
      "url": "http://localhost:8080",
      "tools": [
        {
          "name": "get_weather",
          "description": "Get current weather for a city",
          "parameters": {
            "city": {
              "type": "string",
              "description": "City name (e.g., 'Boston')",
              "required": true
            },
            "units": {
              "type": "string",
              "description": "Units: 'metric' or 'imperial'",
              "default": "metric",
              "required": false
            }
          },
          "returns": {
            "type": "object",
            "properties": {
              "city": {"type": "string"},
              "temperature": {"type": "number"},
              "condition": {"type": "string"},
              "humidity": {"type": "integer"},
              "wind_speed": {"type": "number"},
              "units": {"type": "string"}
            }
          }
        }
      ]
    }
  }
}

This JSON schema (~430 tokens) must be loaded into the agent's context
every time it needs to use the weather tool.
"""
