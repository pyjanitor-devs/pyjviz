#import ipdb
import threading
import pandas as pd
import inspect
import uuid

from . import wb_stack
from . import rdflogging
from . import obj_tracking

class CodeBlock(wb_stack.WithBlock):
    def __init__(self, label = None, rdf_type = "CodeContext"):
        super().__init__(label = label, rdf_type = rdf_type)

CB = CodeBlock

class NestedCall(wb_stack.WithBlock):
    def __init__(self, arg_name, arg_func):
        super().__init__(label = f"nested_call({arg_name})", rdf_type = "NestedCall")        
        #ipdb.set_trace()
        self.arg_name = arg_name
        self.arg_func = arg_func
        self.ret = None
        
    def __call__(self, *args, **kwargs):
        with self:
            print("NestedCall called")
            self.ret = self.arg_func(*args, **kwargs)
            ret_t_obj = obj_tracking.tracking_store.get_tracking_obj(self.ret)
            if ret_t_obj.last_obj_state_uri is None:
                caller_stack_entry = get_parent_of_current_entry(wb_stack.stack)
                rdfl = rdflogging.rdflogger
                ret_t_obj.last_obj_state_uri = rdfl.dump_obj_state(self.ret, ret_t_obj, caller_stack_entry)
            return self.ret

class MethodCall(wb_stack.WithBlock):
    def __init__(self, method_name, have_nested_call_args):
        super().__init__(label = method_name, rdf_type = "MethodCall")
        self.method_bound_args = None
        self.have_nested_call_args = have_nested_call_args
        self.nested_call_args = []
        
    def handle_start_method_call(self, method_name, method_signature, method_args, method_kwargs):
        rdfl = rdflogging.rdflogger
        
        all_args = method_args
        self.method_signature = method_signature
        #ipdb.set_trace()
        self.method_bound_args = self.method_signature.bind(*all_args, **method_kwargs)
        args_w_specified_values = self.method_bound_args.arguments.keys()
        # NB:
        # according to python doc default values are evaluated and saved only once when function is defined
        # apply_defaults method is to be used to put default values to method_bound_args.arguments
        # decision to call or not to call apply_defaults could affect program execution since we could modify arguments
        # of real method call which will happen after this method returns new args and kwargs.
        # E.g. loop over all arguments will be affected
        # since apply_defaults will add new entries which were skipped by method_signature.bind since they are omit and use default values
        #  --- >>>> commented out ---> self.method_bound_args.apply_defaults()

        # NB:
        # loop over args_w_specified_values will skip the args where func value should be supplied and default func value is used.
        # purpose of the loop is to replace such func arg values with equivalent obj of class NestedCall which suppose to collect
        # call tracking information for visualization. so no such information will be collected for fund args where default value is used
        for arg_name in args_w_specified_values:
            arg_value = self.method_bound_args.arguments.get(arg_name)
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

        thread_id = threading.get_native_id()
        caller = get_parent_of_current_entry(wb_stack.wb_stack)
        
        # NB: since apply_defaults is not called then no tracking of args with default values will take place
        rdfl.dump_method_call_in(self, thread_id, method_name, method_signature, self.method_bound_args, caller)

        return new_args, new_kwargs

    def handle_end_method_call(self, ret):
        rdfl = rdflogging.rdflogger
        ret_obj = ret if not ret is None else obj

        ret_t_obj = obj_tracking.tracking_store.get_tracking_obj(ret_obj)

        caller = get_parent_of_current_entry(wb_stack.wb_stack)
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
        elif isinstance(se, CodeBlock):
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
            elif isinstance(se, CodeBlock):
                ret = se
                break

    return ret

def get_parent_code_context_of_current_entry(stack):
    ret = None
           
    if stack.size() > 0:
        for se in reversed(stack.stack_entries__):
            if isinstance(se, MethodCall):
                continue
            elif isinstance(se, NestedCall):
                continue
            elif isinstance(se, CodeBlock):
                ret = se
                break

    return ret
    
