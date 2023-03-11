#import ipdb
from .dia_objs import DiagramObj
from ..rdf.dia_objs_rdf import ArrowRDF
from .obj_tracking import get_tracking_obj
from .dia_objs import DiagramObj

class Arrow(DiagramObj):
    """
    Arrow class is to represent arrow connenting two diagram objects.
    """

    def __init__(self, from_dia_obj, to_dia_obj, *, parent_obj = None, label = None):
        super().__init__(ArrowRDF, parent_obj)

        #ipdb.set_trace()
        if isinstance(from_dia_obj, DiagramObj):
            self.from_dia_obj = from_dia_obj
        else:
            from_dia_obj_id, found = get_tracking_obj(from_dia_obj)
            #if not found:
            #    ...
            self.from_dia_obj = from_dia_obj_id.last_obj_state

        if isinstance(to_dia_obj, DiagramObj):
            self.to_dia_obj = to_dia_obj
        else:
            to_dia_obj_id, found = get_tracking_obj(to_dia_obj)
            #if not found:
            #    ...
            self.to_dia_obj = to_dia_obj_id.last_obj_state


        self.label = label
        
        self.back.dump_rdf()
        
