from . import fstriplestore
from . import rdf_utils

class TextRDF(rdf_utils.RDFRep):
    def __init__(self, text_obj):
        super().__init__()
        self.front = text_obj

    def dump_rdf(self):
        ts = fstriplestore.triple_store        
        self.set_obj_uri("Text")
        ts.dump_triple(self.uri, "rdf:type", self.rdf_type_uri)
        parent_obj = self.front.parent_obj
        parent_uri = parent_obj.back.uri if parent_obj else "rdf:nil"
        ts.dump_triple(self.uri, "<part-of>", parent_uri)
        ts.dump_triple(self.uri, "rdf:label", '"' + self.front.label + '"')
        ts.dump_triple(self.uri, "<text>", '"' + fstriplestore.to_base64(self.front.text) + '"')
        
