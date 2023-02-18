import uuid

from . import fstriplestore
from . import obj_tracking


class RDFNode:
    def __init__(self, rdf_type, label):
        self.label = label
        self.rdf_type = rdf_type
        self.uri = f"<{self.rdf_type}#{str(uuid.uuid4())}>"

        rdfl = fstriplestore.triple_store
        rdf_type_uri = f"<{self.rdf_type}>"
        rdfl.dump_triple(self.uri, "rdf:type", rdf_type_uri)
        label_obj = f'"{self.label}"' if self.label else "rdf:nil"
        rdfl.dump_triple(self.uri, "rdf:label", label_obj)


def arrow(from_obj, arrow_label, to_obj):
    rdfl = fstriplestore.triple_store
    arrow_uri = f"<Arrow#{str(uuid.uuid4())}>"
    rdfl.dump_triple(arrow_uri, "rdf:type", "<Arrow>")
    t_from_obj, from_found = obj_tracking.tracking_store.get_tracking_obj(
        from_obj
    )
    t_to_obj, to_found = obj_tracking.tracking_store.get_tracking_obj(to_obj)
    rdfl.dump_triple(arrow_uri, "<arrow-from>", t_from_obj.last_obj_state_uri)
    rdfl.dump_triple(arrow_uri, "<arrow-to>", t_to_obj.last_obj_state_uri)
    rdfl.dump_triple(arrow_uri, "<arrow-label>", '"' + arrow_label + '"')
