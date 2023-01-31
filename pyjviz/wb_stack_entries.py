#import ipdb
import threading
import pandas as pd
import base64
import inspect
import uuid

from . import wb_stack
from . import rdflogging
from . import obj_tracking

class CodeBlock(wb_stack.WithBlock):
    def __init__(self, label = None, rdf_type = "CodeBlock"):
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
            rdfl = rdflogging.rdflogger
            ret_t_obj, obj_found = obj_tracking.tracking_store.get_tracking_obj(self.ret)
            if not obj_found:
                ret_t_obj = rdfl.dump_obj_state(self.ret)
                caller_stack_entry = wb_stack.wb_stack.get_parent_of_current_entry()
                rdfl.dump_triple__(ret_t_obj.uri, "<part-of>", caller_stack_entry.uri)
            return self.ret

method_counter = 0 # NB: should be better way to cout method calls
class MethodCall(wb_stack.WithBlock):
    def __init__(self, method_name, have_nested_call_args):
        super().__init__(label = method_name, rdf_type = "MethodCall")
        self.method_bound_args = None
        self.have_nested_call_args = have_nested_call_args
        self.nested_call_args = []
        
    def handle_start_method_call(self, method_name, method_signature, method_args, method_kwargs):        
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
        caller = wb_stack.wb_stack.get_parent_of_current_entry()
        
        # NB: since apply_defaults is not called then no tracking of args with default values will take place
        self.dump_method_call_in__(thread_id, method_name, method_signature, self.method_bound_args, caller)

        return new_args, new_kwargs

    def handle_end_method_call(self, ret):
        rdfl = rdflogging.rdflogger
        ret_obj = ret if not ret is None else obj

        caller = wb_stack.wb_stack.get_parent_of_current_entry()
        ret_t_obj = rdfl.dump_obj_state(ret_obj)
        rdfl.dump_triple__(ret_t_obj.last_obj_state_uri, "<part-of>", caller.uri)
        rdfl.dump_triple__(self.uri, "<method-call-return>", ret_t_obj.last_obj_state_uri)

        # catching nested calls values returned after method call executed
        for nested_call_obj in self.nested_call_args:
            t_obj, obj_found = obj_tracking.tracking_store.get_tracking_obj(nested_call_obj.ret)
            if not obj_found:
                raise Exception("expected nested call return obj to be tracked already")
            rdfl.dump_triple__(nested_call_obj.uri, "<ret-val>", t_obj.last_obj_state_uri)

    def dump_method_call_arg__(self, c, arg_name, arg_obj, caller_stack_entry):
        rdfl = rdflogging.rdflogger
        method_call_obj = self
        
        method_call_uri = method_call_obj.uri
        if isinstance(arg_obj, NestedCall):
            rdfl.dump_triple__(method_call_uri, f"<method-call-arg{c}>", arg_obj.uri)
            rdfl.dump_triple__(method_call_uri, f"<method-call-arg{c}-name>", '"' + (arg_name if arg_name else '') + '"')
        elif isinstance(arg_obj, pd.DataFrame) or isinstance(arg_obj, pd.Series):
            arg_t_obj, obj_found = obj_tracking.tracking_store.get_tracking_obj(arg_obj)
            if not obj_found:
                arg_t_obj = rdfl.dump_obj_state(arg_obj)
                rdfl.dump_triple__(arg_t_obj.last_obj_state_uri, "<part-of>", caller_stack_entry.uri)
            rdfl.dump_triple__(method_call_uri, f"<method-call-arg{c}>", arg_t_obj.last_obj_state_uri)
            rdfl.dump_triple__(method_call_uri, f"<method-call-arg{c}-name>", '"' + (arg_name if arg_name else '') + '"')
        else:
            pass
        
    def dump_method_call_in__(self, thread_id,
                              method_name, method_signature, method_bound_args,
                              caller_stack_entry):
        rdfl = rdflogging.rdflogger
        method_call_obj = self
        
        thread_uri = rdfl.register_thread(thread_id)
        method_call_uri = method_call_obj.uri

        rdfl.dump_triple__(method_call_uri, "<method-thread>", thread_uri)
        global method_counter
        rdfl.dump_triple__(method_call_uri, "<method-counter>", method_counter); method_counter += 1
        rdfl.dump_triple__(method_call_uri, "<method-stack-depth>", wb_stack.wb_stack.size())
        rdfl.dump_triple__(method_call_uri, "<method-stack-trace>", '"' + wb_stack.wb_stack.to_string() + '"')

        method_display_args = []
        for p_name, p in method_bound_args.arguments.items():
            if isinstance(p, pd.DataFrame) or isinstance(p, pd.Series):
                method_display_args.append("<b>"+p_name+"</b>")
            else:
                method_display_args.append(p_name + " = " + str(p).replace("<", "&lt;").replace(">", "&gt;"))

        method_display_s = base64.b64encode(("<i>" + method_name + "</i>" + "  (" + ", ".join(method_display_args) + ")").encode('ascii')).decode('ascii')
        rdfl.dump_triple__(method_call_uri, "<method-display>", '"' + method_display_s + '"')
        
        #ipdb.set_trace()
        c = 0
        for arg_name, arg_obj in method_bound_args.arguments.items():
            arg_kind = method_signature.parameters.get(arg_name).kind
            if arg_kind == inspect.Parameter.VAR_KEYWORD:
                for kwarg_name, kwarg_obj in arg_obj.items():
                    self.dump_method_call_arg__(c, kwarg_name, kwarg_obj, caller_stack_entry)
                    c += 1
            elif arg_kind == inspect.Parameter.VAR_POSITIONAL:
                #ipdb.set_trace()
                for p_arg_obj in arg_obj:
                    self.dump_method_call_arg__(c, None, p_arg_obj, caller_stack_entry)
                    c += 1
            else:
                self.dump_method_call_arg__(c, arg_name, arg_obj, caller_stack_entry)
                c += 1
                
        return method_call_uri
    
