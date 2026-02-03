#!/usr/bin/env python3
"""
API Client - PAS Level 2 Compliant Python Reference Implementation

This is a reference implementation demonstrating how to build a PAS-compliant
CLI tool in Python. It shows proper --agent flag handling, JSON output,
structured errors, and semantic exit codes.

Usage:
  api-client.py [--agent] get <endpoint>
  api-client.py [--agent] post <endpoint> --data <json>
  api-client.py --agent --help
"""

import sys
import json
import argparse
from typing import Any, Dict, Optional
import urllib.request
import urllib.error
import urllib.parse

VERSION = "1.0.0"
BASE_URL = "https://jsonplaceholder.typicode.com"


def show_agent_help():
    """Display concise help for agent mode"""
    help_text = """USAGE:
  api-client.py [--agent] get <endpoint>
  api-client.py [--agent] post <endpoint> --data <json>

COMMON PATTERNS:
  api-client.py --agent get /posts/1              # Get single resource
  api-client.py --agent get /posts                # List resources
  api-client.py --agent post /posts --data '{"title":"Test"}' # Create resource

ERROR CODES:
  0   Success
  1   General error
  2   Invalid arguments
  100 Resource not found (404)
  101 Network error
  102 Timeout
  103 Invalid JSON response

ANTI-PATTERNS:
  api-client.py get /posts     # Use --agent for machine-readable output"""
    print(help_text)


def show_human_help():
    """Display verbose help for human mode"""
    help_text = """API Client v{version}

A simple REST API client demonstrating PAS compliance.

Usage:
  api-client.py [OPTIONS] <command> <endpoint>

Commands:
  get <endpoint>              Fetch a resource
  post <endpoint> --data ...  Create a resource

Options:
  --agent                     Enable agent mode (JSON output)
  --base-url <url>           Base URL (default: {base})
  --timeout <seconds>         Request timeout (default: 10)
  -h, --help                 Show this help

Examples:
  api-client.py get /posts/1
  api-client.py --agent get /posts
  api-client.py post /posts --data '{{"title":"Test"}}'

Agent Mode:
  When --agent is used:
  - Output is pure JSON
  - Errors go to stderr
  - Exit codes are semantic
  - No interactive prompts""".format(version=VERSION, base=BASE_URL)
    print(help_text)


def error(code: int, error_type: str, message: str, agent_mode: bool):
    """Output error and exit"""
    if agent_mode:
        error_obj = {
            "error": error_type,
            "message": message,
            "code": code
        }
        print(json.dumps(error_obj), file=sys.stderr)
    else:
        print(f"Error: {message}", file=sys.stderr)
    sys.exit(code)


def make_request(
    method: str,
    endpoint: str,
    data: Optional[Dict[str, Any]] = None,
    base_url: str = BASE_URL,
    timeout: int = 10,
    agent_mode: bool = False
) -> Dict[str, Any]:
    """Make HTTP request and return parsed JSON"""
    url = base_url.rstrip('/') + '/' + endpoint.lstrip('/')

    try:
        # Prepare request
        headers = {'Content-Type': 'application/json'}
        body = json.dumps(data).encode('utf-8') if data else None

        req = urllib.request.Request(url, data=body, headers=headers, method=method)

        # Make request
        with urllib.request.urlopen(req, timeout=timeout) as response:
            response_data = response.read().decode('utf-8')
            return json.loads(response_data)

    except urllib.error.HTTPError as e:
        if e.code == 404:
            error(100, "NOT_FOUND", f"Resource not found: {endpoint}", agent_mode)
        else:
            error(1, "HTTP_ERROR", f"HTTP {e.code}: {e.reason}", agent_mode)
    except urllib.error.URLError as e:
        error(101, "NETWORK_ERROR", f"Network error: {e.reason}", agent_mode)
    except TimeoutError:
        error(102, "TIMEOUT", f"Request timed out after {timeout}s", agent_mode)
    except json.JSONDecodeError:
        error(103, "INVALID_JSON", "Server returned invalid JSON", agent_mode)
    except Exception as e:
        error(1, "UNEXPECTED_ERROR", str(e), agent_mode)


def main():
    # Parse for --agent flag first
    agent_mode = '--agent' in sys.argv

    # Check for --agent --help
    if agent_mode and ('--help' in sys.argv or '-h' in sys.argv):
        show_agent_help()
        sys.exit(0)

    # Parse arguments
    parser = argparse.ArgumentParser(
        description="PAS-compliant API client",
        add_help=False
    )
    parser.add_argument('--agent', action='store_true', help='Enable agent mode')
    parser.add_argument('--base-url', default=BASE_URL, help='Base URL')
    parser.add_argument('--timeout', type=int, default=10, help='Timeout in seconds')
    parser.add_argument('-h', '--help', action='store_true', help='Show help')
    parser.add_argument('command', nargs='?', choices=['get', 'post'], help='Command')
    parser.add_argument('endpoint', nargs='?', help='API endpoint')
    parser.add_argument('--data', help='JSON data for POST')

    args = parser.parse_args()

    # Handle help
    if args.help:
        if args.agent:
            show_agent_help()
        else:
            show_human_help()
        sys.exit(0)

    # Validate command
    if not args.command:
        error(2, "MISSING_COMMAND", "Command required (get or post)", args.agent)

    if not args.endpoint:
        error(2, "MISSING_ENDPOINT", "Endpoint required", args.agent)

    # Handle POST data
    post_data = None
    if args.command == 'post':
        if not args.data:
            error(2, "MISSING_DATA", "POST requires --data argument", args.agent)
        try:
            post_data = json.loads(args.data)
        except json.JSONDecodeError:
            error(2, "INVALID_JSON", "Data must be valid JSON", args.agent)

    # Make request
    result = make_request(
        method=args.command.upper(),
        endpoint=args.endpoint,
        data=post_data,
        base_url=args.base_url,
        timeout=args.timeout,
        agent_mode=args.agent
    )

    # Output result
    if args.agent:
        # Agent mode: Pure JSON
        print(json.dumps(result))
    else:
        # Human mode: Pretty JSON
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
