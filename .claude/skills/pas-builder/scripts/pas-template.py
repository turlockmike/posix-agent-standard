#!/usr/bin/env python3
"""
PAS Template Script (Level 2 Compliant)
Copy this template and customize for your tool
"""

import json
import sys
from typing import Dict, Any, Optional

def usage():
    """Print human-readable usage information."""
    print("""Usage: mytool [OPTIONS] <args>

Options:
  --agent          Agent-compatible output (JSON)
  --agent --help   Show agent-optimized help
  -h, --help       Show this help

Examples:
  mytool input.txt
  mytool --agent input.txt
""")

def agent_help():
    """Print agent-optimized help information."""
    print("""USAGE:
  mytool [--agent] <args>

COMMON PATTERNS:
  mytool --agent file.txt              # Process file
  mytool --agent file.txt | jq '.result' # Extract result

ERROR CODES:
  0   Success
  1   General error
  2   Invalid arguments
  100 Resource not found
  101 Permission denied
""")

def output_error(error_type: str, message: str, code: int,
                 agent_mode: bool, suggestion: Optional[str] = None):
    """
    Output an error message and exit with the specified code.

    Args:
        error_type: Machine-readable error type (UPPER_SNAKE_CASE)
        message: Human-readable error description
        code: Exit code to use
        agent_mode: Whether to output JSON
        suggestion: Optional suggestion for fixing the error
    """
    if agent_mode:
        error_obj = {
            "error": error_type,
            "message": message,
            "code": code
        }
        if suggestion:
            error_obj["suggestion"] = suggestion
        print(json.dumps(error_obj), file=sys.stderr)
    else:
        print(f"Error: {message}", file=sys.stderr)
        if suggestion:
            print(f"Tip: {suggestion}", file=sys.stderr)
    sys.exit(code)

def do_work(input_value: str) -> Dict[str, Any]:
    """
    Your tool's actual logic here.

    Args:
        input_value: The input to process

    Returns:
        A dictionary with the results
    """
    # Replace with your actual logic
    return {
        "result": f"processed {input_value}",
        "status": "success"
    }

def main():
    """Main entry point."""
    agent_mode = '--agent' in sys.argv

    # Remove --agent from args for easier processing
    args = [arg for arg in sys.argv[1:] if arg != '--agent']

    # Handle help
    if '-h' in args or '--help' in args:
        if agent_mode:
            agent_help()
        else:
            usage()
        sys.exit(0)

    # Validate arguments
    if len(args) == 0:
        output_error(
            "MISSING_ARGUMENT",
            "No input specified",
            2,
            agent_mode,
            "Provide required arguments"
        )

    input_value = args[0]

    # Example validation: check if input exists
    import os
    if not os.path.exists(input_value):
        output_error(
            "NOT_FOUND",
            f"Input not found: {input_value}",
            100,
            agent_mode
        )

    try:
        # Do the actual work
        result = do_work(input_value)

        # Output based on mode
        if agent_mode:
            print(json.dumps(result))
        else:
            print(f"Success: {result.get('result', 'done')}")

    except Exception as e:
        output_error(
            "PROCESSING_ERROR",
            str(e),
            1,
            agent_mode
        )

if __name__ == "__main__":
    main()
