import zaturn_mcp

sources = [
    'sqlite:////home/kd/zaturn/sample_dbs/northwind.db',
    '/home/kd/zaturn/sample_dbs/ny_aq.csv'
]
zaturn_mcp.sources = sources

#t = zaturn_mcp.list_tables(sources[1])
t = zaturn_mcp.run_query(sources[1], "SELECT COUNT(*) FROM CSV;")
print(t)
