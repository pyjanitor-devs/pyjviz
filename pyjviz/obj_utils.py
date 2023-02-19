import textwrap
import pandas as pd
import io
import base64

from . import fstriplestore
from . import obj_tracking
from . import wb_stack
from . import rdfio

random_id = 0


def dump_obj_state(obj):
    caller_stack_entry = wb_stack.wb_stack.get_parent_of_current_entry()
    t_obj, obj_found = obj_tracking.tracking_store.get_tracking_obj(obj)

    global random_id
    obj_state_uri = f"<ObjState#{random_id}>"
    random_id += 1
    fstriplestore.triple_store.dump_triple(
        obj_state_uri, "rdf:type", "<ObjState>"
    )
    fstriplestore.triple_store.dump_triple(obj_state_uri, "<obj>", t_obj.uri)
    fstriplestore.triple_store.dump_triple(
        obj_state_uri, "<part-of>", caller_stack_entry.uri
    )
    fstriplestore.triple_store.dump_triple(
        obj_state_uri, "<version>", f'"{t_obj.last_version_num}"'
    )
    t_obj.last_obj_state_uri = obj_state_uri
    t_obj.last_version_num += 1

    dump_obj_state_cc(obj_state_uri, obj, output_type="head")

    return t_obj


def dump_obj_state_cc(obj_state_uri, obj, output_type="head"):
    ts = fstriplestore.triple_store
    global random_id
    obj_state_cc_uri = f"<ObjStateCC#{random_id}>"
    random_id += 1

    ts.dump_triple(obj_state_cc_uri, "rdf:type", "<ObjStateCC>")
    ts.dump_triple(obj_state_cc_uri, "<obj-state>", obj_state_uri)

    rdfio_obj = rdfio.TableDump(ts) if output_type == "head" else rdfio.BasicPlot(ts)
    rdfio_obj.to_rdf(obj, obj_state_cc_uri)
