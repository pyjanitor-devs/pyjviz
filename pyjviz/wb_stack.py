from . import fstriplestore
from . import dia_objs


class WithBlock(dia_objs.DiagramObj):
    """
    Code blocks in python - https://docs.python.org/3/reference/executionmodel.html#:~:text=A%20Python%20program%20is%20constructed,typed%20interactively%20is%20a%20block.
    With PEP use of 'block' - https://peps.python.org/pep-0343/#specification-the-with-statement

    Base class for CodeBlock, MethodCall and NestedCall.
      - uri - to identify itself in graph as node
      - rdf_type_uri- to identify node type
    """  # noqa: E501

    def __init__(self, label):
        super().__init__()
        global wb_stack
        self.label = label
        self.parent_stack_entry = (
            wb_stack.stack_entries__[-1]
            if wb_stack.size() > 0
            else None
        )

        self.dump_rdf()
        
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
        return ":".join(
            [f"{x.label}@{type(x).__name__}" for x in self.stack_entries__]
        )

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
            if type(se).__name__ == "MethodCall":
                ret = se
                break
            elif type(se).__name__ == "CodeBlock":
                continue

        return ret

    def get_parent_of_current_entry(self):
        ret = self.stack_entries__[-1] if self.size() > 0 else None
        return ret


wb_stack = WithBlockStack()


def get_wb_stack():
    global wb_stack
    return wb_stack
