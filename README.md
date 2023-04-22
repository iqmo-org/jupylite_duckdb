# Experimental
This is highly experimental and will change frequently. 

# jupyterlite_duckdb_wasm
Python wrapper to run DuckDB_WASM within JupyterLite with a Pyodide Kernel

See [notebooks](https://github.com/iqmo-org/jupylite_duckdb/tree/main/notebooks) for example of running this within [jupyterlite](https://jupyter.org/try-jupyter/lab/)

## Cell Magic %%dql
Following the example of [magic_duckdb](https://github.com/iqmo-org/magic_duckdb), there's an initial proof of concept for a duckdb for JupyterLite. 
See [Magic Example](https://github.com/iqmo-org/jupylite_duckdb/blob/main/notebooks/examples_magics.ipynb)

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


## Some development notes
- There's some (well known) CORS considerations when trying to load data from other sites. Examples here are all using public sites, there's some limits that to address with your own jupyterlite deployment 
- If you're adding local .py files, use [importlib.invalidate_caches()](https://pyodide.org/en/stable/usage/faq.html#why-can-t-i-import-a-file-i-just-wrote-to-the-file-system). Even then, it was flaky to import.
- Careful with caching... %pip install will pull from browser cache. I had to clear frequently within dev tools
- To clear local storage, which is annoyingly persistent, https://superuser.com/questions/519628/clear-html5-local-storage-on-a-specific-page
- %autoawait is part of why this works in notebooks, which is enabled by default. The %%dql cell magic patches transform-cell to push an await into the cell transformation.: https://ipython.readthedocs.io/en/stable/interactive/autoawait.html