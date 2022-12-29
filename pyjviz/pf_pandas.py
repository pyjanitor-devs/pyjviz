import ipdb
import threading
import pandas as pd
import pandas_flavor as pf

from . import rdflogging
from . import obj_tracking
from . import methods_chain
from . import uw

def enable_pf_pandas():
    pf.register.handle_pandas_method_call = handle_pandas_method_call

    old_describe = pd.DataFrame.describe
    #del pd.DataFrame.describe

    @pf.register_dataframe_method
    def describe(df: pd.DataFrame) -> pd.DataFrame:
        print("override describe")
        return old_describe(df)

    
def handle_pandas_method_call(obj, method_name, method_args, method_kwargs, ret):
    print("handle_pandas_method_call", id(obj))
    
    rdfl = rdflogging.rdflogger

    print("__call__", method_name)
    #ipdb.set_trace()

    t_obj = obj_tracking.tracking_store.get_tracking_obj(obj)
    if methods_chain.curr_methods_chain_path:
        t_obj.obj_chain_path = methods_chain.curr_methods_chain_path if t_obj.obj_chain_path is None else t_obj.obj_chain_path

    if t_obj.obj_chain_path:
        thread_id = threading.get_native_id()
        method_call_uri = rdfl.dump_method_call_in(thread_id, obj, t_obj, method_name, method_args, method_kwargs)

    if ret is None:
        ret = obj

    if t_obj.obj_chain_path is None:
        ret_obj = ret
    else:
        ret_obj = ret
        ret_t_obj = obj_tracking.tracking_store.get_tracking_obj(ret_obj)
        ret_t_obj.obj_chain_path = t_obj.obj_chain_path

        ret_t_obj.last_obj_state_uri = rdfl.dump_obj_state(ret_obj, ret_t_obj)
        rdfl.dump_triple__(method_call_uri, "<method-call-return>", ret_t_obj.last_obj_state_uri)
    
