from . import fstriplestore
from . import rdf_node

class WithBlock(rdf_node.RDFNode):
    """
    Code blocks in python - https://docs.python.org/3/reference/executionmodel.html#:~:text=A%20Python%20program%20is%20constructed,typed%20interactively%20is%20a%20block.
    With PEP use of 'block' - https://peps.python.org/pep-0343/#specification-the-with-statement

    Base class for CodeBlock, MethodCall and NestedCall.
      - uri - to identify itself in graph as node
      - rdf_type_uri - to identify node type
    """
    def __init__(self, *, rdf_type, label):
        super().__init__(rdf_type, label)
        rdfl = fstriplestore.triple_store
        global wb_stack
        parent_uri = wb_stack.stack_entries__[-1].uri if wb_stack.size() > 0 else "rdf:nil"
        rdfl.dump_triple(self.uri, "<part-of>", parent_uri)
        
    def __enter__(self):
        global wb_stack
        wb_stack.push(self)
        return self

    def __exit__(self, type, value, traceback):
        fstriplestore.triple_store.flush()
        global wb_stack
        wb_stack.pop()
        
class WithBlockStack:
    def __init__(self):
        self.stack_entries__ = []

    def to_string(self):
        return ":".join([f"{x.label}@{x.rdf_type}" for x in self.stack_entries__])
    
    def size(self):
        return len(self.stack_entries__)

    def push(self, e):
        self.stack_entries__.append(e)
        
    def pop(self):
        return self.stack_entries__.pop()

    def get_top(self):
        return self.stack_entries__[-1]

    def get_latest_method_call(self):
        ret = None

        for se in reversed(self.stack_entries__):
            if se.rdf_type == "MethodCall":
                ret = se
                break
            elif se.rdf_type == "CodeBlock":
                continue

        return ret

    def get_parent_of_current_entry(self):
        ret = self.stack_entries__[-1] if self.size() > 0 else None
        return ret
        
    
wb_stack = WithBlockStack()
def get_wb_stack():
    global wb_stack
    return wb_stack
