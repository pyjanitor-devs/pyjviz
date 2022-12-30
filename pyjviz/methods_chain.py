import threading
import uuid
import pandas as pd
from . import uw
#from . import obj_tracking
from . import rdflogging

curr_methods_chain_path = None

class MethodsChain:
    def __init__(self, chain_path = "top"):
        self.chain_path = chain_path

    def __enter__(self):
        print(f"enter chain {self.chain_path}")
        global curr_methods_chain_path

        if curr_methods_chain_path is None:
            curr_methods_chain_path = []
        curr_methods_chain_path.append(self.chain_path)
            
        return self

    def __exit__(self, type, value, traceback):
        print(f"exit chain {self.chain_path}")
        global curr_methods_chain_path
        
        curr_methods_chain_path.pop()
        if len(curr_methods_chain_path) == 0:
            curr_methods_chain_path = None
