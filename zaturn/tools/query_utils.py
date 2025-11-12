import os
from typing import List

import clickhouse_connect
import duckdb
from google.oauth2 import service_account
from google.cloud import bigquery
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.orm import Session

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

            case "mssql":
                result = execute_query(source, "SELECT name FROM sys.tables")
                return result['name'].to_list()
                
            case "duckdb" | "csv" | "parquet" | "clickhouse":
                result = execute_query(source, "SHOW TABLES")
                return result['name'].to_list()

            case "bigquery":
                result = execute_query(source, "SELECT table_name FROM INFORMATION_SCHEMA.TABLES")
                return result['table_name'].to_list()

    except Exception as e:
        return str(e)


def describe_table(source, table_name):
    match source['source_type']:
        case 'sqlite':
            return execute_query(source,
                f'PRAGMA table_info("{table_name}");'
            )
            
        case 'postgresql' | 'mssql' | 'bigquery':
            return execute_query(source,
                f"SELECT column_name, data_type, is_nullable FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = '{table_name}';"
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

        case "mssql":
            engine = sqlalchemy.create_engine(url)
            with Session(engine) as session:
                # no known way to ensure read-only here
                # please use read-only credentials
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

        case "bigquery":
            credentials = None
            if config.BIGQUERY_SERVICE_ACCOUNT_FILE:
                credentials = service_account.Credentials.from_service_account_file(
                    config.BIGQUERY_SERVICE_ACCOUNT_FILE,
                )

            chunks = source['url'].split('://')[1].split('/')
            bq_client = bigquery.Client(
                credentials = credentials, 
                default_query_job_config = bigquery.QueryJobConfig(
                    default_dataset = f'{chunks[0]}.{chunks[1]}'
                )
            )
            
            query_job = bq_client.query(query)
            return query_job.result().to_dataframe()
            
        case _:
            raise Exception("Unsupported Source")



