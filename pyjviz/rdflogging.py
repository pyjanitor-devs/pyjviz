# pyjrdf to keep all rdf logging functionality
#
import ipdb
import sys, tempfile
import os.path
import textwrap
import pandas as pd
import uuid

import pandas_flavor as pf

from . import obj_tracking
from . import wb_stack

base_uri = 'https://github.com/pyjanitor-devs/pyjviz/rdflog.shacl.ttl#'

def get_obj_type(o):
    if isinstance(o, pd.DataFrame):
        ret = "DataFrame"
    elif isinstance(o, pd.Series):
        ret = "Series"
    else:
        raise Exception(f"unknown type of o: {str(type(o))}")

    return ret

def show_obj(edge_uri, pyjviz_obj):
    if not isinstance(pyjviz_obj, pd.DataFrame):
        raise Exception("obj of type {type((pyjviz_obj)} is not supported")

    subj_uri = wb_stack.wb_stack.get_top().uri
    parent_obj_uri = wb_stack.wb_stack.get_parent_code_context_of_current_entry().uri
    show_obj_uri = f"<ShowObj#{rdflogger.random_id}>"; rdflogger.random_id += 1
    rdflogger.dump_triple__(show_obj_uri, "rdf:type", "<ShowObj>")
    rdflogger.dump_triple__(show_obj_uri, "<part-of>", parent_obj_uri)
    rdflogger.dump_triple__(subj_uri, edge_uri, show_obj_uri)
    rdflogger.dump_DataFrame_obj_state(show_obj_uri, pyjviz_obj)

class RDFLogger:        
    def __init__(self, triples_sink):
        self.triples_sink = triples_sink
        self.known_threads = {}
        self.known_objs = {}
        self.random_id = 0 # should be better way

    def flush__(self):
        self.triples_sink.flush()
        #self.out_fd.flush()
        
    def dump_triple__(self, subj, pred, obj):
        self.triples_sink.dump_triple(subj, pred, obj)
        #print(subj, pred, obj, ".", file = self.out_fd)

    def register_obj__(self, obj, t_obj):
        obj_uuid = str(t_obj.uuid)
        obj_pyid = t_obj.pyid
        if obj_uuid in self.known_objs:
            ret_uri = self.known_objs[obj_uuid]
        else:
            ret_uri = self.known_objs[obj_uuid] = f"<Obj#{obj_uuid}>"
            self.dump_triple__(ret_uri, "rdf:type", "<Obj>")
            self.dump_triple__(ret_uri, "<obj-type>", f'"{get_obj_type(obj)}"')
            self.dump_triple__(ret_uri, "<obj-uuid>", f'"{obj_uuid}"')
            self.dump_triple__(ret_uri, "<obj-pyid>", f'{obj_pyid}')

        return ret_uri

    def register_thread(self, thread_id):
        if not thread_id in self.known_threads:            
            thread_uri = self.known_threads[thread_id] = f"<Thread#{thread_id}>"
            self.dump_triple__(thread_uri, "rdf:type", "<Thread>")
        else:
            thread_uri = self.known_threads[thread_id]
        return thread_uri
            
    def dump_obj_state(self, obj, t_obj, parent_obj):
        obj_uri = self.register_obj__(obj, t_obj)
        obj_state_uri = f"<ObjState#{self.random_id}>"; self.random_id += 1

        df = obj
        #ipdb.set_trace()
        self.dump_triple__(obj_state_uri, "rdf:type", "<ObjState>")
        self.dump_triple__(obj_state_uri, "<obj>", obj_uri)
        self.dump_triple__(obj_state_uri, "<version>", f'"{t_obj.last_version_num}"')
        t_obj.last_version_num += 1
        self.dump_triple__(obj_state_uri, "<part-of>", parent_obj.uri)

        if isinstance(obj, pd.DataFrame):
            self.dump_DataFrame_obj_state(obj_state_uri, obj)
        elif isinstance(obj, pd.Series):
            self.dump_Series_obj_state(obj_state_uri, obj)
        else:
            raise Exception(f"unknown obj type at {obj_state_uri}")

        return obj_state_uri

    def dump_DataFrame_obj_state(self, obj_state_uri, df, kwargs = {'show-head': True}):
        self.dump_triple__(obj_state_uri, "<df-shape>", f'"{df.shape}"')
        if kwargs.get('show-head', False) == True:
            df_head_html = df.head().applymap(lambda x: textwrap.shorten(str(x), 50)).to_html().replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("\n", "&#10;")
            self.dump_triple__(obj_state_uri, "<df-head>", '"' + df_head_html + '"')

    def dump_Series_obj_state(self, obj_state_uri, s):
        self.dump_triple__(obj_state_uri, "<df-shape>", f'"{s.shape}"')        

    
rdflogger = None
def set_rdflogger__(o):
    global rdflogger
    rdflogger = o

