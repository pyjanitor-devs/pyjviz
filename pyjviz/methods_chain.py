import ipdb
import threading
import pandas as pd
import inspect
import uuid

from . import call_stack
from . import rdflogging
from . import obj_tracking

class CodeContext(call_stack.CallStackEntry):
    def __init__(self, label = None, rdf_type = "CodeContext"):
        super().__init__(label = label, rdf_type = rdf_type)

CC = CodeContext
        
class NestedCall(call_stack.CallStackEntry):
    def __init__(self, arg_name, arg_func):
        super().__init__(label = f"nested_call({arg_name})", rdf_type = "NestedCall")        
        self.arg_name = arg_name
        self.arg_func = arg_func
        self.ret = None

        self.init_dump__(rdflogging.rdflogger)
        
    def __call__(self, *args, **kwargs):
        with self:
            print("NestedCall called")
            self.ret = self.arg_func(*args, **kwargs)
            #ipdb.set_trace()
            return self.ret
        
class MethodCall(CodeContext):
    def __init__(self, method_name, have_nested_call_args):
        super().__init__(label = method_name, rdf_type = "MethodCall")
        self.method_bound_args = None
        self.have_nested_call_args = have_nested_call_args
        self.nested_call_args = []
        
    def handle_start_method_call(self, obj, method_name, method_signature, method_args, method_kwargs):
        rdfl = rdflogging.rdflogger

        all_args = tuple([obj] + list(method_args))
        self.method_signature = method_signature
        self.method_bound_args = self.method_signature.bind(*all_args, **method_kwargs)
        self.method_bound_args.apply_defaults()

        for arg_name, arg_value in self.method_bound_args.arguments.items():
            arg_kind = method_signature.parameters.get(arg_name).kind
            print(method_name, arg_name, arg_kind)
            if arg_kind == inspect.Parameter.VAR_KEYWORD: # case for lambda args of assign
                updates_d = {}
                for kwarg_name, kwarg_value in arg_value.items():
                    if inspect.isfunction(kwarg_value):
                        new_kwarg_value = NestedCall(kwarg_name, kwarg_value) # create empty nested call obj as placeholder for future results
                        updates_d[kwarg_name] = new_kwarg_value
                        self.nested_call_args.append(new_kwarg_value)
                self.method_bound_args.arguments[arg_name].update(updates_d)

        new_args = self.method_bound_args.args
        new_kwargs = self.method_bound_args.kwargs

        #ipdb.set_trace()
        t_obj = obj_tracking.tracking_store.get_tracking_obj(obj)
        thread_id = threading.get_native_id()
        #caller_stack_entry = call_stack.stack.stack_entries[-2]
        caller = get_parent_of_current_entry(call_stack.stack)
        rdfl.dump_method_call_in(self, thread_id, obj, t_obj,
                                 method_name, method_signature, self.method_bound_args,
                                 caller)

        return new_args, new_kwargs

    def handle_end_method_call(self, ret):
        rdfl = rdflogging.rdflogger
        ret_obj = ret if not ret is None else obj

        ret_t_obj = obj_tracking.tracking_store.get_tracking_obj(ret_obj)

        #caller_stack_entry = call_stack.stack.stack_entries[-2]
        caller = get_parent_of_current_entry(call_stack.stack)
        ret_t_obj.last_obj_state_uri = rdfl.dump_obj_state(ret_obj, ret_t_obj, caller)
        rdfl.dump_triple__(self.uri, "<method-call-return>", ret_t_obj.last_obj_state_uri)

        # catching nested calls values returned after method call executed
        for nested_call_obj in self.nested_call_args:
            t_obj = obj_tracking.tracking_store.get_tracking_obj(nested_call_obj.ret)
            if t_obj.last_obj_state_uri is None:
                raise Exception("expected to have uri assigned")
            rdfl.dump_triple__(nested_call_obj.uri, "<ret-val>", t_obj.last_obj_state_uri)


def get_latest_method_call(stack):
    ret = None
           
    for se in reversed(stack.stack_entries__):
        if isinstance(se, MethodCall):
            ret = se
            break
        elif isinstance(se, NestedCall):
            ret = None
            break
        elif isinstance(se, CodeContext):
            continue

    return ret

def get_parent_of_current_entry(stack):
    ret = None
           
    if stack.size() > 0:
        for se in reversed(stack.stack_entries__):
            if isinstance(se, MethodCall):
                ret = se
                break
            elif isinstance(se, NestedCall):
                continue
            elif isinstance(se, CodeContext):
                ret = se
                break

    return ret
    
