import uuid

from . import rdflogging

class CallStackEntry:
    """
    Base class for CodeContext and MethodCall. Each StackEntry obj has:
      - uri - to identify itself in graph as node
      - rdf_type_uri - to identify node type
    """
    def __init__(self, *, label, rdf_type):
        self.label = label
        self.rdf_type = rdf_type
        self.uri = None
        self.init_dump__(rdflogging.rdflogger)
        
    def init_dump__(self, rdfl):
        self.uri = f"<{self.rdf_type}#{str(uuid.uuid4())}>"
        rdf_type_uri = f"<{self.rdf_type}>"
        rdfl.dump_triple__(self.uri, "rdf:type", rdf_type_uri)
        label_obj = f'"{self.label}"' if self.label else 'rdf:nil'
        rdfl.dump_triple__(self.uri, "rdf:label", label_obj)
        global stack
        parent_uri = stack.stack_entries__[-1].uri if stack.size() > 0 else "rdf:nil"
        rdfl.dump_triple__(self.uri, "<part-of>", parent_uri)
        self.dump_init_called = True
        
    def __enter__(self):
        global stack
        stack.push(self)
        return self

    def __exit__(self, type, value, traceback):
        rdflogging.rdflogger.flush__()
        global stack
        stack.pop()
        
class CallStack:
    def __init__(self):
        self.stack_entries__ = []

    def to_string(self):
        return ":".join([f"{x.label}@{x.rdf_type}" for x in self.stack_entries__])

    #def to_methods_calls__(self):
    #    ret = [se.label for se in self.stack_entries__ if se.rdf_type == "MethodCall"]
    #    return ret

    #def to_methods_calls_string(self):
    #    return ":".join(self.to_methods_calls__())
    
    def size(self):
        return len(self.stack_entries__)

    def push(self, e):
        self.stack_entries__.append(e)
        
    def pop(self):
        return self.stack_entries__.pop()

stack = CallStack()

