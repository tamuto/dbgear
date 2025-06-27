"""DBGear MCP Server Entry Point."""

import argparse
import sys
from .server import DBGearMCPServer


def main():
    """Main entry point for the DBGear MCP server."""
    parser = argparse.ArgumentParser(description="DBGear MCP Server")
    parser.add_argument(
        "--project",
        type=str,
        help="Path to the DBGear project directory"
    )
    
    args = parser.parse_args()
    
    try:
        server = DBGearMCPServer(project_path=args.project)
        server.run()
    except Exception as e:
        print(f"Error starting DBGear MCP server: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()