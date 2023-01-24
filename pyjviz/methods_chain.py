import ipdb
import threading
import pandas as pd
import inspect
import uuid

from . import call_stack
from . import rdflogging
from . import obj_tracking

class SubGraph(call_stack.CallStackEntry):
    def __init__(self, label, rdf_type = "SubGraph"):
        super().__init__(label = label, rdf_type = rdf_type)
        
class CallbackObj:
    def __init__(self, arg_name, arg_func):
        #super().__init__(label = f"callback({arg_name})", rdf_type = "CallbackObj")
        self.label = f"callback({arg_name})"
        self.rdf_type = "CallbackObj"
        self.uri = f"<CallbackObj#{str(uuid.uuid4())}>"
        
        self.arg_name = arg_name
        self.arg_func = arg_func
        self.ret = None

        #self.init_dump__(rdflogging.rdflogger)
        rdfl = rdflogging.rdflogger
        rdf_type_uri = f"<{self.rdf_type}>"
        rdfl.dump_triple__(self.uri, "rdf:type", rdf_type_uri)
        rdfl.dump_triple__(self.uri, "rdf:label", '"' + self.label + '"')
        parent_uri = call_stack.stack.stack_entries[-1].uri if call_stack.stack.size() > 0 else "rdf:nil"
        rdfl.dump_triple__(self.uri, "<part-of>", parent_uri)
        
    def __call__(self, *args, **kwargs):
        print("CallbackOBJ called")
        self.ret = self.arg_func(*args, **kwargs)
        #ipdb.set_trace()
        return self.ret
        
class MethodCall(SubGraph):
    def __init__(self, method_name, will_have_cb_args):
        super().__init__(label = method_name, rdf_type = "MethodCall")
        self.method_bound_args = None
        self.will_have_cb_args = will_have_cb_args
        self.cb_args = []
        
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
                        new_kwarg_value = CallbackObj(kwarg_name, kwarg_value) # create empty callback obj as placeholder for future results
                        updates_d[kwarg_name] = new_kwarg_value
                        self.cb_args.append(new_kwarg_value)
                self.method_bound_args.arguments[arg_name].update(updates_d)

        new_args = self.method_bound_args.args
        new_kwargs = self.method_bound_args.kwargs

        #ipdb.set_trace()
        t_obj = obj_tracking.tracking_store.get_tracking_obj(obj)
        thread_id = threading.get_native_id()
        caller_stack_entry = call_stack.stack.stack_entries[-2]
        rdfl.dump_method_call_in(self, thread_id, obj, t_obj,
                                 method_name, method_signature, self.method_bound_args,
                                 caller_stack_entry)

        return new_args, new_kwargs

    def handle_end_method_call(self, ret):
        rdfl = rdflogging.rdflogger
        ret_obj = ret if not ret is None else obj

        ret_t_obj = obj_tracking.tracking_store.get_tracking_obj(ret_obj)

        caller_stack_entry = call_stack.stack.stack_entries[-2]
        ret_t_obj.last_obj_state_uri = rdfl.dump_obj_state(ret_obj, ret_t_obj, caller_stack_entry)
        rdfl.dump_triple__(self.uri, "<method-call-return>", ret_t_obj.last_obj_state_uri)

        # catching arg callback values returned after method call executed all callbacks
        for cb_arg_obj in self.cb_args:
            arg_t_obj = obj_tracking.tracking_store.get_tracking_obj(cb_arg_obj.ret)
            if arg_t_obj.last_obj_state_uri is None:
                raise Exception("expected to have uri assigned")
            rdfl.dump_triple__(cb_arg_obj.uri, "<ret-val>", arg_t_obj.last_obj_state_uri)
