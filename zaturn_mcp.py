from fastmcp import FastMCP
import sys

mcp = FastMCP("Zaturn")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


@mcp.tool()
def get_sources() -> str:
    """Get linked data sources"""
    return '\n'.join(sys.argv[1:])
