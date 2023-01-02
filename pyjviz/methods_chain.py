import threading
import uuid
import pandas as pd
from . import rdflogging

class MethodsChainPath:
    def __init__(self):
        self.path = []

    def get_path(self):
        return "/" + "/".join(self.path)
        
    def handle_with_enter(self, path):
        self.path.append(path)

    def handle_with_exit(self):
        self.path.pop()
        
curr_methods_chain = None
        
class MethodsChain:
    def __init__(self, chain_path = "top"):
        self.chain_path = chain_path

    def __enter__(self):
        print(f"enter chain {self.chain_path}")
        global curr_methods_chain

        if curr_methods_chain is None:
            curr_methods_chain = MethodsChainPath()
        curr_methods_chain.handle_with_enter(self.chain_path)
        return self

    def __exit__(self, type, value, traceback):
        print(f"exit chain {self.chain_path}")
        global curr_methods_chain
        
        curr_methods_chain.handle_with_exit()
        if len(curr_methods_chain.path) == 0:
            curr_methods_chain = None
