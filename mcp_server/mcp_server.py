#!/usr/bin/env python3
"""MCP Server Implementation for AI Development Lab

This is a proper Model Context Protocol (MCP) server that communicates
via JSON-RPC over stdio, not HTTP endpoints.
"""

import asyncio
import json
import logging
import sys
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    ListToolsResult,
    TextContent,
    Tool,
)

# Configure logging to stderr (critical for MCP stdio)
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create the MCP server
server = Server("ai-dev-lab")

# Import our existing tools
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lab.dsp.summarize import Summarize
from mcp_server.tools.search_docs import search_documents_endpoint

# Initialize the summarizer
summarizer = Summarize()


@server.list_tools()
async def list_tools() -> ListToolsResult:
    """List available tools."""
    return ListToolsResult(
        tools=[
            Tool(
                name="search_docs",
                description="Search documents using semantic similarity",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query",
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of results to return",
                            "default": 5,
                        },
                    },
                    "required": ["query"],
                },
            ),
            Tool(
                name="summarize",
                description="Summarize text content",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "passage": {
                            "type": "string",
                            "description": "The text to summarize",
                        },
                    },
                    "required": ["passage"],
                },
            ),
        ],
    )


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> CallToolResult:
    """Handle tool calls."""
    try:
        if name == "search_docs":
            query = arguments.get("query", "")
            top_k = arguments.get("top_k", 5)

            # Call the existing search function
            result = search_documents_endpoint(query, top_k=top_k)

            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=json.dumps(result, indent=2),
                    ),
                ],
            )

        elif name == "summarize":
            passage = arguments.get("passage", "")

            # Call the existing summarizer
            summary = summarizer(passage)

            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=json.dumps({"summary": summary}, indent=2),
                    ),
                ],
            )

        else:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Unknown tool: {name}",
                    ),
                ],
                isError=True,
            )

    except Exception as e:
        logger.error(f"Error calling tool {name}: {e}")
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Error: {e!s}",
                ),
            ],
            isError=True,
        )


async def main():
    """Main entry point for the MCP server."""
    logger.info("Starting AI Dev Lab MCP Server...")

    # Run the server using stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
