import ipdb
import threading
import uuid
import pandas as pd
import graphviz

from . import call_stack
from . import rdflogging
from . import nb_utils
from . import viz

class SubGraph(call_stack.StackEntry):
    def __init__(self, subgraph_label = None):
        super().__init__(rdf_type_uri = "<SubGraph>")
        self.subgraph_label = subgraph_label
        self.uri = f"<SubGraph#{str(uuid.uuid4())}>"

        rdfl = rdflogging.rdflogger
        rdfl.dump_triple__(self.uri, "rdf:type", self.rdf_type_uri)
        rdfl.dump_triple__(self.uri, "rdf:label", '"' + self.subgraph_label + '"')
        
    def __enter__(self):
        call_stack.stack.push(self)
        return self

    def __exit__(self, type, value, traceback):
        rdflogging.rdflogger.flush__()
        call_stack.stack.pop()

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
        
