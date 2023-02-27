"""
rdf_utils.py - RDF representation of python objects
"""

import uuid


class RDFRep:
    """
    RDFRep - class to hold python object URI along with some basic attributes:

    - uri - object URI itself
    - rdf_type_uri - URI to RDF type of python object class
    """

    def __init__(self):
        self.front = None
        self.uri = None
        self.rdf_type_uri = None

    def set_rdf_rep(self, *, rdf_type, obj_id=None):
        """
        this method should be called by ctor of derived class to complete
        construction of RDF rep attributes
        """
        obj_id = obj_id if obj_id else str(uuid.uuid4())
        self.rdf_type_uri = "<" + rdf_type + ">"
        self.uri = f"<{rdf_type}#{obj_id}>"
