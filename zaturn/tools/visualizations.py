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
            self.line_plot,
            self.histogram,
            self.strip_plot,
            self.box_plot,
            self.bar_plot,

            self.density_heatmap,
            self.polar_scatter,
            self.polar_line,
        ]


    def _get_df_from_source(self, source_id, query):
        source = self.data_sources.get(source_id)
        if not source:
            raise Exception(f"Source {source_id} Not Found")
                
        return query_utils.execute_query(source, query)
            

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
    ) -> str | ImageContent:
        """
        Run query against specified source and make a scatter plot using result
        For both csv and parquet sources, use DuckDB SQL syntax
        Use 'CSV' as the table name in the SQL query for csv sources.
        Use 'PARQUET' as the table name in the SQL query for parquet sources.
    
        This will return an image of the plot
        """

        try:
            df = self._get_df_from_source(source_id, query)
            fig = px.scatter(df, x=x, y=y, color=color)
            fig.update_xaxes(autotickangles=[0, 45, 60, 90])

            return _fig_to_image(fig)
        except Exception as e:
            return str(e)


    def line_plot(self,
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
            str | None, Field(description='Optional; column name from SQL result to use for drawing multiple colored lines representing another dimension')
        ] = None,
    ) -> str | ImageContent:
        """
        Run query against specified source and make a line plot using result
        For both csv and parquet sources, use DuckDB SQL syntax
        Use 'CSV' as the table name in the SQL query for csv sources.
        Use 'PARQUET' as the table name in the SQL query for parquet sources.
    
        This will return an image of the plot
        """

        try:
            df = self._get_df_from_source(source_id, query)
            fig = px.line(df, x=x, y=y, color=color)
            fig.update_xaxes(autotickangles=[0, 45, 60, 90])

            return _fig_to_image(fig)
        except Exception as e:
            return str(e)


    def histogram(self,
        source_id: Annotated[
            str, Field(description='The data source to run the query on')
        ],  
        query: Annotated[
            str, Field(description='SQL query to run on the data source')
        ],
        column: Annotated[
            str, Field(description='Column name from SQL result to use for the histogram')
        ],
        color: Annotated[
            str | None, Field(description='Optional; column name from SQL result to use for drawing multiple colored histograms representing another dimension')
        ] = None,
        nbins: Annotated[
            int | None, Field(description='Optional; number of bins')
        ] = None,
    ) -> str | ImageContent:
        """
        Run query against specified source and make a histogram using result
        For both csv and parquet sources, use DuckDB SQL syntax
        Use 'CSV' as the table name in the SQL query for csv sources.
        Use 'PARQUET' as the table name in the SQL query for parquet sources.
    
        This will return an image of the plot
        """

        try:
            df = self._get_df_from_source(source_id, query)
            fig = px.histogram(df, x=column, color=color, nbins=nbins)
            fig.update_xaxes(autotickangles=[0, 45, 60, 90])

            return _fig_to_image(fig)
        except Exception as e:
            return str(e)


    def strip_plot(self,
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
            str | None, Field(description='Optional column name from SQL result to show multiple colored strips representing another dimension')
        ] = None,
    ) -> str | ImageContent:
        """
        Run query against specified source and make a strip plot using result
        For both csv and parquet sources, use DuckDB SQL syntax
        Use 'CSV' as the table name in the SQL query for csv sources.
        Use 'PARQUET' as the table name in the SQL query for parquet sources.
    
        This will return an image of the plot
        """

        try:
            df = self._get_df_from_source(source_id, query)
            fig = px.strip(df, x=x, y=y, color=color)
            fig.update_xaxes(autotickangles=[0, 45, 60, 90])

            return _fig_to_image(fig)
        except Exception as e:
            return str(e)


    def box_plot(self,
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
            str | None, Field(description='Optional column name from SQL result to show multiple colored bars representing another dimension')
        ] = None,
    ) -> str | ImageContent:
        """
        Run query against specified source and make a box plot using result
        For both csv and parquet sources, use DuckDB SQL syntax
        Use 'CSV' as the table name in the SQL query for csv sources.
        Use 'PARQUET' as the table name in the SQL query for parquet sources.
    
        This will return an image of the plot
        """

        try:
            df = self._get_df_from_source(source_id, query)
            fig = px.box(df, x=x, y=y, color=color)
            fig.update_xaxes(autotickangles=[0, 45, 60, 90])

            return _fig_to_image(fig)
        except Exception as e:
            return str(e)


    def bar_plot(self,
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
            str | None, Field(description='Optional column name from SQL result to use as a 3rd dimension by splitting each bar into colored sections')
        ] = None,
        orientation: Annotated[
            str, Field(description="Orientation of the box plot, use 'v' for vertical (default) and 'h' for horizontal. Be mindful of choosing the correct X and Y columns as per orientation")
        ] = 'v',
    ) -> str | ImageContent:
        """
        Run query against specified source and make a bar plot using result
        For both csv and parquet sources, use DuckDB SQL syntax
        Use 'CSV' as the table name in the SQL query for csv sources.
        Use 'PARQUET' as the table name in the SQL query for parquet sources.
    
        This will return an image of the plot
        """

        try:
            df = self._get_df_from_source(source_id, query)
            fig = px.bar(df, x=x, y=y, color=color, orientation=orientation)
            fig.update_xaxes(autotickangles=[0, 45, 60, 90])

            return _fig_to_image(fig)
        except Exception as e:
            return str(e)


    def density_heatmap(self,
        source_id: Annotated[
            str, Field(description='The data source to run the query on')
        ],  
        query: Annotated[
            str, Field(description='SQL query to run on the data source')
        ],
        column_x: Annotated[
            str, Field(description='Column name from SQL result to use on the X-axis')
        ],
        column_y: Annotated[
            str, Field(description='Column name from SQL result to use on the Y-axis')
        ],
        nbins_x: Annotated[
            int | None, Field(description='Optional; number of bins to use on the X-axis')
        ] = None,
        nbins_y: Annotated[
            int | None, Field(description='Optional; number of bins to use on the Y-axis')
        ] = None,
    ) -> str | ImageContent:
        """
        Run query against specified source and make a 2d-histogram aka. Density Heatmap using result
        For both csv and parquet sources, use DuckDB SQL syntax
        Use 'CSV' as the table name in the SQL query for csv sources.
        Use 'PARQUET' as the table name in the SQL query for parquet sources.
    
        This will return an image of the plot
        """

        try:
            df = self._get_df_from_source(source_id, query)
            fig = px.density_heatmap(df, x=column_x, y=column_y, nbinsx=nbins_x, nbinsy=nbins_y)
            fig.update_xaxes(autotickangles=[0, 45, 60, 90])
            fig.update_yaxes(autotickangles=[0, 45, 60, 90])

            return _fig_to_image(fig)
        except Exception as e:
            return str(e)


    def polar_scatter(self,
        source_id: Annotated[
            str, Field(description='The data source to run the query on')
        ],  
        query: Annotated[
            str, Field(description='SQL query to run on the data source')
        ],
        r: Annotated[
            str, Field(description='Column name from SQL result to use as radial coordinate')
        ],
        theta: Annotated[
            str, Field(description='Column name from SQL result to use as angular coordinate')
        ],
        color: Annotated[
            str | None, Field(description='Optional; column name from SQL result to use for coloring the points, with color representing another dimension')
        ] = None,
    ) -> str | ImageContent:
        """
        Run query against specified source and make a polar scatter plot using result
        For both csv and parquet sources, use DuckDB SQL syntax
        Use 'CSV' as the table name in the SQL query for csv sources.
        Use 'PARQUET' as the table name in the SQL query for parquet sources.
    
        This will return an image of the plot
        """

        try:
            df = self._get_df_from_source(source_id, query)
            fig = px.scatter_polar(df, r=r, theta=theta, color=color)
            
            return _fig_to_image(fig)
        except Exception as e:
            return str(e)


    def polar_line(self,
        source_id: Annotated[
            str, Field(description='The data source to run the query on')
        ],  
        query: Annotated[
            str, Field(description='SQL query to run on the data source')
        ],
        r: Annotated[
            str, Field(description='Column name from SQL result to use as radial coordinate')
        ],
        theta: Annotated[
            str, Field(description='Column name from SQL result to use as angular coordinate')
        ],
        color: Annotated[
            str | None, Field(description='Optional; column name from SQL result to use for drawing multiple colored lines representing another dimension')
        ] = None,
    ) -> str | ImageContent:
        """
        Run query against specified source and make a polar line plot using result
        For both csv and parquet sources, use DuckDB SQL syntax
        Use 'CSV' as the table name in the SQL query for csv sources.
        Use 'PARQUET' as the table name in the SQL query for parquet sources.
    
        This will return an image of the plot
        """

        try:
            df = self._get_df_from_source(source_id, query)
            fig = px.line_polar(df, r=r, theta=theta, color=color, line_close=True)
            
            return _fig_to_image(fig)
        except Exception as e:
            return str(e)


if __name__=="__main__":
    print(ImageContent)
