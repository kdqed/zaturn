import clickhouse_connect
import duckdb
import numpy as np
import os
import pandas as pd
import sqlalchemy
from sqlalchemy.orm import Session
import time
from typing import List
from zaturn.tools import config


def list_tables(source):
    try:
        match source['source_type']:
            case "sqlite":
                result = execute_query(source,
                    "SELECT name FROM sqlite_schema WHERE type ='table' AND name NOT LIKE 'sqlite_%';"
                )
                return result['name'].to_list()

            case "postgresql":
                result = execute_query(source,
                    "SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema';"
                )
                return result['tablename'].to_list()

            case "mysql":
                result = execute_query(source, "SHOW TABLES")
                for col in list(result):
                    if col.startswith("Tables_in_"):
                        return result[col].to_list()
                
            case "duckdb" | "csv" | "parquet" | "clickhouse":
                result = execute_query(source, "SHOW TABLES")
                return result['name'].to_list()

    except Exception as e:
        return str(e)


def describe_table(source, table_name):
    match source['source_type']:
        case 'sqlite':
            return execute_query(source,
                f'PRAGMA table_info("{table_name}");'
            )
            
        case 'postgresql':
            return execute_query(source,
                f"SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = '{table_name}';"
            )
            
        case "mysql" | "duckdb" | "csv" | "parquet" | "clickhouse":
            if ' ' in table_name:
                table_name = f'`{table_name}`'
                
            return execute_query(source,
                f'DESCRIBE {table_name};'
            )
            

def execute_query(source: dict, query: str):
    """Run the query using the appropriate engine and read only config"""
    url = source['url']
                
    match source['source_type']:
        case "sqlite":
            with sqlalchemy.create_engine(url).connect() as conn:
                conn.execute(sqlalchemy.text('PRAGMA query_only = ON;'))
                result = conn.execute(sqlalchemy.text(query))
                return pd.DataFrame(result)

        case "mysql":
            engine = sqlalchemy.create_engine(url)
            with Session(engine) as session:
                session.autoflush = False
                session.autocommit = False
                session.flush = lambda *args: None
                session.execute(sqlalchemy.text('SET SESSION TRANSACTION READ ONLY;'))
                result = session.execute(sqlalchemy.text(query))
                return pd.DataFrame(result)

        case "postgresql":
            engine = sqlalchemy.create_engine(url)
            with engine.connect() as conn:
                conn = conn.execution_options(
                    isolation_level="SERIALIZABLE",
                    postgresql_readonly=True,
                    postgresql_deferrable=True,
                )
                with conn.begin():
                    result = conn.execute(sqlalchemy.text(query))
                    return pd.DataFrame(result)

        case "clickhouse":
            client = clickhouse_connect.get_client(dsn=url)
            client.query('SET readonly=1;')
            return client.query_df(query, use_extended_dtypes=False)

        case "duckdb":
            conn = duckdb.connect(url, read_only=True)
            return conn.execute(query).df()

        case "csv":
            conn = duckdb.connect(database=':memory:')
            conn.execute(f"CREATE VIEW CSV AS SELECT * FROM read_csv('{url}')")
            return conn.execute(query).df()

        case "parquet":
            conn = duckdb.connect(database=':memory:')
            conn.execute(f"CREATE VIEW PARQUET AS SELECT * FROM read_parquet('{url}')")
            return conn.execute(query).df()
        
        case _:
            raise Exception("Unsupported Source")


def save_query(df: pd.DataFrame):
    """Save query results to disk and return a unique reference id"""
    query_id = 'q' + str(int(time.time()))
    filepath = os.path.join(config.QUERIES_DIR, f'{query_id}.parquet')
    df.replace({np.nan: None}).to_parquet(filepath, engine='pyarrow', index=False)
    return query_id


def load_query(query_id: str):
    """Load query results from disk using unique reference id"""
    filepath = os.path.join(config.QUERIES_DIR, f'{query_id}.parquet')
    df = pd.read_parquet(filepath, engine='pyarrow').replace({np.nan: None})
    df.reset_index(drop=True, inplace=True)
    return df
