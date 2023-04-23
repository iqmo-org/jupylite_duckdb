# Still a work in progress:
# The complexity here is everything is async and cell magics aren't. 
# %%autoawait gave me some ideas. The workaround right now is to 
# monkey patch ipython.transform_cell to rewrite the %%dql
# cell to:
# obj_df = await jd.query(sql=query) 
# 

from IPython.core.magic import register_line_magic, register_cell_magic
from IPython.core import magic_arguments
from IPython.display import display
import ipywidgets as widgets
import jupylite_duckdb as jd
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

    df = jd.query(sql=sql, return_future=False)
    if outputvar is not None: 
        get_ipython().user_ns[outputvar] = df  # type: ignore
    # with s_out:
    #        r = asyncio.get_event_loop().run_until_complete(jd.query(sql=sql, return_future=False))
    #        r.then(functools.partial(display_result, outputvar = outputvar, output=s_out))


def patch_magic():
    # Monkey patching a transformation to stick an "await" ahead of this cell magic
    shell = get_ipython()

    if not hasattr(shell, "_orig_transform_cell"):
        shell._orig_transform_cell = shell.transform_cell

    def jd_transform_cell(*args, **kwargs) -> bool:
        orig_cell = args[0]
        if orig_cell.startswith("%%dql"):
            lines = orig_cell.split("\n")
            first_line=lines[0]
            first_line=first_line.replace("%%dql", "").strip()
            rest = "\\n".join(lines[1:])
            rest=rest.replace("'", "\\'")
            if len(first_line) >0:
                first_line = f"{first_line} = "
            result= f"{first_line}await jd.query(sql='{rest}')"
            print(result)
            return result
        
        result=shell._orig_transform_cell(*args, **kwargs)
        return result
    
    shell.transform_cell = jd_transform_cell
    
patch_magic()
# %%
