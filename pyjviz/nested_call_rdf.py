from . import fstriplestore
from . import rdf_utils


class NestedCallRDF(rdf_utils.RDFRep):
    def __init__(self, nested_call_obj):
        self.set_rdf_rep(rdf_type="NestedCall")
        self.front = nested_call_obj

    def dump_rdf(self):
        ts = fstriplestore.triple_store
        ts.dump_triple(self.uri, "rdf:type", self.rdf_type_uri)
        ts.dump_triple(self.uri, "<part-of>", self.front.parent_uri)

    def dump_return(self):
        ts = fstriplestore.triple_store
        self.front.ret.back.dump_rdf()
        ts.dump_triple(self.uri, "<ret-val>", self.front.ret.back.uri)

        # nested call refs
        print("nested call:", self.uri)
        print("collected ids:", self.front.ctx.collected_ids)

        for _, ref_obj_state_uri in self.front.ctx.collected_ids:
            if ref_obj_state_uri:
                ts.dump_triple(self.uri, "<nested-call-ref>",
                               ref_obj_state_uri)
