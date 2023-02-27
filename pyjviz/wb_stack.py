from . import dia_objs


class WithBlock(dia_objs.DiagramObj):
    """
    WithBlock is a class of python context objects which are used to implement behavior when python *with* statement is used.
    See also `https://peps.python.org/pep-0343/#specification-the-with-statement`.
    For pyjviz we are using WithBlock to implement the idea of visual contrainer where other diagram objects can be placed.

    pyjviz has wb_atack global object which is maintained using WithBlock implementation of __enter__/__exit__ methods.
    """ # noqa : E501

    def __init__(self, label):
        super().__init__()
        global wb_stack
        self.label = label
        self.parent_stack_entry = (
            wb_stack.stack_entries__[-1]
            if wb_stack.size() > 0
            else None
        )

    def __enter__(self):
        global wb_stack
        wb_stack.push(self)
        return self

    def on_exit__(self):
        pass

    def __exit__(self, type, value, traceback):
        self.on_exit__()
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
        return self.stack_entries__[-1] if self.size() > 0 else None

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
        ret = self.stack_entries__[-2] if self.size() > 1 else None
        return ret


wb_stack = WithBlockStack()


def get_wb_stack():
    """
    returns ref to global wb_stack object.
    """
    global wb_stack
    return wb_stack
