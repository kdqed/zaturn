from base64 import b64encode
from typing import Any, List, Union, Annotated

from mcp.types import ImageContent
import plotly.express as px
from pydantic import Field

from zaturn.tools import query_utils


def _fig_to_image(fig):
    fig_encoded = b64encode(fig.to_image(format='png')).decode()
    img_b64 = "data:image/png;base64," + fig_encoded
    
    return ImageContent(
        type = 'image',
        data = fig_encoded,
        mimeType = 'image/png',
        annotations = None,
    )


class Visualizations:

    def __init__(self, data_sources): 
        self.data_sources = data_sources
        self.tools = [
            self.scatter_plot,
        ]


    def scatter_plot(self,
        source_id: Annotated[
            str, Field(description='The data source to run the query on')
        ],  
        query: Annotated[
            str, Field(description='SQL query to run on the data source')
        ],
        x: Annotated[
            str, Field(description='Column name from SQL result to use for x-axis')
        ],
        y: Annotated[
            str, Field(description='Column name from SQL result to use for y-axis')
        ],
        color: Annotated[
            str | None, Field(description='Optional; column name from SQL result to use for coloring the points, with color representing another dimension')
        ] = None,
    ) -> str:
        """
        Run query against specified source and make a scatter plot using result
        For both csv and parquet sources, use DuckDB SQL syntax
        Use 'CSV' as the table name in the SQL query for csv sources.
        Use 'PARQUET' as the table name in the SQL query for parquet sources.
    
        This will return an image of the plot
        """

        try:
            source = self.data_sources.get(source_id)
            if not source:
                return f"Source {source_id} Not Found"
                
            df = query_utils.execute_query(source, query)
            fig = px.scatter(df, x=x, y=y, color=color)
            fig.update_xaxes(autotickangles=[0, 45, 60, 90])

            return _fig_to_image(fig)
        except Exception as e:
            return str(e)


if __name__=="__main__":
    print(ImageContent)
