import uuid

class RDFRep:
    def __init__(self):
        self.rdf_type_uri = None
        self.uri = None

    def set_obj_uri(self, rdf_type, obj_id = None):
        obj_id = obj_id if obj_id else str(uuid.uuid4())
        self.rdf_type_uri = "<" + rdf_type + ">"
        self.uri = f"<{rdf_type}#{obj_id}>"
        
