from . import fstriplestore
from . import rdf_utils


class CodeBlockRDF(rdf_utils.RDFRep):
    def __init__(self, code_block):
        self.set_rdf_rep(rdf_type="CodeBlock")
        self.front = code_block

    def dump_rdf(self):
        ts = fstriplestore.triple_store
        ts.dump_triple(self.uri, "rdf:type", self.rdf_type_uri)
        if self.front.label:
            l_uri = f'"{self.front.label}"'
        else:
            l_uri = "rdf:nil"

        if self.front.part_of:
            parent_uri = self.front.part_of.back.uri
        else:
            parent_uri = "rdf:nil"

        ts.dump_triple(self.uri, "rdf:label", l_uri)
        ts.dump_triple(self.uri, "<part-of>", parent_uri)

    def flush_triples(self):
        fstriplestore.triple_store.flush()
