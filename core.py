import config
from fastmcp import FastMCP
import os
import query_utils
from typing import Any, List, Union

mcp = FastMCP("Zaturn Core")


@mcp.tool()
def list_sources() -> str:
    """List all available data sources."""
    if not config.SOURCES:
        return "No data sources available. Add sources using the command line parameters."
    
    result = "Available data sources:\n\n"
    for source in config.SOURCES:
        result += f"- {source}\n"
    
    return result    


@mcp.tool()
def list_tables(source: str) -> str:
    """
    Lists names of all tables/datasets in a given data source.
    Use run_query with appropriate SQL query to determine table structure
    
    Args:
        source: The data source to list tables from
    """
    source_type = query_utils.determine_source_type(source)
    match source_type:
        case "sqlite":
            result = query_utils.execute_query(source,
                "SELECT name FROM sqlite_schema WHERE type ='table' AND name NOT LIKE 'sqlite_%';"
            )
            return result['name'].to_list()

        case "postgresql":
            result = query_utils.execute_query(source,
                "SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema';"
            )
            return result['tablename'].to_list()

        case "mysql":
            result = query_utils.execute_query(source, "SHOW TABLES")
            for col in list(result):
                if col.startswith("Tables_in_"):
                    return result[col].to_list()
            
        case "duckdb" | "csv" | "parquet":
            result = query_utils.execute_query(source, "SHOW TABLES")
            return result['name'].to_list()


@mcp.tool()
def run_query(source: str, query: str) -> str:
    """
    Run query against specified source
    For both csv and parquet sources, use DuckDB SQL syntax
    Use 'CSV' as the table name for csv sources.
    Use 'PARQUET' as the table name for parquet sources.

    This will return a query_id, which can be referenced while calling other Zaturn tools.
    Args:
        source: The data source to run the query on
        query: SQL query to run on the data source
    """
    df = query_utils.execute_query(source, query)
    query_id = query_utils.save_query(df)
    return query_id


@mcp.tool()
def show_query_result(query_id) -> str:
    """
    Show stored result for query_id in markdown table format
    """
    df = query_utils.load_query(query_id)
    return df.to_markdown(index=False)
