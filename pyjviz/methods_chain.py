import threading
import uuid
import pandas as pd
from . import uw
#from . import obj_tracking
from . import rdflogging

curr_methods_chain = None

class MethodsChain:
    def __init__(self, chain_name, parent_chain = None):
        self.uuid = uuid.uuid4()
        self.chain_name = chain_name
        self.parent_chain = parent_chain
        
    def __enter__(self):
        print(f"enter chain {self.chain_name}")
        global curr_methods_chain
        curr_methods_chain = self
        return self

    def __exit__(self, type, value, traceback):
        print(f"exit chain {self.chain_name}")
        global curr_methods_chain
        curr_methods_chain = None

    def __del__(self):
        print(f"deleting chain {self.chain_name} {id(self)}")
