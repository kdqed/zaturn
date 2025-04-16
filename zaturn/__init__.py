from fastmcp import FastMCP
from zaturn import core, visualizations

# Mount modules and make MCP
mcp = FastMCP("Zaturn MCP")
mcp.mount("core", core.mcp)
mcp.mount("visualizations", visualizations.mcp)

def main():
    mcp.run()


if __name__=="__main__":
    main()
