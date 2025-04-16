import duckdb
import numpy as np
import os
import pandas as pd
import sqlalchemy
from sqlalchemy.orm import Session
import time
from typing import List
from zaturn import config


def execute_query(source: dict, query: str):
    """Run the query using the appropriate engine and read only config"""
    url = source['url']
    
    match source['type']:
        case "sqlite":
            if "mode=ro" in url:
                pass
            elif '?' in url:
                url += '&mode=ro'
            else:
                url += '?mode=ro'
            with sqlalchemy.create_engine(url).connect() as conn:
                result = conn.execute(sqlalchemy.text(query))
                return pd.DataFrame(result)

        case "mysql":
            engine = sqlalchemy.create_engine(url)
            with Session(engine) as session:
                session.autoflush = False
                session.autocommit = False
                session.flush = lambda *args: None
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
