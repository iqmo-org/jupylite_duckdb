import js
from pandas import DataFrame
from typing import Optional

async def query(sql: str, connection: object = None) -> DataFrame:
    """Executes query in a standalone connection"""
    if connection is not None:
        result_promise = connection.query(sql)
    else:
        js_function = js.Function('obj', '''
            async function executeSqlDuckdb() {
                    let c = undefined
                    if(obj.connection == undefined) {
                        const duckdb = await import('https://cdn.skypack.dev/@duckdb/duckdb-wasm');
                        const JSDELIVR_BUNDLES = duckdb.getJsDelivrBundles();
                        const bundle = await duckdb.selectBundle(JSDELIVR_BUNDLES);

                        const worker_url = URL.createObjectURL(
                            new Blob([`importScripts("${bundle.mainWorker}");`], { type: 'text/javascript' })
                        );
                        const worker = new Worker(worker_url);
                        const logger = new duckdb.ConsoleLogger();
                        const db = new duckdb.AsyncDuckDB(logger, worker);
                        await db.instantiate(bundle.mainModule, bundle.pthreadWorker);
                        c = await db.connect();
                    }
                    else {
                        c = obj.connection
                    }

                    console.log('Running SQL: ', obj.sql)
                    const sql = obj.sql;
                    const result = await c.query(sql);

                    console.log('Result:', result);
                    return result
                }
            return executeSqlDuckdb()
        ''')

        js_obj = js.Object() 
        js_obj.sql = sql
        js_obj.connection = connection

        result_promise = js_function(js_obj)    # <class 'pyodide.webloop.PyodideFuture'>
    
    obj = await result_promise
    a = obj.toArray()
    data = [dict(v) for v in a.object_values()]

    df = DataFrame(data)
    return df  # <class 'pyodide.ffi.JsProxy'>
    

async def connect() -> object:
    js_function = js.Function('obj', '''
        async function connectDuckdb() {
                console.log("Connecting to " + obj.connectionstr);
                const duckdb = await import('https://cdn.skypack.dev/@duckdb/duckdb-wasm');
                const JSDELIVR_BUNDLES = duckdb.getJsDelivrBundles();
                const bundle = await duckdb.selectBundle(JSDELIVR_BUNDLES);

                const worker_url = URL.createObjectURL(
                    new Blob([`importScripts("${bundle.mainWorker}");`], { type: 'text/javascript' })
                );
                const worker = new Worker(worker_url);
                const logger = new duckdb.ConsoleLogger();
                const db = new duckdb.AsyncDuckDB(logger, worker);
                await db.instantiate(bundle.mainModule, bundle.pthreadWorker);
                const c = await db.connect(obj.connectionstr);

                console.log('Result:', c);

                return c;

            }
        return connectDuckdb()
    ''')

    js_obj = js.Object()
    js_obj.connectionstr = ":memory:"

    result_promise = js_function(js_obj)
    
    connection = await result_promise

    return connection