# pyjrdf to keep all rdf logging functionality
#
import ipdb
import sys
import os.path
import pandas as pd
import uuid

from . import obj_tracking

base_uri = 'https://github.com/pyjanitor-devs/pyjviz/rdflog.shacl.ttl#'
method_counter = 0

def get_rdflog_filename(argv0):
    rdflog_fn = os.path.basename(argv0).replace(".py", ".ttl")
    return os.path.expanduser(os.path.join("~/.pyjviz/rdflog", rdflog_fn))

def open_pyjrdf_output__(out_fn):
    out_dir = os.path.dirname(out_fn)    
    if out_dir != "" and not os.path.exists(out_dir):
        print("setup_pyjrdf_output:", out_dir)
        os.makedirs(out_dir)
    out_fd = open(out_fn, "wt")

    # rdf prefixes used by PYJRDFLogger
    print(f"@base <{base_uri}> .", file = out_fd)
    print("@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .", file = out_fd)
    print("@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .", file = out_fd)
    
    return out_fd

rdflogger = None

def get_obj_type(o):
    if isinstance(o, pd.DataFrame):
        ret = "DataFrame"
    else:
        raise Exception(f"unknown type of o: {str(type(o))}")

    return ret
    
class RDFLogger:
    @staticmethod
    def init(out_filename): 
        global rdflogger
        rdflogger = RDFLogger(out_filename)
    
    def __init__(self, out_filename):        
        self.out_fd = open_pyjrdf_output__(out_filename)
        self.known_threads = {}
        self.known_chains = {}
        self.known_objs = {}
        self.random_id = 0 # should be better way

    def flush__(self):
        self.out_fd.flush()
        
    def dump_triple__(self, subj, pred, obj):
        print(subj, pred, obj, ".", file = self.out_fd)

    def register_obj(self, obj, t_obj):
        obj_uuid = str(t_obj.uuid)
        if obj_uuid in self.known_objs:
            ret_uri = self.known_objs[obj_uuid]
        else:
            ret_uri = self.known_objs[obj_uuid] = f"<Obj#{obj_uuid}>"
            self.dump_triple__(ret_uri, "rdf:type", "<Obj>")
            self.dump_triple__(ret_uri, "<obj-type>", f'"{get_obj_type(obj)}"')
            self.dump_triple__(ret_uri, "<obj-uuid>", f'"{obj_uuid}"')

        return ret_uri
        
    def register_chain(self, chain_path):
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
        obj_uri = self.register_obj(obj, t_obj)
        obj_state_uri = f"<ObjState#{self.random_id}>"; self.random_id += 1
        chain_uri = self.register_chain(chain_path)

        if 1:
            df = obj
            #ipdb.set_trace()
            self.dump_triple__(obj_state_uri, "rdf:type", "<ObjState>")
            self.dump_triple__(obj_state_uri, "<obj>", obj_uri)
            self.dump_triple__(obj_state_uri, "<version>", f'"{t_obj.last_version_num}"')
            self.dump_triple__(obj_state_uri, "<chain>", chain_uri)

            if isinstance(obj, pd.DataFrame):
                self.dump_DataFrame_obj_state(obj_state_uri, obj)
            else:
                pass

        return obj_state_uri

    def dump_DataFrame_obj_state(self, obj_state_uri, df):
        self.dump_triple__(obj_state_uri, "<df-shape>", f'"{df.shape}"')
        #self.dump_triple__(obj_state_uri, "<df-columns>", f'"{df.columns}"')
        
    
    def dump_method_call_in(self, chain_path, thread_id, obj, t_obj, method_name, method_args, method_kwargs):
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
        rdfl.dump_triple__(method_call_uri, "<method-call-chain>", obj_chain_uri)

        if t_obj.last_obj_state_uri is None:
            t_obj.last_obj_state_uri = rdfl.dump_obj_state(chain_path, obj, t_obj)
        rdfl.dump_triple__(method_call_uri, "<method-call-arg0>", t_obj.last_obj_state_uri)

        c = 1
        for arg_obj in method_args:
            if isinstance(arg_obj, pd.DataFrame):
                arg_t_obj = obj_tracking.tracking_store.get_tracking_obj(arg_obj)
                if arg_t_obj.last_obj_state_uri is None:
                    arg_t_obj.last_obj_state_uri = rdfl.dump_obj_state(chain_path, arg_obj, arg_t_obj)
                rdfl.dump_triple__(method_call_uri, f"<method-call-arg{c}>", arg_t_obj.last_obj_state_uri)
            c += 1

        return method_call_uri
    
