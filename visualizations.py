from fastmcp import FastMCP, Image
import io
import seaborn as sns
import source_utils
from typing import Any, List, Union

sns.set_theme()

mcp = FastMCP("Zaturn Visualizations")


def _plot_to_image(plot) -> Image:
    buffer = io.BytesIO()
    figure = plot.get_figure()
    figure.savefig(buffer)
    return Image(buffer.getvalue(), format="png")


@mcp.tool()
def histogram(source: str, query: str, column: str) -> Image:
    """
    Make a histogram with a column of the dataframe obtained from running SQL Query against source
    Args:
        source: The data source to run SQL query on
        query: The SQL query to run
        column: Column name from SQL result to use for the histogram
    """
    df = source_utils.execute_query(source, query)
    plot = sns.histplot(df, x=column)
    return _plot_to_image(plot)
