# pyjrdf to keep all rdf logging functionality
#
import ipdb
import sys, tempfile
import os.path
import textwrap
import pandas as pd
import uuid
import base64
import inspect

import pandas_flavor as pf

from . import obj_tracking
from . import methods_chain
from . import call_stack

base_uri = 'https://github.com/pyjanitor-devs/pyjviz/rdflog.shacl.ttl#'
method_counter = 0

def get_obj_type(o):
    if isinstance(o, pd.DataFrame):
        ret = "DataFrame"
    elif isinstance(o, pd.Series):
        ret = "Series"
    else:
        raise Exception(f"unknown type of o: {str(type(o))}")

    return ret
    
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

    def dump_method_call_arg__(self, method_call_obj, c, arg_name, arg_obj, caller_stack_entry):
        rdfl = self
        method_call_uri = method_call_obj.uri
        if isinstance(arg_obj, methods_chain.CallbackObj):
            #ipdb.set_trace()
            arg_obj.uri = f"<CallbackObj#{self.random_id}>"; self.random_id += 1
            rdfl.dump_triple__(arg_obj.uri, "rdf:type", "<CallbackObj>")
            rdfl.dump_triple__(arg_obj.uri, "<part-of>", caller_stack_entry.uri)
            rdfl.dump_triple__(method_call_uri, f"<method-call-arg{c}>", arg_obj.uri)
            rdfl.dump_triple__(method_call_uri, f"<method-call-arg{c}-name>", '"' + (arg_name if arg_name else '') + '"')
        elif isinstance(arg_obj, pd.DataFrame) or isinstance(arg_obj, pd.Series):
            arg_t_obj = obj_tracking.tracking_store.get_tracking_obj(arg_obj)
            if arg_t_obj.last_obj_state_uri is None:
                arg_t_obj.last_obj_state_uri = rdfl.dump_obj_state(arg_obj, arg_t_obj, caller_stack_entry)
            arg_uri = arg_t_obj.last_obj_state_uri
            #ipdb.set_trace()
            rdfl.dump_triple__(method_call_uri, f"<method-call-arg{c}>", arg_uri)
            rdfl.dump_triple__(method_call_uri, f"<method-call-arg{c}-name>", '"' + (arg_name if arg_name else '') + '"')
        else:
            pass
        
    def dump_method_call_in(self, method_call_obj, thread_id, obj, t_obj,
                            method_name, method_signature, method_bound_args,
                            caller_stack_entry):
        #ipdb.set_trace()
        rdfl = self
        
        thread_uri = rdfl.register_thread(thread_id)
        method_call_uri = method_call_obj.uri

        rdfl.dump_triple__(method_call_uri, "<method-thread>", thread_uri)
        global method_counter
        rdfl.dump_triple__(method_call_uri, "<method-counter>", method_counter); method_counter += 1
        rdfl.dump_triple__(method_call_uri, "<method-stack-depth>", call_stack.stack.size())
        rdfl.dump_triple__(method_call_uri, "<method-stack-trace>", '"' + call_stack.stack.to_methods_calls_string() + '"')

        c = 0
        for arg_name, arg_obj in method_bound_args.arguments.items():
            arg_kind = method_signature.parameters.get(arg_name).kind
            if arg_kind == inspect.Parameter.VAR_KEYWORD:
                for kwarg_name, kwarg_obj in arg_obj.items():
                    self.dump_method_call_arg__(method_call_obj, c, kwarg_name, kwarg_obj, caller_stack_entry)
                    c += 1
            elif arg_kind == inspect.Parameter.VAR_POSITIONAL:
                #ipdb.set_trace()
                for p_arg_obj in arg_obj:
                    self.dump_method_call_arg__(method_call_obj, c, None, p_arg_obj, caller_stack_entry)
                    c += 1
            else:
                self.dump_method_call_arg__(method_call_obj, c, arg_name, arg_obj, caller_stack_entry)
                c += 1
                
        return method_call_uri

rdflogger = None
def set_rdflogger__(o):
    global rdflogger
    rdflogger = o

