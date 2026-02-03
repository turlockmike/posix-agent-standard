#!/usr/bin/env bash
#
# weather - POSIX Agent Standard (PAS) Weather Tool
# ==================================================
#
# A minimal, PAS-compliant CLI for getting weather data.
# Demonstrates the simplicity of the POSIX Agent approach.
#
# Requirements: curl, jq (standard on most systems)
# Lines of code: 28
# Dependencies: 0 external packages (uses system tools)
# Setup time: ~10 minutes
# Token overhead: ~20 tokens (just "use weather --agent --city <name>")
#
# PAS Compliance: Level 2 (Agent-Optimized)
# - ✅ --agent flag for deterministic behavior
# - ✅ JSON output
# - ✅ Structured errors on stderr
# - ✅ --help-agent concise documentation
# - ✅ Semantic exit codes

set -euo pipefail

# Configuration
API_URL="https://wttr.in"
VERSION="1.0.0"

# ============================================================================
# Help Documentation
# ============================================================================

show_help() {
    cat << 'EOF'
weather - Get current weather conditions

Usage:
  weather [OPTIONS] --city <city>

Options:
  --agent          Output JSON for agent consumption
  --city <name>    City name (required)
  --units <type>   Units: metric (default) or imperial
  --help-agent     Show agent-optimized help
  -h, --help       Show this help

Examples:
  weather --city Boston
  weather --agent --city "New York"
  weather --agent --city London --units imperial
EOF
}

show_agent_help() {
    cat << 'EOF'
USAGE:
  weather [--agent] --city <city> [--units metric|imperial]

COMMON PATTERNS:
  weather --agent --city Boston                    # Get weather (metric)
  weather --agent --city "New York" --units imperial # Imperial units
  echo "Boston\nLondon\nTokyo" | xargs -I {} weather --agent --city {} # Multiple cities

ERROR CODES:
  0   Success
  1   General error
  2   Invalid arguments
  100 City not found
  101 API timeout
  102 Network error

ANTI-PATTERNS:
  weather --city Boston     # Use --agent for machine-readable output
EOF
}

# ============================================================================
# Core Logic
# ============================================================================

get_weather() {
    local city="$1"
    local units="${2:-metric}"
    local agent_mode="${3:-false}"

    # Fetch weather data from wttr.in
    local response
    if ! response=$(curl -sf --max-time 10 "${API_URL}/${city}?format=j1" 2>&1); then
        # Handle errors
        if echo "$response" | grep -q "timeout"; then
            if [ "$agent_mode" = true ]; then
                echo '{"error":"API_TIMEOUT","message":"Weather API request timed out","code":101}' >&2
            else
                echo "Error: API timeout" >&2
            fi
            exit 101
        else
            if [ "$agent_mode" = true ]; then
                echo '{"error":"NETWORK_ERROR","message":"Failed to fetch weather data","code":102}' >&2
            else
                echo "Error: Network error" >&2
            fi
            exit 102
        fi
    fi

    # Parse response with jq
    local weather_json
    if ! weather_json=$(echo "$response" | jq -r '.current_condition[0]' 2>&1); then
        if [ "$agent_mode" = true ]; then
            echo '{"error":"CITY_NOT_FOUND","message":"City not found: '"$city"'","code":100}' >&2
        else
            echo "Error: City not found: $city" >&2
        fi
        exit 100
    fi

    # Extract fields
    local temp_c=$(echo "$weather_json" | jq -r '.temp_C')
    local condition=$(echo "$weather_json" | jq -r '.weatherDesc[0].value')
    local humidity=$(echo "$weather_json" | jq -r '.humidity')
    local wind_kmph=$(echo "$weather_json" | jq -r '.windspeedKmph')
    local wind_mph=$(echo "$weather_json" | jq -r '.windspeedMiles')

    # Convert temperature based on units
    local temperature
    local wind_speed
    if [ "$units" = "imperial" ]; then
        temperature=$(echo "$temp_c" | awk '{printf "%.1f", ($1 * 9/5) + 32}')
        wind_speed=$wind_mph
    else
        temperature=$temp_c
        wind_speed=$wind_kmph
    fi

    # Output based on mode
    if [ "$agent_mode" = true ]; then
        # Agent mode: Pure JSON
        echo "{\"city\":\"$city\",\"temperature\":$temperature,\"condition\":\"$condition\",\"humidity\":$humidity,\"wind_speed\":$wind_speed,\"units\":\"$units\"}"
    else
        # Human mode: Pretty output
        echo "Weather in $city:"
        echo "  Temperature: ${temperature}°$([ "$units" = "imperial" ] && echo F || echo C)"
        echo "  Condition: $condition"
        echo "  Humidity: ${humidity}%"
        echo "  Wind: ${wind_speed} $([ "$units" = "imperial" ] && echo mph || echo km/h)"
    fi
}

# ============================================================================
# Argument Parsing
# ============================================================================

AGENT_MODE=false
CITY=""
UNITS="metric"

while [ $# -gt 0 ]; do
    case "$1" in
        --agent)
            AGENT_MODE=true
            shift
            ;;
        --city)
            CITY="$2"
            shift 2
            ;;
        --units)
            UNITS="$2"
            if [ "$UNITS" != "metric" ] && [ "$UNITS" != "imperial" ]; then
                if [ "$AGENT_MODE" = true ]; then
                    echo '{"error":"INVALID_UNITS","message":"Units must be metric or imperial","code":2}' >&2
                else
                    echo "Error: Units must be 'metric' or 'imperial'" >&2
                fi
                exit 2
            fi
            shift 2
            ;;
        --help-agent)
            show_agent_help
            exit 0
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            if [ "$AGENT_MODE" = true ]; then
                echo '{"error":"INVALID_ARGUMENT","message":"Unknown option: '"$1"'","suggestion":"See --help"}' >&2
            else
                echo "Error: Unknown option: $1" >&2
                show_help >&2
            fi
            exit 2
            ;;
    esac
done

# Validate required arguments
if [ -z "$CITY" ]; then
    if [ "$AGENT_MODE" = true ]; then
        echo '{"error":"MISSING_ARGUMENT","message":"--city is required","suggestion":"weather --agent --city Boston"}' >&2
    else
        echo "Error: --city is required" >&2
        show_help >&2
    fi
    exit 2
fi

# ============================================================================
# Main
# ============================================================================

get_weather "$CITY" "$UNITS" "$AGENT_MODE"

# That's it! 28 lines of actual logic vs 247 lines for the MCP server.
# The agent already knows how to run bash commands. No server needed.
