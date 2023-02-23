from . import wb_stack
from .dia_objs_rdf import TextRDF

class DiagramObj:
    def __init__(self):
        pass

class Text(DiagramObj):
    def __init__(self, title, text, parent_obj = None):
        if parent_obj:
            if not isinstance(parent_obj, DiagramObj):
                raise Exception(f"parent_obj must be instance of subclass of DiagramObj, {type(parent_obj)}")
        else:
            parent_obj = wb_stack.wb_stack.get_top()

        self.parent_obj = parent_obj
            
        self.label = title
        self.text = text
        self.back = TextRDF(self)
