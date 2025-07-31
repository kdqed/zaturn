import argparse
import importlib.resources
import os
import platformdirs
import sys

from fastmcp import FastMCP
from fastmcp.tools.tool import Tool

from zaturn.tools import ZaturnTools

# Basic Setup
USER_DATA_DIR = platformdirs.user_data_dir('zaturn', 'zaturn')
SOURCES_FILE = os.path.join(USER_DATA_DIR, 'sources.txt')

# Parse command line args
parser = argparse.ArgumentParser(
    description="Zaturn MCP: A read-only BI tool for analyzing various data sources"
)
parser.add_argument('sources', nargs=argparse.REMAINDER, default=[], 
    help='Data source (can be specified multiple times). Can be SQLite, MySQL, PostgreSQL connection string, or a path to CSV, Parquet, or DuckDB file.'
)
args = parser.parse_args()

source_list = []
if os.path.exists(SOURCES_FILE):
    with open(SOURCES_FILE) as f:
        source_list = [line.strip('\n') for line in f.readlines() if line.strip('\n')]

if not source_list:
    source_list = args.sources

if not source_list:
    with importlib.resources.path(
        'zaturn.tools.example_data', 'all_pokemon_data.csv'
    ) as source_path:
        source_list = [str(source_path)]
    
    print("No data sources provided. Loading example dataset for demonstration.")
    print(f"\nTo load your datasets, add them to {SOURCES_FILE} (one source URL or full file path per line)")
    print("\nOr use command line args to specify data sources:")
    print("zaturn_mcp sqlite:///path/to/mydata.db /path/to/my_file.csv")
    print(f"\nNOTE: Sources in command line args will be ignored if sources are found in {SOURCES_FILE}")

SOURCES = {}
for s in source_list:
    source = s.lower()
    if source.startswith('sqlite://'):
        source_type = 'sqlite'
        source_name = source.split('/')[-1].split('?')[0].split('.db')[0]
    elif source.startswith('postgresql://'):
        source_type = 'postgresql'
        source_name = source.split('/')[-1].split('?')[0]
    elif source.startswith("mysql://") or source.startswith("mysql+pymysql://"):
        source_type = 'mysql'
        s = s.replace('mysql://', 'mysql+pymysql://')
        source_name = source.split('/')[-1].split('?')[0]
    elif source.startswith("mssql://"):
        source_type = 'mssql'
        s = s.replace('mssql://', 'mssql+pymssql://')
        source_name = source.split('/')[-1].split('?')[0]    
    elif source.startswith('clickhouse://'):
        source_type = 'clickhouse'
        source_name = source.split('/')[-1].split('?')[0]
    elif source.endswith(".duckdb"):
        source_type = "duckdb"
        source_name = source.split('/')[-1].split('.')[0]
    elif source.endswith(".csv"):
        source_type = "csv"
        source_name = source.split('/')[-1].split('.')[0]
    elif source.endswith(".parquet") or source.endswith(".pq"):
        source_type = "parquet"
        source_name = source.split('/')[-1].split('.')[0]
    else:
        continue

    source_id = f'{source_name}-{source_type}'
    if source_id in SOURCES:
        i = 2
        while True:
            source_id = f'{source_name}{i}-{source_type}'
            if source_id not in SOURCES:
                break
            i += 1

    SOURCES[source_id] = {'url': s, 'source_type': source_type}


def ZaturnMCP(sources):
    zaturn_tools = ZaturnTools(sources)
    zaturn_mcp = FastMCP()
    for tool_function in zaturn_tools.tools:
        zaturn_mcp.add_tool(Tool.from_function(tool_function))

    return zaturn_mcp


def main():
    ZaturnMCP(SOURCES).run()

