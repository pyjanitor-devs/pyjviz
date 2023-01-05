import ipdb
import threading
import pandas as pd
import pandas_flavor as pf

from . import rdflogging
from . import obj_tracking
from . import methods_chain

class DataFrameAttr:
    def __init__(self, func):
        self.func = func

    def __call__(self, *x, **y):
        ipdb.set_trace()
        print("Caller __call__", x, y)
        return self.func(*x, **y)

def enable_pf_pandas__():
    print("pf_pandas.py: register handle_pandas_method_call")
    pf.register.handle_pandas_method_call = handle_pandas_method_call

    if 0: # TBC
        old_getattr = pd.DataFrame.__getattr__
        pd.DataFrame.__getattr__ = lambda *x, **y: DataFrameAttr(old_getattr)(*x, *y)
    
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
        ret = old_rename(df, columns = columns)
        #print("my rename", id(df), id(ret))
        return ret

    @pf.register_dataframe_method
    def assign(df: pd.DataFrame, **kw) -> pd.DataFrame:
        ret = old_assign(df, **kw)
        #print("my assign", id(df), id(ret))
        return ret

    @pf.register_series_method
    def combine_first(s: pd.Series, *args, **kw) -> pd.Series:
        ret = old_combine_first(s, *args, **kw)
        return ret
    

def handle_pandas_method_call(obj, method_name, method_args, method_kwargs, ret):
    print("handle_pandas_method_call", id(obj))

    if method_name in ['set_chain', 'reset_chain']:
        return
    
    rdfl = rdflogging.rdflogger

    print("__call__", method_name)
    #ipdb.set_trace()

    t_obj = obj_tracking.tracking_store.get_tracking_obj(obj)
    if methods_chain.curr_methods_chain:
        chain_path = methods_chain.curr_methods_chain.get_path()
        thread_id = threading.get_native_id()
        method_call_uri = rdfl.dump_method_call_in(chain_path, thread_id, obj, t_obj, method_name, method_args, method_kwargs)

        ret_obj = ret if not ret is None else obj

        ret_t_obj = obj_tracking.tracking_store.get_tracking_obj(ret_obj)

        ret_t_obj.last_obj_state_uri = rdfl.dump_obj_state(chain_path, ret_obj, ret_t_obj)
        rdfl.dump_triple__(method_call_uri, "<method-call-return>", ret_t_obj.last_obj_state_uri)
    
