import ipdb
import pandas as pd
import base64
import inspect

from . import rdf_utils
from . import fstriplestore
from . import wb_stack
from . import obj_tracking
from . import obj_utils
from . import rdf_utils

method_counter = 0  # NB: should be better way to count method calls
class MethodCallRDF(rdf_utils.RDFRep):
    def __init__(self, method_call):
        super().__init__()
        self.front = method_call
        self.set_rdf_rep(rdf_type = "MethodCall")
    
    def dump_rdf_method_call_in(self):
        ts = fstriplestore.triple_store

        ts.dump_triple(self.uri, "rdf:type", self.rdf_type_uri)
        ts.dump_triple(self.uri, "rdf:label", '"' + self.front.method_name + '"')
        parent_obj = self.front.parent_stack_entry
        parent_uri = parent_obj.back.uri if parent_obj else "rdf:nil"
        ts.dump_triple(self.uri, "<part-of>", parent_uri)

        # ts.dump_triple(method_call_uri, "<method-thread>", thread_uri)
        global method_counter
        ts.dump_triple(self.uri, "<method-counter>", method_counter); method_counter += 1
        ts.dump_triple(self.uri, "<method-stack-depth>", wb_stack.wb_stack.size())
        ts.dump_triple(self.uri, "<method-stack-trace>", '"' + wb_stack.wb_stack.to_string() + '"')

        method_display_args = []
        for p_name, p in self.front.args_l:
            if isinstance(p, obj_utils.ObjState):
                method_display_args.append("<b>" + p_name + "</b>")
            else:
                method_display_args.append(
                    p_name
                    + " = "
                    + str(p).replace("<", "&lt;").replace(">", "&gt;")
                )

        method_display_s = base64.b64encode(
            (
                "<i>"
                + self.front.method_name
                + "</i>"
                + "  ("
                + ", ".join(method_display_args)
                + ")"
            ).encode("ascii")
        ).decode("ascii")
        ts.dump_triple(self.uri, "<method-display>", '"' + method_display_s + '"')

        # ipdb.set_trace()
        c = 0
        for arg_name, arg_obj in self.front.args_l:
            #ipdb.set_trace()
            arg_obj.back.dump_rdf()
            ts.dump_triple(self.uri, f"<method-call-arg{c}-name>", '"' + arg_name + '"')
            ts.dump_triple(self.uri, f"<method-call-arg{c}>", arg_obj.back.uri)
            c += 1

        return self.uri

    def dump_rdf_method_call_out(self):
        ts = fstriplestore.triple_store
        ret_obj = self.front.ret_obj_state        
        ret_obj.back.dump_rdf()
        ts.dump_triple(self.uri, "<method-call-return>", ret_obj.back.uri)
