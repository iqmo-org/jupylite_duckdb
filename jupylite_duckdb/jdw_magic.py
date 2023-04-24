# Still a work in progress:
# The basic problem is properly handling the Pyodide Future. 
# Couldn't handle it in the usual ways (event loop), and simplest solution
# is to "await" the operation. 
# But, since Cell/Line magics don't support async, needed to come up with a way to await them.
# 
# The monkey patch approach patches the iPython line and cell transformers to rewrite the magics directly
# to the syntax we want: "await <function>(params)" 
# instead of its usual behavior which is to rewrite a cell magic to: get_ipython().run_<cell|line>_magic(line, cell)
#
# So, the cell/line magic here is only used for registration purposes... but is never called.
# 
# The last complexity is that there are three paths for rewriting:
# Cell Magics: Cells starting with %%magic
# Line Magics: lines starting with %magic
# Line Magics with Assignment: lines starting with xyz = %magic
#
# Only the first two cases are dealt with here. The assignment case is a bit weird. For now, %dql -o <xyz> instead of xyz = %dql.
# 
# ref: https://github.com/ipython/ipython/blob/main/IPython/core/interactiveshell.py
# https://github.com/ipython/ipython/blob/main/IPython/core/inputtransformer2.py
# 
import warnings

from IPython.core.magic import register_line_magic, register_cell_magic
from IPython.core import magic_arguments
from IPython.display import display
import ipywidgets as widgets
import asyncio
import jupylite_duckdb as jd
import functools
from IPython.core.getipython import get_ipython

import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

DEBUG = True
async def display_result(result, output, outputvar = None):
    with output:
        try:
            if result is None:
                display("Empty Result")
            else:
                if DEBUG:
                    display(f"Output type: {type(result)}")
                display(result)
                if outputvar is not None: 
                    get_ipython().user_ns[outputvar] = result  # type: ignore
        except Exception as e:
            print(e)

@register_line_magic
@register_cell_magic
@magic_arguments.magic_arguments()
@magic_arguments.argument('-o', '--output', nargs=1, help="Output.", type=str)
@magic_arguments.argument('remainder', nargs='*', help='Everything else')
async def dql(line = "", cell = ""):
    outputvar = None
    if line:
        args = magic_arguments.parse_argstring(dql, line)
        if args.output:
            outputvar = args.output[0]
    
    if cell:
        query=cell
    else:
        query=" ".join(args.remainder)
    
    result = await jd.query(query)
    if outputvar:
        get_ipython().user_ns[outputvar] = result
    
    return result

            
def transform_dql_cell(orig_cell: str) -> str:
    # Use find_cell_magic because we don't know the namespace
    lines = orig_cell.split("\n")
    
    first_line=lines[0]
    first_line=first_line.replace("%%dql", "") #.replace("-o", "").strip()
    if len(lines)==1:
        rest = ""
    else:
        rest = "\\n".join(lines[1:])
        rest=rest.replace("'", "\\'")
    
    result= f"await get_ipython().find_cell_magic('dql')(line='{first_line}', cell='{rest}')"
    return result

def patch_transformer():
    
    shell = get_ipython()
    transformermanager = shell.input_transformer_manager
    
    if not hasattr(transformermanager, "_orig_transform_cell"):
        transformermanager._orig_transform_cell = transformermanager.transform_cell
    
    def jd_transform_cell(*args, **kwargs) -> bool:
        orig_cell = args[0]
        
        if orig_cell.startswith("%%dql"):
            return transform_dql_cell(orig_cell)
        else:
            result=get_ipython().input_transformer_manager._orig_transform_cell(*args, **kwargs)
            if "%dql" in orig_cell:
                result = result.replace("get_ipython().run_line_magic('dql',", "await get_ipython().find_line_magic('dql')(line=")
                #print(result)
            return result
    
    transformermanager.transform_cell = jd_transform_cell

def patch_should_run_async():
    shell = get_ipython()
    
    if not hasattr(shell, "_orig_should_run_async"):
        shell._orig_should_run_async = shell.should_run_async
    
    def jd_should_run_async(*args, **kwargs) -> bool:
        orig_cell = args[0]
        if not orig_cell.startswith("%%") and "%dql" in orig_cell:
            return True
        else:
            return shell._orig_should_run_async(*args, **kwargs)
        
    shell.should_run_async = jd_should_run_async
        
patch_transformer()
patch_should_run_async()