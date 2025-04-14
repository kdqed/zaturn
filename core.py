from fastmcp import FastMCP
from typing import Any, List, Union
import source_utils

mcp = FastMCP("Zaturn Core")


@mcp.tool()
def list_sources() -> str:
    """List all available data sources."""
    if not source_utils.sources:
        return "No data sources available. Add sources using the command line parameters."
    
    result = "Available data sources:\n\n"
    for source in source_utils.sources:
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
    source_type = source_utils.determine_source_type(source)
    match source_type:
        case "sqlite":
            result = source_utils.execute_query(source,
                "SELECT name FROM sqlite_schema WHERE type ='table' AND name NOT LIKE 'sqlite_%';"
            )
            return result['name'].to_list()

        case "postgresql":
            result = source_utils.execute_query(source,
                "SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema';"
            )
            return result['tablename'].to_list()

        case "mysql":
            result = source_utils.execute_query(source, "SHOW TABLES")
            for col in list(result):
                if col.startswith("Tables_in_"):
                    return result[col].to_list()
            
        case "duckdb" | "csv" | "parquet":
            result = source_utils.execute_query(source, "SHOW TABLES")
            return result['name'].to_list()


@mcp.tool()
def run_query(source: str, query: str) -> Union[List, str]:
    """
    List all tables/datasets in a given data source.
    For both csv and parquet sources, use DuckDB SQL syntax
    Use 'CSV' as the table name for csv sources.
    Use 'PARQUET' as the table name for parquet sources.
    
    Args:
        source: The data source to run the query on
        query: SQL query to run on the data source
    """
    return source_utils.execute_query(source, query).to_markdown()


