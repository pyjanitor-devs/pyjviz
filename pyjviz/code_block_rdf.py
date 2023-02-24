from . import fstriplestore
from . import rdf_utils

class CodeBlockRDF(rdf_utils.RDFRep):
    def __init__(self, code_block):
        self.front = code_block
        
    def to_rdf(self):
        ts = fstriplestore.triple_store
        self.set_obj_uri("CodeBlock")
        ts.dump_triple(self.uri, "rdf:type", self.rdf_type_uri)
        ts.dump_triple(self.uri, "rdf:label", f'"{self.front.label}"' if self.front.label else "rdf:nil")
        parent_uri = self.front.parent_stack_entry.uri if self.front.parent_stack_entry else "rdf:nil"
        ts.dump_triple(self.uri, "<part-of>", parent_uri)

    def flush_triples(self):
        fstriplestore.triple_store.flush()