"""
needs-radar-mcp — Reverse B2B prospecting MCP server from France Travail job postings.

This is a thin entry point for `python server.py` (legacy mode).
The canonical source is the `needs_radar_mcp` package.
"""
from needs_radar_mcp import *  # noqa: F403

if __name__ == "__main__":
    main()
