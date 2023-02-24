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

class ObjIdRDF(rdf_utils.RDFRep):
    def __init__(self, obj_id):
        self.set_rdf_rep(rdf_type = "ObjId")
        self.front = obj_id
        self.was_dumped = False
        
    def dump_rdf(self):
        if self.was_dumped == False:
            self.was_dumped = True
            ts = fstriplestore.triple_store
            ts.dump_triple(self.uri, "rdf:type", self.rdf_type_uri)
            ts.dump_triple(self.uri, "<obj-type>", f'"{self.front.obj_type}"')
            ts.dump_triple(self.uri, "<obj-uuid>", f'"{self.front.uuid}"')
            ts.dump_triple(self.uri, "<obj-pyid>", f"{self.front.pyid}")
            

class ObjStateRDF(rdf_utils.RDFRep):
    def __init__(self, obj_state):
        super().__init__()
        self.front = obj_state
        self.was_dumped = False

        global random_id
        self.set_rdf_rep(rdf_type = "ObjState", obj_id = str(random_id)); random_id += 1
        
    def dump_rdf(self):
        if self.was_dumped == False:
            self.was_dumped = True
            obj_id = self.front.obj_id
            obj_id.back.dump_rdf()
        
            ts = fstriplestore.triple_store
            caller_stack_entry = wb_stack.wb_stack.get_top()
            
            ts.dump_triple(self.uri, "rdf:type", self.rdf_type_uri)
            #ts.dump_triple(self.uri, "rdf:type", rdf_io.CCObjStateLabel.rdf_type)
            
            ts.dump_triple(self.uri, "<obj>", obj_id.back.uri)
            ts.dump_triple(self.uri, "<part-of>", caller_stack_entry.back.uri)
            ts.dump_triple(self.uri, "<version>", f'"{obj_id.last_version_num}"')
            
            obj_state_label_dumper = rdf_io.CCObjStateLabel()
            obj_state_label_dumper.to_rdf(self.front.obj, self.uri)

            #dump_obj_state_cc(obj_state_uri, obj, output_type="head")
