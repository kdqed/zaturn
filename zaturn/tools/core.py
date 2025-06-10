from typing import Any, List, Union, Annotated

from pydantic import Field

from zaturn.tools import query_utils


class Core:

    def __init__(self, data_sources): 
        self.data_sources = data_sources
        self.tools = [
            self.list_data_sources,
            self.describe_table,
            self.run_query,
        ]


    def list_data_sources(self) -> str:
        """
        List all available data sources.
        Returns a list of unique source_ids to be used for other queries.
        Source type is included in the source_id string.
        While drafting SQL queries use appropriate syntax as per source type.
        """
        try:
            if not self.data_sources:
                return "No data sources available. Add data sources."
            
            result = "Available data sources:\n\n"
            for source_id in self.data_sources:
                tables = query_utils.list_tables(
                    self.data_sources[source_id]
                )
                if type(tables) is list:
                    tables = ', '.join(tables)
                result += f"- {source_id}\nHas tables: {tables}\n"
                
            return result
            
        except Exception as e:
            return str(e)


    def describe_table(self, 
        source_id: Annotated[
            str, Field(description='The data source')
        ], 
        table_name: Annotated[
            str, Field(description='The table in the data source')
        ]
    ) -> str:
        """
        Lists columns and their types in the specified table of specified data source.
        """
        
        try:
            source = self.data_sources.get(source_id)
            if not source:
                return f"Source {source_id} Not Found"
    
            result = query_utils.describe_table(source, table_name)
            return result.to_markdown(index=False)
        
        except Exception as e:
            return str(e)


    def run_query(self,
        source_id: Annotated[
            str, Field(description='The data source to run the query on')
        ],  
        query: Annotated[
            str, Field(description='SQL query to run on the data source')
        ]
    ) -> str:
        """
        Run query against specified source
        For both csv and parquet sources, use DuckDB SQL syntax
        Use 'CSV' as the table name for csv sources.
        Use 'PARQUET' as the table name for parquet sources.
    
        This will return a dataframe with the results.
        """
        
        try:
            source = self.data_sources.get(source_id)
            if not source:
                return f"Source {source_id} Not Found"
                
            df = query_utils.execute_query(source, query)
            return df.to_markdown(index=False)
        except Exception as e:
            return str(e)



