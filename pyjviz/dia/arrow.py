from .dia_objs import DiagramObj
from ..rdf.dia_objs_rdf import ArrowRDF
from .obj_tracking import get_tracking_obj

class Arrow(DiagramObj):
    """
    Arrow class is to represent arrow connenting two diagram objects.
    """

    def __init__(self, from_dia_obj, to_dia_obj, *, parent_obj = None, label = None):
        super().__init__(ArrowRDF, parent_obj)
        #if isinstance(from_dia_obj, obj_state.ObjState):
        if 1:
            from_dia_obj_id, found = get_tracking_obj(from_dia_obj)
            #if not found:
            #    ...
            self.from_dia_obj = from_dia_obj_id.last_obj_state

        #if isinstance(to_dia_obj, obj_state.ObjState):
        if 1:
            to_dia_obj_id, found = get_tracking_obj(to_dia_obj)
            #if not found:
            #    ...
            self.to_dia_obj = to_dia_obj_id.last_obj_state

        self.label = label
        
        self.back.dump_rdf()
        
