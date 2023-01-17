import threading
import uuid
import pandas as pd

from . import rdflogging
from . import viz

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
        if rdflogging.rdflogger is None:
            rdflogging.RDFLogger.init()

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

    def show(self, vertical = False):
        import graphviz
        from IPython.display import display
        import rdflib

        rdflogging.RDFLogger.flush()
        g = rdflib.Graph()
        print("LOGGER:", rdflogging.rdflogger.out_filename)
        g.parse(rdflogging.rdflogger.out_filename)
        dot_code = viz.dump_dot_code(g, vertical, show_objects = False)

        source = dot_code
        #print(source)
        gvz = graphviz.Source(source)
        display(gvz)
