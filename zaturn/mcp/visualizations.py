from fastmcp import FastMCP, Image
import math
import os
import plotly.express as px
import time
from typing import Any, Union, Optional
from zaturn.mcp import config, query_utils


mcp = FastMCP("Zaturn Visualizations")


def _fig_to_image(fig) -> Union[str, Image]:
    filepath = os.path.join(config.VISUALS_DIR, str(int(time.time())) + '.png')
    fig.write_image(filepath)
    if config.RETURN_IMAGES:
        return Image(path=filepath)
    else:
        return filepath
        

# Relationships

@mcp.tool()
def scatter_plot(
    query_id: str,
    x: str,
    y: str,
    color: str = None
    ):
    """
    Make a scatter plot with the dataframe obtained from running SQL Query against source
    If this returns an image, display it. If it returns a file path, mention it.
    Args:
        query_id: Previously run query to use for plotting
        x: Column name from SQL result to use for x-axis
        y: Column name from SQL result to use for y-axis
        color: Optional; column name from SQL result to use for coloring the points, with color representing another dimension
    """
    df = query_utils.load_query(query_id)
    fig = px.scatter(df, x=x, y=y, color=color)
    fig.update_xaxes(autotickangles=[0, 45, 60, 90])
    return _fig_to_image(fig)


@mcp.tool()
def line_plot(
    query_id: str,
    x: str,
    y: str,
    color: str = None
    ):
    """
    Make a line plot with the dataframe obtained from running SQL Query against source
    Args:
        query_id: Previously run query to use for plotting
        x: Column name from SQL result to use for x-axis
        y: Column name from SQL result to use for y-axis
        color: Optional; column name from SQL result to use for drawing multiple colored lines representing another dimension
    """
    df = query_utils.load_query(query_id)
    fig = px.line(df, x=x, y=y, color=color)
    fig.update_xaxes(autotickangles=[0, 45, 60, 90])
    return _fig_to_image(fig)


# Distributions

@mcp.tool()
def histogram(
    query_id: str,
    column: str,
    color: str = None,
    nbins: int = None
    ):
    """
    Make a histogram with a column of the dataframe obtained from running SQL Query against source
    Args:
        query_id: Previously run query to use for plotting
        column: Column name from SQL result to use for the histogram
        color: Optional; column name from SQL result to use for drawing multiple colored histograms representing another dimension
        nbins: Optional; number of bins
    """
    df = query_utils.load_query(query_id)
    fig = px.histogram(df, x=column, color=color, nbins=nbins)
    fig.update_xaxes(autotickangles=[0, 45, 60, 90])
    return _fig_to_image(fig)

# Categorical

@mcp.tool()
def strip_plot(
    query_id: str,
    x: str,
    y: str = None,
    color: str = None
    ):
    """
    Make a strip plot with the dataframe obtained from running SQL Query against source
    Args:
        query_id: Previously run query to use for plotting
        x: Column name from SQL result to use for x axis
        y: Optional; column name from SQL result to use for y axis
        color: Optional column name from SQL result to show multiple colored strips representing another dimension
    """
    df = query_utils.load_query(query_id)
    fig = px.strip(df, x=x, y=y, color=color)
    fig.update_xaxes(autotickangles=[0, 45, 60, 90])
    return _fig_to_image(fig)


@mcp.tool()
def box_plot(
    query_id: str,
    y: str,
    x: str = None,
    color: str = None
    ):
    """
    Make a box plot with the dataframe obtained from running SQL Query against source
    Args:
        query_id: Previously run query to use for plotting
        y: Column name from SQL result to use for y axis
        x: Optional; Column name from SQL result to use for x axis
        color: Optional column name from SQL result to show multiple colored bars representing another dimension
    """
    df = query_utils.load_query(query_id)
    fig = px.box(df, x=x, y=y, color=color)
    fig.update_xaxes(autotickangles=[0, 45, 60, 90])
    return _fig_to_image(fig)


@mcp.tool()
def bar_plot(
    query_id: str,
    x: str,
    y: str = None,
    color: str = None,
    orientation: str = 'v'
    ):
    """
    Make a bar plot with the dataframe obtained from running SQL Query against source
    Args:
        query_id: Previously run query to use for plotting
        x: Column name from SQL result to use for x axis
        y: Optional; column name from SQL result to use for y axis
        color: Optional column name from SQL result to use as a 3rd dimension by splitting each bar into colored sections
        orientation: Orientation of the box plot, use 'v' for vertical (default) and 'h' for horizontal. Be mindful of choosing the correct X and Y columns as per orientation
    """
    df = query_utils.load_query(query_id)
    fig = px.bar(df, x=x, y=y, color=color, orientation=orientation)
    fig.update_xaxes(autotickangles=[0, 45, 60, 90])
    return _fig_to_image(fig)


