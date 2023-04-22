# Inspired by: https://github.com/jupyterlite/jupyterlite/issues/237

from IPython.core.magic import register_line_magic, register_cell_magic
from IPython.core import magic_arguments
from IPython.display import display
import ipywidgets as widgets
import asyncio
import jupylite_duckdb as jd
import functools


async def display_result(obj, output):
        with output:
            display(obj)
            
@register_line_magic
@register_cell_magic
@magic_arguments.magic_arguments()
@magic_arguments.argument('query', nargs="+", help="Query.", type=str)
def dql(line = "", cell = ""):
    global connection
    if line:
        args = magic_arguments.parse_argstring(dql, line)
        sql = ' '.join(args.query)

    elif cell:
        sql= cell


    s_out = widgets.Output(layout={'border': '1px solid black'})
    display(s_out)
    with s_out:
        r = asyncio.get_event_loop().run_until_complete(jd.query(sql=sql, return_future=False))
        r.then(functools.partial(display_result, output=s_out))

