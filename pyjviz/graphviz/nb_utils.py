import sys, os.path
import warnings
import graphviz
from IPython.display import display, HTML

from ..rdf import fstriplestore
from .viz_utils import replace_a_href_with_onclick, is_nb_run
from .viz import dump_dot_code

warnings.filterwarnings("ignore", category=DeprecationWarning)

def show_diagram(dot_code):
    gvz = graphviz.Source(dot_code)

    output = gvz.pipe(engine="dot", format="svg").decode("ascii")
    mod_output = replace_a_href_with_onclick(output)

    if is_nb_run():
        display(HTML(mod_output))
    else:
        bn = os.path.basename(sys.argv[0])
        dia_num = 0
        while 1:
            dia_num += 1
            out_fn = os.path.join(".", bn + f"-diagram{dia_num}.svg")
            if not os.path.exists(out_fn):
                break
            
        print(f"saving diagram to file {out_fn}")
        with open(out_fn, "w") as out_fd:
            out_fd.write(mod_output)

def show(vertical=False, show_objects=False, popup_output=False):
    ts = fstriplestore.triple_store

    g = ts.get_graph()
    dot_code = dump_dot_code(
        g, vertical=vertical, show_objects=show_objects, popup_output=popup_output
    )
    show_diagram(dot_code)
    ts.clear()
