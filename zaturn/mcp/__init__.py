from fastmcp import FastMCP
from zaturn.mcp import core, visualizations

# Mount modules and make MCP
mcp = FastMCP("Zaturn MCP")
mcp.mount("core", core.mcp)
mcp.mount("visualizations", visualizations.mcp)


def main():
    mcp.run()


def run_studio():
    print('hello')


if __name__=="__main__":
    main()
