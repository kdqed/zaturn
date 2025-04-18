<h1>
  <img src="https://github.com/kdqed/zaturn/raw/main/brand/logo.png" width="24" height="24">
  <span>Zaturn: Your Co-Pilot For Data Analytics & Business Insights</span>
</h1>

Zaturn let's you analyze your data using AI chat; without needing you to write SQL/Python code or fiddling with aesthetically pleasing (but overwhelming) dashboards. You can add Zaturn MCP to Claude Desktop (or any MCP client), connect your data sources, ask questions in natural language, and get instant insights with visualizations. With Zaturn, your AI can automatically understand the kind of data you have, query it, and give you useful pointers with a coherent narrative. You can ask specific questions like "Who is our most valuable customer?", or let AI explore your data with a question like "Here's all the data we have, give us some ideas for the next quarter."

[![PyPI Downloads](https://static.pepy.tech/badge/zaturn)](https://pepy.tech/projects/zaturn) 

[Join The Discord](https://discord.gg/K8mECeVzpQ)


<a href="https://glama.ai/mcp/servers/@kdqed/zaturn">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@kdqed/zaturn/badge" alt="Zaturn MCP server" />
</a>

## But I can just upload my data to ChatGPT and ask it analyze right?

Yes, but ChatGPT has an upload size limit of approximately 50MB for CSV files/spreadsheets, and uploading also takes time. Plus, it can't read data straight from your MySQL or PostgreSQL server. Zaturn can overcome all of these limitations, without moving your data anywhere. It simply equips your AI with SQL and visualization capabilities so AI can query your data directly, get the results, process them, and give you instant insights. With Zaturn, AI does not need to process your full dataset and keep it in its memory to answer your questions about the data.

## Zaturn in Action

https://github.com/user-attachments/assets/d42dc433-e5ec-4b3e-bef0-5cfc097396ab

## Features:

### Multiple Data Sources 
Zaturn can currently connect to the following data sources: 
- SQL Databases: PostgreSQL, SQLite, DuckDB, MySQL
- Files: CSV, Parquet

Connectors for more data sources are being added.

### Visualizations
In addition to providing tabular and textual summaries, Zaturn can also generate the following image visualizations

- Scatter and Line Plots
- Histograms
- Strip and Box Plots
- Bar Plots

> NOTE: The visuals will be shown only if your MCP client supports image rendering (e.g. Claude Desktop)
> 
> If you MCP client does not support images (e.g. Cursor) add the `--noimg` argument in the MCP config. Then the plots will be stored as files and the file location will be returned. You can view the plots with your file browser.

More visualization capabilities are being added.


## Installation & Setup
1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/#installation-methods)

2. Install [Zaturn](https://pypi.org/project/zaturn/) with uv:
```bash
uv tool install zaturn
```

3. Add to MCP config, with data sources:
```json
"mcpServers": {
  "zaturn": {
    "command": "zaturn_mcp",
    "args": [
      "postgresql://username:password@host:port/dbname",
      "mysql+pymysql://username:password@host:3306/dbname",
      "sqlite:////full/path/to/sample_dbs/northwind.db",
      "/full/path/to/sample_dbs/titanic.parquet",
      "/full/path/to/sample_dbs/ny_aq.csv",
      "/full/path/to/sample_dbs/duckdb_sample.duckdb"
    ]
  },
}
```

OR add a `sources.txt` to the Zaturn config directory:
```
postgresql://username:password@host:port/dbname
mysql+pymysql://username:password@host:3306/dbname
sqlite:////full/path/to/sample_dbs/northwind.db
/full/path/to/sample_dbs/titanic.parquet
/full/path/to/sample_dbs/ny_aq.csv
/full/path/to/sample_dbs/duckdb_sample.duckdb
```

This file needs to be at `~/.config/zaturn/sources.txt` on Linux/MacOS and at `%APPDATA%\zaturn\sources.txt` on Windows.

If your MCP client does not support image rendering, add the `--noimg` argument:
```json
...
    "args": [
      "--noimg",
      "mysql+pymysql://username:password@host:3306/dbname",
...
```


4. Set a system prompt if your LLM/IDE allows you to:
```
You are a helpful data analysis assistant. Use only the tool provided data sources to process user inputs. Do not use external sources or your own knowledge base.
```

5. Ask a question and watch the magic:
```
User: List the top 5 customers by revenue for Northwind
AI: 
The top 5 customers by revenue for Northwind are:

1. B's Beverages with a revenue of $6,154,115.34
2. Hungry Coyote Import Store** with a revenue of $5,698,023.67
3. Rancho grande with a revenue of $5,559,110.08
4. Gourmet Lanchonetes with a revenue of $5,552,597.90
5. Ana Trujillo Emparedados y helados with a revenue of $5,534,356.6
```

## Roadmap

- Support for more data source types
- More data visualizations
- Predictive analysis and forecasting, e.g.:
```
Based on the revenue of the last 3 months, forecast next month's revenue.
```
- Generate Presentations & PDFs
```
Manager: 
  I need a presentation to show the boss. Can you do it by EOD?
Analyst: 
  EOD?! Are you still in the 2010s? 
  I can get it done right now. Actually, you can do it right now.
  You know what? The boss can do it right now.
```
- A native notebook interface 

## Support And Feedback

[Raise an issue](https://github.com/kdqed/zaturn/issues) or [join the Discord](https://discord.gg/K8mECeVzpQ).


## Example Dataset Credits

The [pokemon dataset compiled by Sarah Taha and PokéAPI](https://www.kaggle.com/datasets/sarahtaha/1025-pokemon) has been included under the [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) license for demonstration purposes.

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=kdqed/zaturn&type=Date)](https://www.star-history.com/#kdqed/zaturn&Date)
