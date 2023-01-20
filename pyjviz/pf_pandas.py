import ipdb
import threading
import pandas as pd
import pandas_flavor as pf
import inspect
import uuid
from contextlib import nullcontext

from . import rdflogging
from . import obj_tracking
from . import methods_chain
from . import call_stack

class CallbackObj:
    def __init__(self, chain_path, func):
        self.chain_path = chain_path
        self.func = func
        self.ret = None
        self.uri = None

    def __call__(self, *args, **kwargs):
        print("CallbackOBJ called")
        self.ret = self.func(*args, **kwargs)
        #ipdb.set_trace()
        return self.ret

class DataFrameAttr:
    def __init__(self, func):
        self.func = func

    def __call__(self, *x, **y):
        print("DataFrameAttr __call__", x[1], y)
        rdfl = rdflogging.rdflogger
        if call_stack.stack.size() == 0:
            ret_obj = self.func(*x, **y)
        else:
            chain_path = call_stack.stack.to_string()
        
            x0_obj = x[0]
            ret_obj = self.func(*x, **y)

            x0_t_obj = obj_tracking.tracking_store.get_tracking_obj(x0_obj)
            if x0_t_obj.last_obj_state_uri is None:
                x0_t_obj.last_obj_state_uri = rdfl.dump_obj_state(chain_path, x0_obj, x0_t_obj)

            ret_t_obj = obj_tracking.tracking_store.get_tracking_obj(ret_obj)
            if ret_t_obj.last_obj_state_uri is None:
                ret_t_obj.last_obj_state_uri = rdfl.dump_obj_state(chain_path, ret_obj, ret_t_obj)

            rdfl.dump_triple__(ret_t_obj.last_obj_state_uri, "<df-projection>", x0_t_obj.last_obj_state_uri)
        
        return ret_obj

class Caller_to_datetime:
    def __init__(self, func):
        self.func = func

    def __call__(self, *x, **y):
        print("Caller_to_datetime __call__", x, y)
        #ipdb.set_trace()
        rdfl = rdflogging.rdflogger
        if call_stack.stack.size() == 0:
            ret_obj = self.func(*x, **y)
        else:
            chain_path = call_stack.stack.to_string()
        
            x0_obj = x[0]
            ret_obj = self.func(*x, **y)

            x0_t_obj = obj_tracking.tracking_store.get_tracking_obj(x0_obj)
            if x0_t_obj.last_obj_state_uri is None:
                x0_t_obj.last_obj_state_uri = rdfl.dump_obj_state(chain_path, x0_obj, x0_t_obj)

            ret_t_obj = obj_tracking.tracking_store.get_tracking_obj(ret_obj)
            if ret_t_obj.last_obj_state_uri is None:
                ret_t_obj.last_obj_state_uri = rdfl.dump_obj_state(chain_path, ret_obj, ret_t_obj)

            rdfl.dump_triple__(ret_t_obj.last_obj_state_uri, "<to_datetime>", x0_t_obj.last_obj_state_uri)
        
        return ret_obj
    
