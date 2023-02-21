from . import fstriplestore
from . import wb_stack

class CodeBlock(wb_stack.WithBlock):
    def __init__(self, label = None):
        super().__init__(label)

    def dump_rdf(self):
        ts = fstriplestore.triple_store
        self.set_obj_uri("CodeBlock")
        ts.dump_triple(self.uri, "rdf:type", self.rdf_type_uri)
        ts.dump_triple(self.uri, "rdf:label", f'"{self.label}"' if self.label else "rdf:nil")
        parent_uri = self.parent_stack_entry.uri if self.parent_stack_entry else "rdf:nil"
        ts.dump_triple(self.uri, "<part-of>", parent_uri)
        
CB = CodeBlock
