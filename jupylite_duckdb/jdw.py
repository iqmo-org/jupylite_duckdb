import js
from pandas import DataFrame
from typing import Optional
from js import globalThis

# TODO Laundry List
# - Pass arrow from duckdb_wasm to Python efficiently, altho dependent on pyodide pyarrow?
# - Register pandas dataframes with duckdb_wasm: maybe use get_table_names to determine
# what needs to be registered, then register
# - Update connect to take connect(file)
# - 

CONNECTION = None

DEBUG = False

async def future_to_df(result_promise):
    try:
        obj = await result_promise # <class 'pyodide.ffi.JsProxy'>
        a = obj.toArray()
        data = [dict(v) for v in a.object_values()] 

        df = DataFrame(data)
        return df
    except Exception as e:
        print(e)
        return None
    
async def query(sql: str, connection = None, return_future= False) -> DataFrame:
    """Executes query in a standalone connection"""
    if connection is None:
        connection = CONNECTION # if both are None, then a temp db & connection is used
    try:
        if connection is not None:
            result_fut = connection.query(sql)
        else:
            if DEBUG:
                print("Creating a new connection to a temporary database...")
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
                        
                        return await result
                    }
                return executeSqlDuckdb()
            ''')
            js_obj = js.Object() 
            js_obj.sql = sql
            js_obj.connection = connection

            result_fut = js_function(js_obj)    # <class 'pyodide.webloop.PyodideFuture'>

        if return_future: 
            return result_fut
        else:
            return await future_to_df(result_fut)
    except Exception as e:
        print(e)
        return None
    

async def connect() -> object:
    # Other approaches:
    # Store the function in globalThis, instead of creating a new function
    # on connect
    # then access via import GlobalThis; globalThis.connectDuckDb()
    #
    # //  globalThis.connectDuckDb = connectDuckDb;

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

    thisconnection = await result_promise

    global CONNECTION
    CONNECTION = thisconnection
    
    return thisconnection

def register_iiafes():
    syncWrapperConnect_js = js.Function('obj', '''
        function syncWrapperConnect(obj) {
            //delete globalThis.connection;
            (async () => {
                async function executeSqlDuckdb() {
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

                        globalThis.connection=result;
                        return result;
                    }
                try {
      const result = await executeSqlDuckdb();
      // Process the result
      console.log('Result:', result);
      
    } catch (error) {
      // Handle errors
      console.error('Error:', error);
    }
                }
                
            )();
        }
        globalThis.syncWrapperConnect=syncWrapperConnect
    ''')

    syncWrapperConnect_js() # function stored on globalThis.syncWrapperConnect


    
    syncWrapper_query = js.Function('obj', '''
        function syncWrapperQuery(obj) {
            globalThis.result=null;
            (async () => {
                async function executeSqlDuckdb() {
                        //delete globalThis.result;
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
                        globalThis.objresult=result;
                        return result;
                    }
                try {
      const result = await executeSqlDuckdb();
      // Process the result
      console.log('Result:', result);
      
    } catch (error) {
      // Handle errors
      console.error('Error:', error);
    }
                }
                
            )();
        }
        globalThis.syncWrapperQuery=syncWrapperQuery
    ''')
    syncWrapper_query() # function stored on globalThis.syncWrapperQuery

def connect_sync(connstr: str = ":memory:"):

    js_obj_conn = js.Object()
    js_obj_conn.connectionstr = connstr
    globalThis.syncWrapperConnect(js_obj_conn)


def query_sync(sql: str) -> DataFrame:
        
    js_obj_q = js.Object()
    js_obj_q.connection = globalThis.connection
    js_obj_q.sql=sql

    globalThis.syncWrapperQuery(js_obj_q)
    
    a = globalThis.objresult.toArray()
    data = [dict(v) for v in a.object_values()]
    df = DataFrame(data)
    
    return df