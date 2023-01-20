# pyjrdf to keep all rdf logging functionality
#
import ipdb
import sys, tempfile
import os.path
import pandas as pd
import uuid
import base64
import inspect

import pandas_flavor as pf

from . import obj_tracking
from . import pf_pandas

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
        self.known_chains = {}
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
        
    def register_chain(self, chain_path):
        # NB: chain should be object not path
        #chain_id = str(uuid.uuid4())
        chain_id = chain_path
        chain_uri = None
        if not chain_id in self.known_chains:
            chain_uri = self.known_chains[chain_id] = f"<Chain#{chain_id}>"
            self.dump_triple__(chain_uri, "rdf:type", "<Chain>")
            #ipdb.set_trace()
            self.dump_triple__(chain_uri, "rdf:label", f'"{chain_path}"' if chain_path else "rdf:nil")
        else:
            chain_uri = self.known_chains[chain_id]
        return chain_uri

    def register_thread(self, thread_id):
        if not thread_id in self.known_threads:            
            thread_uri = self.known_threads[thread_id] = f"<Thread#{thread_id}>"
            self.dump_triple__(thread_uri, "rdf:type", "<Thread>")
        else:
            thread_uri = self.known_threads[thread_id]
        return thread_uri
            
    def dump_obj_state(self, chain_path, obj, t_obj):
        obj_uri = self.register_obj__(obj, t_obj)
        obj_state_uri = f"<ObjState#{self.random_id}>"; self.random_id += 1
        chain_uri = self.register_chain(chain_path)

        df = obj
        #ipdb.set_trace()
        self.dump_triple__(obj_state_uri, "rdf:type", "<ObjState>")
        self.dump_triple__(obj_state_uri, "<obj>", obj_uri)
        self.dump_triple__(obj_state_uri, "<version>", f'"{t_obj.last_version_num}"')
        t_obj.last_version_num += 1
        self.dump_triple__(obj_state_uri, "<chain>", chain_uri)

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
            #df_head_html = df.head().to_html()
            #ipdb.set_trace()
            df_head_html = base64.b64encode(df.head(5).to_string(index = False, justify = 'start').encode('ascii')).decode('ascii')
            self.dump_triple__(obj_state_uri, "<df-head>", '"' + df_head_html + '"')
        #self.dump_triple__(obj_state_uri, "<df-columns>", f'"{df.columns}"')

    def dump_Series_obj_state(self, obj_state_uri, s):
        self.dump_triple__(obj_state_uri, "<df-shape>", f'"{s.shape}"')        

    def dump_method_call_arg__(self, method_call_uri, c, arg_name, arg_obj, chain_path):
        rdfl = self
        if isinstance(arg_obj, pf_pandas.CallbackObj):
            arg_obj.uri = f"<CallbackObj#{self.random_id}>"; self.random_id += 1
            rdfl.dump_triple__(arg_obj.uri, "rdf:type", "<CallbackObj>")
            arg_obj_chain_uri = rdfl.register_chain(arg_obj.chain_path)
            rdfl.dump_triple__(arg_obj.uri, "<chain>", arg_obj_chain_uri)
            rdfl.dump_triple__(method_call_uri, f"<method-call-arg{c}>", arg_obj.uri)
            rdfl.dump_triple__(method_call_uri, f"<method-call-arg{c}>", arg_obj.uri)
            rdfl.dump_triple__(method_call_uri, f"<method-call-arg{c}-name>", '"' + (arg_name if arg_name else '') + '"')
        elif isinstance(arg_obj, pd.DataFrame) or isinstance(arg_obj, pd.Series):
            arg_t_obj = obj_tracking.tracking_store.get_tracking_obj(arg_obj)
            if arg_t_obj.last_obj_state_uri is None:
                arg_t_obj.last_obj_state_uri = rdfl.dump_obj_state(chain_path, arg_obj, arg_t_obj)
            arg_uri = arg_t_obj.last_obj_state_uri
            #ipdb.set_trace()
            rdfl.dump_triple__(method_call_uri, f"<method-call-arg{c}>", arg_uri)
            rdfl.dump_triple__(method_call_uri, f"<method-call-arg{c}-name>", '"' + (arg_name if arg_name else '') + '"')
        else:
            pass
        
    def dump_method_call_in(self, chain_path, thread_id, obj, t_obj,
                            method_name, method_signature, method_bound_args,
                            stack_depth):
        #ipdb.set_trace()
        rdfl = self
        
        obj_chain_uri = rdfl.register_chain(chain_path)
        thread_uri = rdfl.register_thread(thread_id)
        method_call_id = rdfl.random_id; rdfl.random_id += 1
        method_call_uri = f"<MethodCall#{method_call_id}>"

        rdfl.dump_triple__(method_call_uri, "rdf:type", "<MethodCall>")
        rdfl.dump_triple__(method_call_uri, "rdf:label", '"' + method_name + '"')
        rdfl.dump_triple__(method_call_uri, "<method-thread>", thread_uri)
        global method_counter
        rdfl.dump_triple__(method_call_uri, "<method-counter>", method_counter); method_counter += 1
        rdfl.dump_triple__(method_call_uri, "<method-stack-depth>", stack_depth)
        rdfl.dump_triple__(method_call_uri, "<method-call-chain>", obj_chain_uri)

        c = 0
        for arg_name, arg_obj in method_bound_args.arguments.items():
            arg_kind = method_signature.parameters.get(arg_name).kind
            if arg_kind == inspect.Parameter.VAR_KEYWORD:
                for kwarg_name, kwarg_obj in arg_obj.items():
                    self.dump_method_call_arg__(method_call_uri, c, kwarg_name, kwarg_obj, chain_path)
            elif arg_kind == inspect.Parameter.VAR_POSITIONAL:
                #ipdb.set_trace()
                for p_arg_obj in arg_obj:
                    self.dump_method_call_arg__(method_call_uri, c, None, p_arg_obj, chain_path)                    
            else:
                self.dump_method_call_arg__(method_call_uri, c, arg_name, arg_obj, chain_path)

            c += 1

                
                
        return method_call_uri

rdflogger = None
def set_rdflogger__(o):
    global rdflogger
    rdflogger = o

