import uuid

from . import fstriplestore

class RDFNode:
    def __init__(self, rdf_type, label):
        self.label = label
        self.rdf_type = rdf_type
        self.uri = f"<{self.rdf_type}#{str(uuid.uuid4())}>"

        rdfl = fstriplestore.triple_store
        rdf_type_uri = f"<{self.rdf_type}>"
        rdfl.dump_triple(self.uri, "rdf:type", rdf_type_uri)
        label_obj = f'"{self.label}"' if self.label else 'rdf:nil'
        rdfl.dump_triple(self.uri, "rdf:label", label_obj)
    
