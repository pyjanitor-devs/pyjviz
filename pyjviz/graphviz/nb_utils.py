import warnings
import graphviz
from IPython.display import display, HTML
from IPython import get_ipython
from IPython.core.events import pre_run_cell

from . import viz_nodes
from .viz_utils import replace_a_href_with_onclick

warnings.filterwarnings("ignore", category=DeprecationWarning)

def get_cell_id():
    cell_id = get_ipython().parent_header.get("metadata").get("cellId")
    return cell_id


def register_pre_run(my_pre_run_cell):
    # print("register_pre_run")
    get_ipython().events.register("pre_run_cell", my_pre_run_cell)
    return None


def show_method_chain(dot_code):
    gvz = graphviz.Source(dot_code)

    output = gvz.pipe(engine="dot", format="svg").decode("ascii")
    mod_output = replace_a_href_with_onclick(output)
    display(HTML(mod_output))


cell_triplestores_d = {}  # cell_id -> FSTripleOutputOneShot
