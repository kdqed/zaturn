import duckdb
import pandas as pd
import sqlalchemy
from sqlalchemy.orm import Session
from typing import List


def determine_source_type(source: str):
    """Figure out the source type"""
    if source.startswith(('sqlite://', 'mysql://', 'postgresql://')):
        return source.split("://")[0]
    elif source.endswith(".duckdb"):
        return "duckdb"
    elif source.endswith(".csv"):
        return "csv"
    elif source.endswith(".parquet"):
        return "parquet"


def execute_query(source: str, query: str):
    """Run the query using the appropriate engine and read only config"""
    source_type = determine_source_type(source)
    match source_type:
        case "sqlite":
            if "mode=ro" in source:
                pass
            elif '?' in source:
                source += '&mode=ro'
            else:
                source += '?mode=ro'
            with sqlalchemy.create_engine(source).connect() as conn:
                result = conn.execute(sqlalchemy.text(query))
                return pd.DataFrame(result)

        case "mysql":
            engine = sqlalchemy.create_engine(source)
            with Session(engine) as session:
                session.autoflush = False
                session.autocommit = False
                session.flush = lambda *args: None
                result = session.execute(sqlalchemy.text(query))
                return pd.DataFrame(result)

        case "postgresql":
            engine = sqlalchemy.create_engine(source)
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
            conn = duckdb.connect(source, read_only=True)
            return conn.execute(query).df()

        case "csv":
            conn = duckdb.connect(database=':memory:')
            conn.execute(f"CREATE VIEW CSV AS SELECT * FROM read_csv('{source}')")
            return conn.execute(query).df()

        case "parquet":
            conn = duckdb.connect(database=':memory:')
            conn.execute(f"CREATE VIEW PARQUET AS SELECT * FROM read_parquet('{source}')")
            return conn.execute(query).df()
        
        case _:
            raise Exception("Unsupported Source")
    
