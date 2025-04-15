import core
from fastmcp import FastMCP
import visualizations

mcp = FastMCP("Zaturn MCP")
mcp.mount("core", core.mcp)
mcp.mount("visualizations", visualizations.mcp)

mcp.run()
