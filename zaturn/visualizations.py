from fastmcp import FastMCP, Image
import math
import matplotlib.pyplot as plt
import os
import seaborn as sns
import time
from typing import Any, Union, Optional
from zaturn import config, query_utils

sns.set_theme()
sns.set_style('ticks')

mcp = FastMCP("Zaturn Visualizations")


def _plot_to_image(plot) -> Union[str, Image]:
    figure = plot.get_figure()
    filepath = os.path.join(config.VISUALS_DIR, str(int(time.time())) + '.png')
    figure.savefig(filepath, bbox_inches='tight')
    plt.clf()
    if config.RETURN_IMAGES:
        return Image(path=filepath)
    else:
        return filepath


def _fix_x_labels(plot, labels):
    max_label_length = max(list(labels.map(lambda x: len(str(x)))))

    LABEL_HIDE_FACTOR = 1
    if len(labels) > 20:
        LABEL_HIDE_FACTOR = math.ceil(len(labels)/20)

    labels_to_show = list(labels)
    ticks = list(plot.get_xticks()) 
    if LABEL_HIDE_FACTOR > 1:
        ticks = ticks[::LABEL_HIDE_FACTOR]
        labels_to_show = labels_to_show[::LABEL_HIDE_FACTOR]
            
    plot.set_xticks(ticks, labels_to_show)
    cutoff = 2 # for rotation
    
    if max_label_length >= 12:
        cutoff = 3
    elif max_label_length >= 10:
        cutoff = 4
    elif max_label_length >= 8:
        cutoff = 5
    elif max_label_length >= 7:
        cutoff = 5
    elif max_label_length >= 6:
        cutoff = 6
    elif max_label_length >= 5:
        cutoff = 7
    elif max_label_length >= 4:
        cutoff = 9
    elif max_label_length >= 3:
        cutoff = 13
    else:
        cutoff = 15
    
    if len(labels)>cutoff:
        plot.set_xticklabels(plot.get_xticklabels(), rotation=-45, ha='left', va='top')
    
    return plot


# Relationships

@mcp.tool()
def scatter_plot(
    query_id: str,
    x: str,
    y: str,
    hue: str = None
    ):
    """
    Make a scatter plot with the dataframe obtained from running SQL Query against source
    If this returns an image, display it. If it returns a file path, mention it.
    Args:
        query_id: Previously run query to use for plotting
        x: Column name from SQL result to use for x-axis
        y: Column name from SQL result to use for y-axis
        hue: Optional String; Column name from SQL result to use for coloring the points  
    """
    df = query_utils.load_query(query_id)
    plot = sns.scatterplot(df, x=x, y=y, hue=hue)
    plot = _fix_x_labels(plot, df[x])
    return _plot_to_image(plot)


@mcp.tool()
def line_plot(
    query_id: str,
    x: str,
    y: str,
    hue: str = None
    ):
    """
    Make a line plot with the dataframe obtained from running SQL Query against source
    Args:
        query_id: Previously run query to use for plotting
        x: Column name from SQL result to use for x-axis
        y: Column name from SQL result to use for y-axis
        hue: Optional; column name from SQL result to use for drawing multiple colored lines
    """
    df = query_utils.load_query(query_id)
    plot = sns.lineplot(df, x=x, y=y, hue=hue)
    plot = _fix_x_labels(plot, df[x])
    return _plot_to_image(plot)


# Distributions

@mcp.tool()
def histogram(
    query_id: str,
    column: str,
    hue: str = None,
    bins: int = None
    ):
    """
    Make a histogram with a column of the dataframe obtained from running SQL Query against source
    Args:
        query_id: Previously run query to use for plotting
        column: Column name from SQL result to use for the histogram
        hue: Optional; column name from SQL result to use for drawing multiple colored histograms
        bins: Optional; number of bins
    """
    df = query_utils.load_query(query_id)
    plot = sns.histplot(df, x=column, hue=hue, bins=bins)
    return _plot_to_image(plot)


# Categorical

@mcp.tool()
def strip_plot(
    query_id: str,
    x: str,
    y: str = None,
    hue: str = None,
    legend: bool = False
    ):
    """
    Make a strip plot with the dataframe obtained from running SQL Query against source
    Args:
        query_id: Previously run query to use for plotting
        x: Column name from SQL result to use for x axis
        y: Optional; column name from SQL result to use for y axis
        hue: Optional; column name from SQL result to use for coloring the points
        legend: Whether to draw a legend for the hue
    """
    df = query_utils.load_query(query_id)
    plot = sns.stripplot(df, x=x, y=y, hue=hue, legend=legend)
    plot = _fix_x_labels(plot, df[x])
    return _plot_to_image(plot)


@mcp.tool()
def box_plot(
    query_id: str,
    x: str,
    y: str = None,
    hue: str = None
    ):
    """
    Make a box plot with the dataframe obtained from running SQL Query against source
    Args:
        query_id: Previously run query to use for plotting
        x: Column name from SQL result to use for x axis
        y: Optional; column name from SQL result to use for y axis
        hue: Optional column name from SQL result to use for coloring the points
    """
    df = query_utils.load_query(query_id)
    plot = sns.boxplot(df, x=x, y=y, hue=hue)
    plot = _fix_x_labels(plot, df[x])
    return _plot_to_image(plot)


@mcp.tool()
def bar_plot(
    query_id: str,
    x: str,
    y: str = None,
    hue: str = None,
    orient: str = 'v'
    ):
    """
    Make a bar plot with the dataframe obtained from running SQL Query against source
    Args:
        query_id: Previously run query to use for plotting
        x: Column name from SQL result to use for x axis
        y: Optional; column name from SQL result to use for y axis
        hue: Optional column name from SQL result to use for coloring the bars
        orient: Orientation of the box plot, use 'v' for vertical and 'h' for horizontal
    """
    df = query_utils.load_query(query_id)
    plot = sns.barplot(df, x=x, y=y, hue=hue, orient=orient)
    plot = _fix_x_labels(plot, df[x])
    return _plot_to_image(plot)


