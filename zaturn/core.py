from fastmcp import FastMCP
import os
from typing import Any, List, Union
from zaturn import config, query_utils

mcp = FastMCP("Zaturn Core")


@mcp.tool()
def list_sources() -> str:
    """
    List all available data sources.
    Returns a list of unique source_ids to be used for other queries.
    Source type is included in the source_id string.
    While drafting SQL queries use appropriate syntax as per source type.
    """
    try:
        if not config.SOURCES:
            return "No data sources available. Add sources using the command line parameters."
        
        result = "Available data sources:\n\n"
        for source in config.SOURCES:
            tables = _list_tables(source)
            if type(tables) is List:
                tables = ', '.join(tables)
            result += f"- {source}\nHas tables: {tables}\n"
    
        return result
    except Exception as e:
        return str(e)


def _list_tables(source_id: str):
    """
    Lists names of all tables/datasets in a given data source.
    Use run_query with appropriate SQL query to determine table structure
    
    Args:
        source_id: The data source to list tables from
    """
    try:
        source = config.SOURCES.get(source_id)
        if not source:
            return f"Source {source_id} Not Found"

        match source['type']:
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
                
            case "duckdb" | "csv" | "parquet" | "clickhouse":
                result = query_utils.execute_query(source, "SHOW TABLES")
                return result['name'].to_list()

    except Exception as e:
        return str(e)

@mcp.tool()
def describe_table(source_id: str, table_name: str) -> str:
    """
    Lists columns and their types in the specified table of specified data source.

    Args:
        source_id: The data source
        table_name: The table in the data source
    """
    try:
        source = config.SOURCES.get(source_id)
        if not source:
            return f"Source {source_id} Not Found"

        match source['type']:
            case 'sqlite':
                result = query_utils.execute_query(source,
                    f'PRAGMA table_info({table_name});'
                )
                return result.to_markdown(index=False)
                
            case 'postgresql':
                result = query_utils.execute_query(source,
                    f"SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = '{table_name}';"
                )
                return result.to_markdown(index=False)
                
            case "mysql" | "duckdb" | "csv" | "parquet" | "clickhouse":
                result = query_utils.execute_query(source,
                    f"DESCRIBE {table_name};"
                )
                return result.to_markdown(index=False)
    
    except Exception as e:
        return str(e)
            

@mcp.tool()
def run_query(source_id: str, query: str) -> str:
    """
    Run query against specified source
    For both csv and parquet sources, use DuckDB SQL syntax
    Use 'CSV' as the table name for csv sources.
    Use 'PARQUET' as the table name for parquet sources.

    This will return a query_id, which can be referenced while calling other Zaturn tools.
    Args:
        source_id: The data source to run the query on
        query: SQL query to run on the data source
    """
    try:
        source = config.SOURCES.get(source_id)
        if not source:
            return f"Source {source_id} Not Found"
            
        df = query_utils.execute_query(source, query)
        query_id = query_utils.save_query(df)
        return query_id
    except Exception as e:
        return str(e)


@mcp.tool()
def show_query_result(query_id) -> str:
    """
    Show stored result for query_id in markdown table format
    """
    df = query_utils.load_query(query_id)
    return df.to_markdown(index=False)
