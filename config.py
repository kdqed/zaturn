import argparse
import os
import platformdirs
import sys

# Basic Setup
USER_DATA_DIR = platformdirs.user_data_dir('zaturn', 'zaturn')
QUERIES_DIR = os.path.join(USER_DATA_DIR, 'queries')
VISUALS_DIR = os.path.join(USER_DATA_DIR, 'visuals')

os.makedirs(QUERIES_DIR, exist_ok=True)
os.makedirs(VISUALS_DIR, exist_ok=True)

# Parse command line args
parser = argparse.ArgumentParser(
    description="Zaturn: A read-only BI tool for analyzing various data sources"
)
parser.add_argument('--noimg', action='store_const', 
    const=True, default=False, 
    help='Return image file paths instead of images for visuals. Use when MCP client cannot render images.',
)
parser.add_argument('sources', nargs=argparse.REMAINDER, default=[], 
    help='Data source (can be specified multiple times). Can be SQLite, MySQL, PostgreSQL connection string, or a path to CSV, Parquet, or DuckDB file.'
)
args = parser.parse_args()

# Read sources
SOURCES = args.sources
if not SOURCES:
    print("Error: At least one data source must be provided using the -s flag.")
    print("Example: uv run --directory /path/to/zaturn mcp_server.py sqlite:///mydata.db data.csv")
    sys.exit(1)


# Other Settings
RETURN_IMAGES = not args.noimg

