import threading
import uuid
import pandas as pd
from . import uw
#from . import obj_tracking
from . import rdflogging

curr_methods_chain_path = None

class MethodsChain:
    def __init__(self, chain_path):
        self.chain_path = chain_path

    def __enter__(self):
        print(f"enter chain {self.chain_path}")
        global curr_methods_chain_path
        curr_methods_chain_path = self.chain_path
        return self

    def __exit__(self, type, value, traceback):
        print(f"exit chain {self.chain_path}")
        global curr_methods_chain_path
        curr_methods_chain_path = None
