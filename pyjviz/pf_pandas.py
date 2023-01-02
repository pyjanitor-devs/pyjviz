import ipdb
import threading
import pandas as pd
import pandas_flavor as pf

from . import rdflogging
from . import obj_tracking
from . import methods_chain

def enable_pf_pandas__():
    print("pf_pandas.py: register handle_pandas_method_call")
    pf.register.handle_pandas_method_call = handle_pandas_method_call

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

    @pf.register_dataframe_method
    def dropna(df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        print("call dropna")
        ret = old_dropna(df, **kwargs)
        #print("my dropna", id(df), id(ret))
        return ret

    @pf.register_dataframe_method
    def drop(df: pd.DataFrame, columns) -> pd.DataFrame:
        ret = old_drop(df, columns = columns)
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

"""
@pf.register_dataframe_method
def set_chain(df: pd.DataFrame, chain_path: str) -> pd.DataFrame:
    #ipdb.set_trace()
    global curr_methods_chain
    curr_methods_chain_path.set_savepoint(...)
    
    if methods_chain.curr_methods_chain_path is None:
        methods_chain.curr_methods_chain_path = []
    methods_chain.curr_methods_chain_path.append(chain_path)

    return df

@pf.register_dataframe_method
def reset_chain(df: pd.DataFrame) -> pd.DataFrame:
    #global curr_methods_chain_path

    methods_chain.curr_methods_chain_path.pop()
    if len(methods_chain.curr_methods_chain_path) == 0:
        methods_chain.curr_methods_chain_path = None

    return df
"""   

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
    
