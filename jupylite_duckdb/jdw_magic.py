# Inspired by: https://github.com/jupyterlite/jupyterlite/issues/237

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

#@register_line_magic
@register_cell_magic
@magic_arguments.magic_arguments()
@magic_arguments.argument('-output', nargs=1, help="Output.", type=str)
#@magic_arguments.argument('query', nargs="+", help="Query.", type=str)
def dql(line = "", cell = ""):
    outputvar = None
    if line:
        args = magic_arguments.parse_argstring(dql, line)
        outputvar = args.output[0]
        #sql = ' '.join(args.query)

    sql = cell

    s_out = widgets.Output(layout={'border': '1px solid black'})
    display(s_out)

    with s_out:
            r = asyncio.get_event_loop().run_until_complete(jd.query(sql=sql, return_future=False))
            r.then(functools.partial(display_result, outputvar = outputvar, output=s_out))