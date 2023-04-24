# Experimental
This is highly experimental and will change frequently. 

There are three ways to demo this:
- PyScript: [PyScript + DuckDb](https://raw.githack.com/iqmo-org/jupylite_duckdb/main/pyscript/pyscript_example.html)
- JupyerLite: Open a JupyterLite site, and use the examples from  =[notebooks](https://github.com/iqmo-org/jupylite_duckdb/tree/main/notebooks)
- JupyterLite [Code Console REPL](https://iqmo-org.github.io/jupyterlite_run/repl/?kernel=python&code=print%28%22Installing%20packages%22%29%0A%25pip%20install%20jupylite-duckdb%20--pre%0A%25pip%20install%20plotly%0Aprint%28%22Creating%20DuckDB%20Instance%22%29%0Aimport%20jupylite_duckdb%20as%20duckdb%0Aawait%20duckdb.connect%28%29%0Aprint%28%22Printing%20DuckDB%20Version%22%29%0Adf%20%3D%20await%20duckdb.query%28%22pragma%20version%22%29%0Adisplay%28df%29%0A%0Aimport%20plotly.express%20as%20px%0Ar4%20%3D%20await%20duckdb.query%28%22select%20%2A%20from%20read_csv_auto%28%27https%3A%2F%2Fraw.githubusercontent.com%2Fmwaskom%2Fseaborn-data%2Fmaster%2Firis.csv%27%29%22%29%0Apx.scatter%28r4%2C%20x%3D%22sepal_length%22%2C%20y%3D%22petal_length%22%2C%20color%3D%22species%22%29%0A)
- Pyodide Console: See below
# Demonstration
## Code Console REPL Example
[Code Console REPL](https://iqmo-org.github.io/jupyterlite_run/repl/?kernel=python&code=print%28%22Installing%20packages%22%29%0A%25pip%20install%20jupylite-duckdb%20--pre%0A%25pip%20install%20plotly%0Aprint%28%22Creating%20DuckDB%20Instance%22%29%0Aimport%20jupylite_duckdb%20as%20duckdb%0Aawait%20duckdb.connect%28%29%0Aprint%28%22Printing%20DuckDB%20Version%22%29%0Adf%20%3D%20await%20duckdb.query%28%22pragma%20version%22%29%0Adisplay%28df%29%0A%0Aimport%20plotly.express%20as%20px%0Ar4%20%3D%20await%20duckdb.query%28%22select%20%2A%20from%20read_csv_auto%28%27https%3A%2F%2Fraw.githubusercontent.com%2Fmwaskom%2Fseaborn-data%2Fmaster%2Firis.csv%27%29%22%29%0Apx.scatter%28r4%2C%20x%3D%22sepal_length%22%2C%20y%3D%22petal_length%22%2C%20color%3D%22species%22%29%0A)

## jupyterlite_duckdb_wasm
Python wrapper to run DuckDB_WASM within JupyterLite with a Pyodide Kernel

See [notebooks](https://github.com/iqmo-org/jupylite_duckdb/tree/main/notebooks) for example of running this within [jupyterlite](https://jupyter.org/try-jupyter/lab/)

## Cell Magic %%dql
Following the example of [magic_duckdb](https://github.com/iqmo-org/magic_duckdb), there's an initial proof of concept for a duckdb for JupyterLite. 
See [Magic Example](https://github.com/iqmo-org/jupylite_duckdb/blob/main/notebooks/examples_magics.ipynb)




## Pyodide Console

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

## To Do
- Embed POC in a JupyterLite [Code Console REPL](https://jupyterlite.readthedocs.io/en/latest/quickstart/embed-repl.html)
- Implement a proof of concept version of dataframe registration
- Reduce startup time, probably a combination of the jupyterlite config (preloading modules) and wasm
- Handling errors: detect and display errors in Jupyter: too much sfuff buried in console, such as CORS errors
- invalidate pip browser cache (as/if needed); annoying for development purposes
- think through async/await/transform_cell approach and whether there's a better solution.
## Some development notes
- Zero copy data exchange (js/duckdb arrow -> python/dataframe and python/df -> js/duckdb): Blocked by Pyarrow support
- If you're adding local .py files, use [importlib.invalidate_caches()](https://pyodide.org/en/stable/usage/faq.html#why-can-t-i-import-a-file-i-just-wrote-to-the-file-system). Even then, it was flaky to import.
- Careful with caching... %pip install will pull from browser cache. I had to clear frequently within dev tools
- To clear local storage, which is annoyingly persistent, https://superuser.com/questions/519628/clear-html5-local-storage-on-a-specific-page
- %autoawait is part of why this works in notebooks, which is enabled by default. The %%dql cell magic patches transform-cell to push an await into the cell transformation.: https://ipython.readthedocs.io/en/stable/interactive/autoawait.html