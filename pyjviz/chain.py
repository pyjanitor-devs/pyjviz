import threading
import pandas as pd
from . import uw
from . import obj_tracking
from . import rdflogging

class Chain:
    def __init__(self, chain_name, parent_chain = None):
        self.is_active = False
        self.chain_name = chain_name
        self.parent_chain = parent_chain
        
    def __enter__(self):
        self.is_active = True
        print(f"enter chain {self.chain_name}")
        return self

    def __exit__(self, type, value, traceback):
        self.is_active = False
        print(f"exit chain {self.chain_name}")

    def __del__(self):
        print(f"deleting chain {self.chain_name} {id(self)}")
        
    def pin(self, orig_obj):
        obj = uw.UWObject(orig_obj)
        t_obj = obj_tracking.tracking_store.set_tracking_obj_attr(obj, 'obj_chain', self)
        rdflogging.rdflogger.register_osca(t_obj, self)
        return obj
