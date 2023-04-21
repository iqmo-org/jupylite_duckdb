# Experimental
This is highly experimental and will change frequently. 

# jupyterlite_duckdb_wasm
Python wrapper to run DuckDB_WASM within JupyterLite with a Pyodide Kernel

See [notebooks](https://github.com/iqmo-org/jupylite_duckdb/tree/main/notebooks) for example of running this within [jupyterlite](https://jupyter.org/try-jupyter/lab/)

## You can also test directly on pyodide

[pyodide console](https://pyodide.org/en/stable/console.html)

```
import micropip;
await micropip.install('pandas');
await micropip.install('jupylite-duckdb');
import jupylite_duckdb as jd;
conn = await jd.connect();
r1 = await jd.query("pragma version", conn);
r2 = await jd.query("create or replace table xyz as select * from 'https://raw.githubusercontent.com/Teradata/kylo/master/samples/sample-data/parquet/userdata2.parquet'", conn);
r3 = await jd.query("select gender, count(*) as c from xyz group by gender", conn);
print(r1);
print(r2);
print(r3);
```