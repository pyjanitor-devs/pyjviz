import ipdb
import threading
import pandas as pd
import pandas_flavor as pf
import inspect

from . import rdflogging
from . import obj_tracking
from . import methods_chain

class CallbackObj:
    def __init__(self, chain_path, func):
        self.chain_path = chain_path
        self.func = func
        self.ret = None
        self.uri = None

    def __call__(self, *args, **kwargs):
        self.ret = self.func(*args, **kwargs)
        #ipdb.set_trace()
        return self.ret

class DataFrameAttr:
    def __init__(self, func):
        self.func = func

    def __call__(self, *x, **y):
        print("DataFrameAttr __call__", x[1], y)
        rdfl = rdflogging.rdflogger
        if methods_chain.curr_methods_chain is None:
            ret_obj = self.func(*x, **y)
        else:
            chain_path = methods_chain.curr_methods_chain.get_path()
        
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
        ret = self.func(*x, **y)

        rdfl = rdflogging.rdflogger
        x0_t_obj = obj_tracking.tracking_store.get_tracking_obj(x[0])
        x0_uri = rdfl.register_obj(x[0], x0_t_obj)
        t_ret = obj_tracking.tracking_store.get_tracking_obj(ret)
        ret_uri = rdfl.register_obj(ret, t_ret)
        rdfl.dump_triple__(ret_uri, "<to_datetime>", x0_uri)
        
        return ret
    
def enable_pf_pandas__():
    print("pf_pandas.py: register start_method_call")
    pf.register.start_method_call = start_method_call

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
    def combine_first(s: pd.Series, *args, **kw) -> pd.Series:
        ret = old_combine_first(s, *args, **kw)
        return ret
    

# pandas_flavor register.py callback
    
class MethodCallHandler:
    def __init__(self, obj, method_name, method_args, method_kwargs):
        self.obj = obj
        self.method_name = method_name
        self.method_args = method_args
        self.method_kwargs = method_kwargs
        self.chain_path = None
        self.method_call_uri = None
        
    def handle_start_method_call(self):
        rdfl = rdflogging.rdflogger

        #ipdb.set_trace()
        for k, arg in self.method_kwargs.items():
            if inspect.isfunction(arg):
                self.method_kwargs[k] = CallbackObj(methods_chain.curr_methods_chain.get_path(), arg) # create empty callback obj as placeholder for future results
            else:
                self.method_kwargs[k] = arg

        t_obj = obj_tracking.tracking_store.get_tracking_obj(self.obj)
        self.chain_path = methods_chain.curr_methods_chain.get_path()
        thread_id = threading.get_native_id()
        self.method_call_uri = rdfl.dump_method_call_in(self.chain_path, thread_id, self.obj, t_obj, self.method_name, self.method_args, self.method_kwargs)                
        #curr_call_contexts.clear()

    def handle_end_method_call(self, ret):
        rdfl = rdflogging.rdflogger
        ret_obj = ret if not ret is None else obj

        ret_t_obj = obj_tracking.tracking_store.get_tracking_obj(ret_obj)

        ret_t_obj.last_obj_state_uri = rdfl.dump_obj_state(self.chain_path, ret_obj, ret_t_obj)
        rdfl.dump_triple__(self.method_call_uri, "<method-call-return>", ret_t_obj.last_obj_state_uri)

        # catching arg callback values returned after method call executed all callbacks
        all_args = list(self.method_args) + list(self.method_kwargs.values())
        for arg_obj in all_args:
            if isinstance(arg_obj, CallbackObj):
                arg_t_obj = obj_tracking.tracking_store.get_tracking_obj(arg_obj.ret)
                if arg_t_obj.last_obj_state_uri is None:
                    arg_t_obj.last_obj_state_uri = rdfl.dump_obj_state(self.chain_path, arg_obj.ret, arg_t_obj)
                rdfl.dump_triple__(arg_obj.uri, "<ret-val>", arg_t_obj.last_obj_state_uri)
   
def start_method_call(obj, method_name, method_args, method_kwargs):
    print("start_method_call", id(obj))

    result = None
    if methods_chain.curr_methods_chain:
        result = MethodCallHandler(obj, method_name, method_args, method_kwargs)
        result.handle_start_method_call()
    return result
