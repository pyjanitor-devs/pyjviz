import ipdb
import threading
import pandas as pd
import base64
import inspect

from . import wb_stack
from . import fstriplestore
from . import obj_tracking
from . import obj_utils

from .nested_call import NestedCall

from . import method_call_rdf

from . import rdf_io

method_counter = 0  # NB: should be better way to count method calls
class MethodCall(wb_stack.WithBlock):
    def __init__(self, method_name):
        super().__init__(method_name)
        self.back = method_call_rdf.MethodCallRDF(self)
        self.method_name = method_name
        self.method_bound_args = None

        self.args_l = None
        
    def add_args_l_entry__(self, arg_name, arg_obj):
        if arg_name is None: arg_name = f"arg_{len(self.args_l)}"
        
        if type(arg_obj).__name__ == "NestedCall":
            self.args_l.append((arg_name, arg_obj))
        elif isinstance(arg_obj, pd.DataFrame) or isinstance(arg_obj, pd.Series):
            arg_obj_id, found = obj_tracking.get_tracking_obj(arg_obj)
            print("arg id:", id(arg_obj), found)
            if found:
                arg_obj_state = arg_obj_id.last_obj_state
            else:
                arg_obj_state = obj_utils.ObjState(arg_obj, arg_obj_id)
                    
            self.args_l.append((arg_name, arg_obj_state))
        else:
            self.args_l.append((arg_name, arg_obj))
                
    def build_args_l__(self):
        self.args_l = []
        for arg_name, arg_obj in self.method_bound_args.arguments.items():            
            arg_kind = self.method_signature.parameters.get(arg_name).kind
            if arg_kind == inspect.Parameter.VAR_KEYWORD:
                for kwarg_name, kwarg_obj in arg_obj.items():
                    self.add_args_l_entry__(kwarg_name, kwarg_obj)
            elif arg_kind == inspect.Parameter.VAR_POSITIONAL:
                # ipdb.set_trace()
                for p_arg_obj in arg_obj:
                    self.add_args_l_entry__(None, p_arg_obj)
            else:
                self.add_args_l_entry__(arg_name, arg_obj)
        
    def handle_start_method_call(self, method_name, method_signature, method_args, method_kwargs):
        if method_name == "pin":
            arg0_obj = method_args[0]
            arg0_obj_id, found = obj_tracking.get_tracking_obj(arg0_obj)
            if found:
                rdf_io.CCBasicPlot().to_rdf(arg0_obj, arg0_obj_id.last_obj_state.back.uri)
            else:
                raise Exception("logical error: expected to have obj state created before")
            return method_args, method_kwargs
            
        self.thread_id = threading.get_native_id()

        all_args = method_args
        self.method_signature = method_signature
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
            if arg_kind == inspect.Parameter.VAR_KEYWORD:
                # case for lambda args of assign
                updates_d = {}
                for kwarg_name, kwarg_value in arg_value.items():
                    if inspect.isfunction(kwarg_value):
                        # create empty nested call obj as placeholder for future results
                        new_kwarg_value = NestedCall(kwarg_name, kwarg_value)
                        updates_d[kwarg_name] = new_kwarg_value
                self.method_bound_args.arguments[arg_name].update(updates_d)

        self.build_args_l__()
        
        new_args = self.method_bound_args.args
        new_kwargs = self.method_bound_args.kwargs
        
        # NB: since apply_defaults is not called then no tracking of args with default values will take place
        self.back.dump_rdf_method_call_in()

        return new_args, new_kwargs

    def handle_end_method_call(self, ret):
        if self.method_name == "pin":
            return

        if ret is None:
            raise Exception(f"method call of {self.method_name} returned None, can't use it chained method calls")
        
        ret_obj_id, found = obj_tracking.get_tracking_obj(ret)
        if found:
            ret_obj_id.last_version_num += 1

        # since we don't know was object state changed or not
        # we create new object state and set it as last obj state in obj id
        self.ret_obj_state = obj_utils.ObjState(ret, ret_obj_id)
        
        self.back.dump_rdf_method_call_out()
