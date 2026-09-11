#!/bin/bash
# Launch script for via54ADIdeahub MCP Server
# This script activates the virtual environment and starts the MCP server via stdio
# Used for TRAE MCP integration — configure in TRAE Settings > MCP > Add Server

PROJECT_DIR="/Users/david/Desktop/developments/via54ADIdeahub"
VENV_PYTHON="$PROJECT_DIR/.mcp_venv/bin/python"

exec "$VENV_PYTHON" "$PROJECT_DIR/mcp_server.py"
