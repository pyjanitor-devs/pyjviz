import ipdb
import threading
import pandas as pd
import pandas_flavor as pf
import uuid
from contextlib import nullcontext

from . import rdflogging
from . import obj_tracking
from . import methods_chain
from . import call_stack

class DataFrameAttr:
    def __init__(self, func):
        self.func = func

    def __call__(self, *x, **y):
        print("DataFrameAttr __call__", x[1], y)
        rdfl = rdflogging.rdflogger
        if call_stack.stack.size() == 0:
            ret_obj = self.func(*x, **y)
        else:
            caller_stacke_entry = call_stack.stack.stack_entries[-1]
            
            x0_obj = x[0]
            ret_obj = self.func(*x, **y)

            x0_t_obj = obj_tracking.tracking_store.get_tracking_obj(x0_obj)
            if x0_t_obj.last_obj_state_uri is None:
                x0_t_obj.last_obj_state_uri = rdfl.dump_obj_state(x0_obj, x0_t_obj, caller_stacke_entry)

            ret_t_obj = obj_tracking.tracking_store.get_tracking_obj(ret_obj)
            if ret_t_obj.last_obj_state_uri is None:
                ret_t_obj.last_obj_state_uri = rdfl.dump_obj_state(ret_obj, ret_t_obj, caller_stacke_entry)

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
            caller_stacke_entry = call_stack.stack.stack_entries[-2]
        
            x0_obj = x[0]
            ret_obj = self.func(*x, **y)

            x0_t_obj = obj_tracking.tracking_store.get_tracking_obj(x0_obj)
            if x0_t_obj.last_obj_state_uri is None:
                x0_t_obj.last_obj_state_uri = rdfl.dump_obj_state(x0_obj, x0_t_obj, caller_stacke_entry)

            ret_t_obj = obj_tracking.tracking_store.get_tracking_obj(ret_obj)
            if ret_t_obj.last_obj_state_uri is None:
                ret_t_obj.last_obj_state_uri = rdfl.dump_obj_state(ret_obj, ret_t_obj, caller_stacke_entry)

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

def cb_create_method_call_context_manager(method_name):
    if call_stack.stack.size() == 0:
        return nullcontext()

    method_calls = call_stack.stack.to_methods_calls() + [method_name]
    print("method_calls:", method_calls)
    if len(method_calls) == 1:
        ret = methods_chain.MethodCall(method_name)
    elif len(method_calls) == 2 and method_calls[-2] == 'assign':
        ret = methods_chain.MethodCall(method_name)
    else:
        ret = nullcontext()
        
    return ret
