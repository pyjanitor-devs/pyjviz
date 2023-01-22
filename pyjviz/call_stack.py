class StackEntry:
    """
    Base class for SubGraph and MethodCall. Each StackEntry obj has:
      - uri - to identify itself in graph as node
      - rdf_type_uri - to identify node type
    """
    def __init__(self, rdf_type_uri):
        self.rdf_type_uri = rdf_type_uri
        self.uri = None

class Stack:
    def __init__(self):
        self.stack_entries = []

    def to_string(self):
        return ":".join([x.rdf_type for x in self.stack_entries])

    def to_methods_calls(self):
        ret = [se.label for se in self.stack_entries if se.rdf_type == "MethodCall"]
        return ret

    def to_methods_calls_string(self):
        return ":".join(self.to_methods_calls())
    
    def size(self):
        return len(self.stack_entries)

    def push(self, e):
        self.stack_entries.append(e)
        
    def pop(self):
        return self.stack_entries.pop()
    
stack = Stack()

