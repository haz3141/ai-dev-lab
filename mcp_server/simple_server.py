#!/usr/bin/env python3
"""Minimal MCP Server for testing - implements the KISS baseline"""

import asyncio
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

# Import search tool
from mcp_server.tools.search_docs import search_documents_endpoint

# Import summarize tool
from mcp_server.tools.summarize import summarize_text

# Configure logging to stderr (critical for MCP stdio)
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create the MCP server
server = Server("lab-server")


@server.list_tools()
async def list_tools() -> ListToolsResult:
    """List available tools."""
    return ListToolsResult(
        tools=[
            Tool(
                name="ping",
                description="Health check tool; returns the input message",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "The message to return",
                            "default": "ok",
                        },
                    },
                    "required": [],
                },
            ),
            Tool(
                name="search_docs",
                description="Search documents using embedding similarity",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query text",
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of top results to return",
                            "default": 5,
                            "minimum": 1,
                            "maximum": 20,
                        },
                    },
                    "required": ["query"],
                },
            ),
            Tool(
                name="summarize",
                description="Summarize text using DSPy or fallback methods",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Text to summarize",
                        },
                        "max_length": {
                            "type": "integer",
                            "description": "Maximum length of summary",
                            "default": 100,
                            "minimum": 10,
                            "maximum": 500,
                        },
                    },
                    "required": ["text"],
                },
            ),
        ],
    )


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> CallToolResult:
    """Handle tool calls."""
    try:
        if name == "ping":
            message = arguments.get("message", "ok")
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=message,
                    ),
                ],
            )
        elif name == "search_docs":
            query = arguments.get("query", "")
            top_k = arguments.get("top_k", 5)

            if not query:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text="Error: query parameter is required",
                        ),
                    ],
                    isError=True,
                )

            # Call the search function
            search_result = search_documents_endpoint(query, top_k)

            # Format the result as JSON string
            import json

            result_text = json.dumps(search_result, indent=2)

            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=result_text,
                    ),
                ],
            )
        elif name == "summarize":
            text = arguments.get("text", "")
            max_length = arguments.get("max_length", 100)

            if not text:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text="Error: text parameter is required",
                        ),
                    ],
                    isError=True,
                )

            # Call the summarize function
            summarize_result = summarize_text(text, max_length)

            # Format the result as JSON string
            import json

            result_text = json.dumps(summarize_result, indent=2)

            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=result_text,
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
    logger.info("Starting Lab MCP Server (minimal)...")

    # Run the server using stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
