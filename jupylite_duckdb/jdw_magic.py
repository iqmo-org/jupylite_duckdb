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

from IPython.core.magic import register_line_magic, register_cell_magic
from IPython.core import magic_arguments
from IPython.display import display
import ipywidgets as widgets
import asyncio
import jupylite_duckdb as jd
import functools
from IPython.core.getipython import get_ipython

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
#@magic_arguments.argument('query', nargs="+", help="Query.", type=str)
def dql(line = "", cell = ""):
    raise ValueError("Invalid syntax")
    pass


def transform_dql_line(line: str) -> str:
    outputobj = None
    try:
        if line.startswith("-o"):
            a = line.split(" ")
            if len(a) < 3:
                print("Warning: Missing option after -o or query")
            else:
                outputobj = a[1]
                rest = " ".join(a[2:])
        else:
            rest = line

        if outputobj is not None: 
            pre = f"{outputobj} = "
        else:
            pre = ""

        rest = rest.replace("'", "\'")
        result =  f"{pre}await jd.query(sql='{rest}')\n"
        return result
    except Exception as e:
        print(f"Error {e}")

def transform_dql_cell(orig_cell: str) -> str:
    lines = orig_cell.split("\n")
    first_line=lines[0]
    first_line=first_line.replace("%%dql", "").replace("-o", "").strip()
    rest = "\\n".join(lines[1:])
    rest=rest.replace("'", "\\'")
    if len(first_line) >0:
        first_line = f"{first_line} = "
    result= f"{first_line}await jd.query(sql='{rest}')"
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
            #print(result)
            return result
    
    transformermanager.transform_cell = jd_transform_cell


def patch_magic_assign():
    from IPython.core.inputtransformer2 import MagicAssign
    from typing import List

    if not hasattr(MagicAssign, "_orig_transform"):
        MagicAssign._orig_transform = MagicAssign.transform

    def transform(a, lines: List[str]):
        return a._orig_transform(lines)

    MagicAssign.transform=transform

def patch_tr_magic():
    import IPython.core.inputtransformer2 as it

    if not hasattr(it, "_orig_tr_magic"):
        it._orig_tr_magic = it.tr[it.ESC_MAGIC]

    def _tr_magic(content):
        if content.startswith("dql "):
            result=transform_dql_line(content[4:])
        else:
            result= it._orig_tr_magic(content)
        return result

    it.tr[it.ESC_MAGIC] = _tr_magic
    
patch_transformer()
patch_tr_magic()
# Disabled for now: xyz = %dql won't work. 
# patch_magic_assign()