def enable_pf_pandas__():
    pf.register.cb_create_call_stack_context_manager = cb_create_method_call_context_manager
    
    old_DataFrame_init = pd.DataFrame.__init__
    def aux_init(func, *x, **y):
        #print("aux init")
        #ipdb.set_trace()
        ret = func(*x, **y)
        return ret
    
    pd.DataFrame.__init__ = lambda *x, **y: aux_init(old_DataFrame_init, *x, **y)
    
    if 1:
        old_getattr = pd.DataFrame.__getattr__
        pd.DataFrame.__getattr__ = lambda *x, **y: DataFrameAttr(old_getattr)(*x, *y)
   
    if 1:
        old_to_datetime = pd.to_datetime
        pd.to_datetime = lambda *x, **y: Caller_to_datetime(old_to_datetime)(*x, **y)
        
    old_describe = pd.DataFrame.describe
    #del pd.DataFrame.describe

    @pf.register_dataframe_method
    def describe(df: pd.DataFrame) -> pd.DataFrame:
        print("override describe")
        return old_describe(df)

    old_dropna = pd.DataFrame.dropna; del pd.DataFrame.dropna
    old_drop = pd.DataFrame.drop; del pd.DataFrame.drop
    old_rename = pd.DataFrame.rename; del pd.DataFrame.rename
    old_assign = pd.DataFrame.assign; del pd.DataFrame.assign
    old_copy = pd.DataFrame.copy
    
    old_combine_first = pd.Series.combine_first
    
    @pf.register_dataframe_method
    def dropna(df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        print("call dropna")
        ret = old_dropna(df, **kwargs)
        #print("my dropna", id(df), id(ret))
        return ret

    @pf.register_dataframe_method
    def drop(df: pd.DataFrame, *x, **y) -> pd.DataFrame:
        #ipdb.set_trace()
        ret = old_drop(df, *x, **y)
        #print("my drop", id(df), id(ret))
        return ret

    @pf.register_dataframe_method
    def rename(df: pd.DataFrame, columns) -> pd.DataFrame:
        print("my rename", id(df))
        #ipdb.set_trace()
        ret = old_rename(df, columns = columns)
        return ret

    @pf.register_dataframe_method
    def assign(df: pd.DataFrame, **kw) -> pd.DataFrame:
        ret = old_assign(df, **kw)
        #print("my assign", id(df), id(ret))
        return ret

    @pf.register_dataframe_method
    def copy(df: pd.DataFrame, *x, **y) -> pd.DataFrame:
        print("new copy:", x, y)
        ret = old_copy(df, *x, **y)
        return ret
    
    @pf.register_series_method
    def combine_first(s: pd.Series, other) -> pd.Series:
        ret = old_combine_first(s, other)
        return ret
    

# pandas_flavor register.py callback

class MethodCall(call_stack.StackEntry):
    def __init__(self, method_name):
        super().__init__(rdf_type_uri = "<MethodCall>")
        self.method_bound_args = None
        #ipdb.set_trace()
        self.uri = f"<MethodCall#{str(uuid.uuid4())}>"
        self.method_name = method_name
        rdfl = rdflogging.rdflogger
        rdfl.dump_triple__(self.uri, "rdf:type", self.rdf_type_uri)

    def __enter__(self):
        call_stack.stack.push(self)
        return self
        
    def __exit__(self, type, value, traceback):
        call_stack.stack.pop()
        
    def handle_start_method_call(self, obj, method_name, method_signature, method_args, method_kwargs):
        rdfl = rdflogging.rdflogger
        
        all_args = tuple([obj] + list(method_args))
        self.method_signature = method_signature
        self.method_bound_args = self.method_signature.bind(*all_args, **method_kwargs)
        self.method_bound_args.apply_defaults()

        updates_d = {}
        for arg_name, arg_value in self.method_bound_args.arguments.items():
            arg_kind = method_signature.parameters.get(arg_name).kind
            print(method_name, arg_name, arg_kind)
            if arg_kind == inspect.Parameter.VAR_KEYWORD: # case for lambda args of assign
                for kwarg_name, kwarg_value in arg_value.items():
                    if inspect.isfunction(kwarg_value):
                        new_kwarg_value = CallbackObj(call_stack.stack.to_string(), kwarg_value) # create empty callback obj as placeholder for future results
                        updates_d[kwarg_name] = new_kwarg_value                        
                self.method_bound_args.arguments[arg_name].update(updates_d); updates_d = {}

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
        for arg_name, arg_value in self.method_bound_args.arguments.items():
            arg_kind = self.method_signature.parameters.get(arg_name).kind
            if arg_kind == inspect.Parameter.VAR_KEYWORD:
                for kwarg_name, kwarg_value in arg_value.items():
                    if isinstance(kwarg_value, CallbackObj):
                        arg_obj = kwarg_value
                        arg_t_obj = obj_tracking.tracking_store.get_tracking_obj(arg_obj.ret)
                        if arg_t_obj.last_obj_state_uri is None:
                            arg_t_obj.last_obj_state_uri = rdfl.dump_obj_state(self.chain_path, arg_obj.ret, arg_t_obj)
                        rdfl.dump_triple__(arg_obj.uri, "<ret-val>", arg_t_obj.last_obj_state_uri)


def cb_create_method_call_context_manager(method_name):
    return MethodCall(method_name) if call_stack.stack.size() > 0 else nullcontext()
    
                        
"""
def cb_notify_dataframe_method_call(obj, method_name, method_signature, method_args, method_kwargs):
    result = None
    print("pyjviz call stack:", call_stack.stack.to_string())
    #cond = call_stack.call_stack.size() == 1 or (call_stack.call_stack.size() == 2 and call_stack.call_stack.calls[-1] == "copy")
    #cond = cond and not (call_stack.call_stack.size() >= 2 and call_stack.call_stack.calls[-1] == "copy" and call_stack.call_stack.calls[-2] == "rename")
    cond = True
    if call_stack.stack.size() > 0 and cond:
        result = MethodCallHandler(obj, method_name, method_signature, method_args, method_kwargs)
    return result

def cb_notify_series_method_call(obj, method_name, method_signature, method_args, method_kwargs):
    result = None
    print("pyjviz call stack:", call_stack.stack.to_string())
    #cond = call_stack.stack.size() <= 2
    cond = True
    if call_stack.stack.size() > 0 and cond:
        result = MethodCallHandler(obj, method_name, method_signature, method_args, method_kwargs)
    return result
"""     
