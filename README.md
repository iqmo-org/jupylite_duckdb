# Experimental
This is experimental and unstable.

# Pyodide + DuckDB

This is a proof of concept at executing duckdb_wasm from a Pyodide kernel. This unlocks a few paths for using duckdb, such as PyScript & JupyterLite. 

** The project should probably be called Pyoduckwasm or something like that... it started with JupyterLite as the end goal. 

# Demonstration:
- [Static PyScript Example](https://raw.githack.com/iqmo-org/jupylite_duckdb/main/pyscript/pyscript_example.html)
- [PyScript REPL](https://raw.githack.com/iqmo-org/jupylite_duckdb/main/pyscript/pyscript_repl.html)
- [pyodide console](https://pyodide.org/en/stable/console.html)
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

- JupyerLite: Open a JupyterLite site, and use the examples from  =[notebooks](https://github.com/iqmo-org/jupylite_duckdb/tree/main/notebooks)
- JupyterLite [Code Console REPL](https://iqmo-org.github.io/jupyterlite_run/repl/?kernel=python&code=print%28%22Installing%20packages%22%29%0A%25pip%20install%20jupylite-duckdb%20--pre%0A%25pip%20install%20plotly%0Aprint%28%22Creating%20DuckDB%20Instance%22%29%0Aimport%20jupylite_duckdb%20as%20duckdb%0Aawait%20duckdb.connect%28%29%0Aprint%28%22Printing%20DuckDB%20Version%22%29%0Adf%20%3D%20await%20duckdb.query%28%22pragma%20version%22%29%0Adisplay%28df%29%0A%0Aimport%20plotly.express%20as%20px%0Ar4%20%3D%20await%20duckdb.query%28%22select%20%2A%20from%20read_csv_auto%28%27https%3A%2F%2Fraw.githubusercontent.com%2Fmwaskom%2Fseaborn-data%2Fmaster%2Firis.csv%27%29%22%29%0Apx.scatter%28r4%2C%20x%3D%22sepal_length%22%2C%20y%3D%22petal_length%22%2C%20color%3D%22species%22%29%0A)

Note: reloading seems somewhat unreliable with pyodide. CTRL-F5 works more reliably. 

Limitations: 
- API: duckdb.connect() and duckdb.query()
- DataFrames are not (yet) registered in the DuckDB database.
- Data is copied from the duckdb_wasm arrow result to a python list[dict], and then to a dataframe. PyArrow is not available (yet) in Pyodide.

# Observations:
- It takes about a minute to run the JupyterLite examples. Most of this time is prior to any DuckDB stuff. Some of this time could be shaved off with a custom pyodide build, but PyScript is much faster.
- JupyterLite was unreliable with page reloads, I ended up having to clear the cache a lot.
- Not thrilled with PyScript removing the top level await... will probably just auto-wrap it (like ipython %autoawait)
# Demonstration
## Code Console REPL Example


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

## Various Issues, Todos and Ideas
- Implement a proof of concept version of dataframe registration
- Evaluate startup time reduction. Probably will never do this, given PyScript. 
- Handling errors: detect and display errors in Jupyter: too much sfuff buried in console, such as CORS errors
- invalidate pip browser cache (as/if needed); annoying for development purposes
- think through async/await/transform_cell approach and whether there's a better solution.
- Zero copy data exchange (js/duckdb arrow -> python/dataframe and python/df -> js/duckdb): Blocked by Pyarrow support
- If you're adding local .py files, use [importlib.invalidate_caches()](https://pyodide.org/en/stable/usage/faq.html#why-can-t-i-import-a-file-i-just-wrote-to-the-file-system). Even then, it was flaky to import.
- Careful with caching... %pip install will pull from browser cache. I had to clear frequently within dev tools
- To clear local storage, which is annoyingly persistent, https://superuser.com/questions/519628/clear-html5-local-storage-on-a-specific-page
- %autoawait is part of why this works in notebooks, which is enabled by default. The %%dql cell magic patches transform-cell to push an await into the cell transformation.: https://ipython.readthedocs.io/en/stable/interactive/autoawait.html
