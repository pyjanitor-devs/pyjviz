class CallStack:
    def __init__(self):
        self.calls = []

    def size(self):
        return len(self.calls)

    def to_string(self):
        return ":".join(self.calls)
    
call_stack = CallStack()

class CallStackContextManager:
    def __init__(self, method_name):
        self.method_name = method_name

    def __enter__(self):
        global call_stack
        call_stack.calls.append(self.method_name)        

    def __exit__(self, type, value, traceback):
        global call_stack
        call_stack.calls.pop()        

def create_call_stack_context_manager(method_name):
    return CallStackContextManager(method_name)
