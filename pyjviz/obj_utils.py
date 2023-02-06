import textwrap
import pandas as pd

from . import fstriplestore
from . import obj_tracking
from . import wb_stack

random_id = 0
def dump_obj_state(obj):
    caller_stack_entry = wb_stack.wb_stack.get_parent_of_current_entry()
    stack_entry = wb_stack.wb_stack.get_top()    
    t_obj, _ = obj_tracking.tracking_store.get_tracking_obj(obj)

    global random_id
    obj_state_uri = f"<ObjState#{random_id}>"; random_id += 1

    fstriplestore.triple_store.dump_triple(obj_state_uri, "rdf:type", "<ObjState>")
    fstriplestore.triple_store.dump_triple(obj_state_uri, "<obj>", t_obj.uri)
    fstriplestore.triple_store.dump_triple(obj_state_uri, "<part-of>", caller_stack_entry.uri)    
    fstriplestore.triple_store.dump_triple(obj_state_uri, "<version>", f'"{t_obj.last_version_num}"')
    t_obj.last_version_num += 1

    output_type = stack_entry.pyjviz_opts.get('obj-state-output-type', None)
    output_type = output_type if output_type else 'head'
    if isinstance(obj, pd.DataFrame):
        dump_DataFrame_obj_state(obj_state_uri, obj, output_type)
    elif isinstance(obj, pd.Series):
        dump_Series_obj_state(obj_state_uri, obj)
    else:
        raise Exception(f"unknown obj type at {obj_state_uri}")

    t_obj.last_obj_state_uri = obj_state_uri
    return t_obj

def dump_DataFrame_obj_state(obj_state_uri, df, output_type):
    fstriplestore.triple_store.dump_triple(obj_state_uri, "<df-shape>", f'"{df.shape}"')
    if output_type == 'head':
        df_head_html = df.head(10).applymap(lambda x: textwrap.shorten(str(x), 50)).to_html().replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("\n", "&#10;")
        fstriplestore.triple_store.dump_triple(obj_state_uri, "<df-head>", '"' + df_head_html + '"')
    elif output_type == 'plot':
        out_fd = io.BytesIO()
        fig = df.plot().get_figure()
        fig.savefig(out_fd)
        fstriplestore.triple_store.dump_triple(obj_state_uri, '<df-plot>', '"' + im_s + '"')
    else:
        raise Exception(f"unknown output_type: {output_type}")


def dump_Series_obj_state(obj_state_uri, s):
    fstriplestore.triple_store.dump_triple(obj_state_uri, "<df-shape>", f'"{s.shape}"')        

