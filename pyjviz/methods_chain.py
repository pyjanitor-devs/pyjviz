#import ipdb
import threading
import uuid
import pandas as pd
import graphviz

from . import rdflogging
from . import nb_utils
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
        self.uuid = uuid.uuid4()
        self.chain_path = chain_path

    def __enter__(self):
        print(f"enter chain {self.chain_path}")
        global curr_methods_chain

        if curr_methods_chain is None:
            curr_methods_chain = MethodsChainPath()
        curr_methods_chain.handle_with_enter(self.chain_path)
        return self

    def __exit__(self, type, value, traceback):
        rdflogging.rdflogger.flush__()

        print(f"exit chain {self.chain_path}")
        global curr_methods_chain
        
        curr_methods_chain.handle_with_exit()
        if len(curr_methods_chain.path) == 0:
            curr_methods_chain = None

    def print_dot(self, vertical = False, show_objects = False):
        #ipdb.set_trace()
        g = rdflogging.rdflogger.triples_sink.get_graph()
        print(viz.dump_dot_code(g, vertical = vertical, show_objects = show_objects))

    def save_dot(self, dot_output_fn = None, vertical = False, show_objects = False):
        ts = rdflogging.rdflogger.triples_sink
        if dot_output_fn is None:
            if hasattr(ts, 'output_fn') and ts.output_fn is not None:
                ttl_output_fn = ts.output_fn
                dot_output_fn = ttl_output_fn + ".dot"
            else:
                raise Exception("can't guess dot_output_fn")
            
        g = ts.get_graph()
        dot_code = viz.dump_dot_code(g, vertical = vertical, show_objects = show_objects)
        gvz = graphviz.Source(dot_code)
        gvz.render(dot_output_fn, format = 'png', engine = 'dot')

    def show(self, vertical = False, show_objects = False):
        ts = rdflogging.rdflogger.triples_sink
        if not (hasattr(ts, 'output_fn') and ts.output_fn is None):
            raise Exception("triple sink is not in-memory file")
        
        g = ts.get_graph()
        dot_code = viz.dump_dot_code(g, vertical = vertical, show_objects = show_objects)
        nb_utils.show_method_chain(dot_code)
        
