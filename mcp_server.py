import argparse
import sys
import zaturn_mcp

parser = argparse.ArgumentParser(description="Zaturn: A read-only BI tool for analyzing various data sources")
parser.add_argument('sources', nargs=argparse.REMAINDER, default=[], 
                    help='Data source (can be specified multiple times). Can be SQLite, MySQL, PostgreSQL connection string, or a path to CSV, Parquet, or DuckDB file.')

args = parser.parse_args()

if not args.sources:
    print("Error: At least one data source must be provided using the -s flag.")
    print("Example: uv run --directory /path/to/zaturn mcp_server.py sqlite:///mydata.db data.csv")
    sys.exit(1)

zaturn_mcp.sources = args.sources
print("Starting Zaturn MCP Server")
zaturn_mcp.mcp.run()
