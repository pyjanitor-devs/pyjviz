import ipdb
import uuid
import weakref
import textwrap
import pandas as pd
import io
import base64

from . import fstriplestore
from . import obj_tracking
from . import wb_stack
from . import rdf_utils
from . import rdf_io
from . import dia_objs

def obj_del_cb(ref):
    print("obj deleted", ref)

random_id = 0

class ObjId(rdf_utils.RDFRepOfObj):
    def __init__(self, obj):
        self.obj_wref = weakref.ref(obj, obj_del_cb)
        self.obj_type = type(obj).__name__
        self.uuid = uuid.uuid4()
        self.pyid = id(obj)
        self.last_obj_state = None
        self.last_version_num = 0
        
    def is_alive(self):
        return not self.obj_wref() is None

    def incr_version(self):
        ret = self.last_version_num
        self.last_version_num += 1
        return ret

    def dump_rdf(self):
        ts = fstriplestore.triple_store
        self.set_obj_uri("ObjId")
        ts.dump_triple(self.uri, "rdf:type", self.rdf_type_uri)
        ts.dump_triple(self.uri, "<obj-type>", f'"{self.obj_type}"')
        ts.dump_triple(self.uri, "<obj-uuid>", f'"{self.uuid}"')
        ts.dump_triple(self.uri, "<obj-pyid>", f"{self.pyid}")


def dump_obj_state(obj):
    obj_state = ObjState(obj)
    obj_state.dump_rdf()
    t_obj, obj_found = obj_tracking.get_tracking_obj(obj)
    return t_obj

class ObjState(dia_objs.DiagramObj, rdf_io.CCObjStateLabel):
    def __init__(self, obj):
        dia_objs.DiagramObj.__init__(self)
        rdf_io.CCObjStateLabel.__init__(self)
        self.obj = obj

    def dump_rdf(self):
        ts = fstriplestore.triple_store
        caller_stack_entry = wb_stack.wb_stack.get_parent_of_current_entry()
        t_obj, obj_found = obj_tracking.get_tracking_obj(self.obj)
        
        global random_id
        self.set_obj_uri("ObjState", str(random_id)); random_id += 1
        ts.dump_triple(self.uri, "rdf:type", self.rdf_type_uri)
        #ts.dump_triple(self.uri, "rdf:type", rdf_io.CCObjStateLabel.rdf_type)

        ts.dump_triple(self.uri, "<obj>", t_obj.uri)
        ts.dump_triple(self.uri, "<part-of>", caller_stack_entry.uri)
        ts.dump_triple(self.uri, "<version>", f'"{t_obj.last_version_num}"')
        t_obj.last_obj_state = self
        t_obj.last_version_num += 1

        obj_state_label_dumper = rdf_io.CCObjStateLabel()
        obj_state_label_dumper.to_rdf(self.obj, self.uri)

        #dump_obj_state_cc(obj_state_uri, obj, output_type="head")

        return t_obj

    """
    def dump_obj_state_cc(obj_state_uri, obj, output_type="head"):
        ts = fstriplestore.triple_store
        global random_id
        obj_state_cc_uri = f"<ObjStateCC#{random_id}>"
        random_id += 1

        ts.dump_triple(obj_state_cc_uri, "rdf:type", "<ObjStateCC>")
        ts.dump_triple(obj_state_cc_uri, "<obj-state>", obj_state_uri)

        rdfio_obj = rdf_io.CCGlance(ts) if output_type == "head" else rdfio.CCBasicPlot(ts)
        rdfio_obj.to_rdf(obj, obj_state_cc_uri)
    """
    
