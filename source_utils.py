import duckdb
import sqlalchemy


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
                return conn.execute(sqlalchemy.text(query)).fetchall()
                
        case "mysql":
            engine = sqlalchemy.create_engine(source)
            with engine.connect() as conn:
                conn.execute("SET SESSION TRANSACTION READ ONLY")
                return conn.execute(sqlalchemy.text(query)).fetchall()

        case "postgresql":
            engine = sqlalchemy.create_engine(source)
            @sqlalchemy.event.listens_for(engine, "begin")
            def receive_begin(conn):
                conn.execute("SET TRANSACTION READ ONLY")
                
            with engine.connect() as conn:
                return conn.execute(sqlalchemy.text(query)).fetchall()

        case "duckdb":
            conn = duckdb.connect(source, read_only=True)
            return conn.execute(query).fetchall()

        case "csv":
            conn = duckdb.connect(database=':memory:')
            conn.execute(f"CREATE VIEW CSV AS SELECT * FROM read_csv('{source}')")
            return conn.execute(query).fetchall()

        case "parquet":
            conn = duckdb.connect(database=':memory:')
            conn.execute(f"CREATE VIEW PARQUET AS SELECT * FROM read_parquet('{source}')")
            return conn.execute(query).fetchall()
        
        case _:
            raise Exception("Unsupported Source")
    
