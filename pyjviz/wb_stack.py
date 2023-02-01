import uuid

from . import fstriplestore

class WithBlock:
    """
    Code blocks in python - https://docs.python.org/3/reference/executionmodel.html#:~:text=A%20Python%20program%20is%20constructed,typed%20interactively%20is%20a%20block.
    With PEP use of 'block' - https://peps.python.org/pep-0343/#specification-the-with-statement

    Base class for CodeBlock, MethodCall and NestedCall.
      - uri - to identify itself in graph as node
      - rdf_type_uri - to identify node type
    """
    def __init__(self, *, label, rdf_type):
        self.label = label
        self.rdf_type = rdf_type
        self.uri = None
        self.init_dump__()
        
    def init_dump__(self):
        rdfl = fstriplestore.triple_store
        self.uri = f"<{self.rdf_type}#{str(uuid.uuid4())}>"
        rdf_type_uri = f"<{self.rdf_type}>"
        rdfl.dump_triple(self.uri, "rdf:type", rdf_type_uri)
        label_obj = f'"{self.label}"' if self.label else 'rdf:nil'
        rdfl.dump_triple(self.uri, "rdf:label", label_obj)
        global wb_stack
        parent_uri = wb_stack.stack_entries__[-1].uri if wb_stack.size() > 0 else "rdf:nil"
        rdfl.dump_triple(self.uri, "<part-of>", parent_uri)
        self.dump_init_called = True
        
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

    def get_top(self):
        return self.stack_entries__[-1]

    def get_latest_method_call(self):
        ret = None

        for se in reversed(self.stack_entries__):
            if se.rdf_type == "MethodCall":
                ret = se
                break
            elif se.rdf_type == "NestedCall":
                ret = None
                break
            elif se.rdf_type == "CodeBlock":
                continue

        return ret

    def get_parent_of_current_entry(self):
        ret = None

        if self.size() > 0:
            for se in reversed(self.stack_entries__):
                if se.rdf_type == "MethodCall":
                    ret = se
                    break
                elif se.rdf_type == "NestedCall":
                    continue
                elif se.rdf_type == "CodeBlock":
                    ret = se
                    break

        return ret

    def get_parent_code_context_of_current_entry(self):
        ret = None

        if self.size() > 0:
            for se in reversed(self.stack_entries__):
                if se.rdf_type == "MethodCall":
                    continue
                elif se.rdf_type == "NestedCall":
                    continue
                elif se.rdf_type == "CodeBlock":
                    ret = se
                    break

        return ret

    def get_parent_nested_call(self):
        ret = None

        if self.size() > 0:
            for se in reversed(self.stack_entries__):
                if se.rdf_type == "MethodCall":
                    continue
                elif se.rdf_type == "NestedCall":
                    ret = se
                    break
                elif se.rdf_type == "CodeBlock":
                    continue
        return ret
        
    
wb_stack = WithBlockStack()
def get_wb_stack():
    global wb_stack
    return wb_stack
