# pyjrdf to keep all rdf logging functionality
#
import ipdb
import sys
import os.path
import pandas as pd
import uuid

from . import uw

base_uri = 'https://github.com/pyjanitor-devs/pyjviz/rdflog.shacl.ttl/'
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

    def register_obj(self, tracking_obj):
        obj_uuid = str(tracking_obj.uuid)
        if obj_uuid in self.known_objs:
            ret_uri = self.known_objs[obj_uuid]
        else:
            ret_uri = self.known_objs[obj_uuid] = f"<Obj#{obj_uuid}>"
            self.dump_triple__(ret_uri, "rdf:type", "<Obj>")
            self.dump_triple__(ret_uri, "<obj-type>", "<DataFrame>")
            self.dump_triple__(ret_uri, "<obj-uuid>", f'"{obj_uuid}"')

        return ret_uri
        
    def register_chain(self, chain):
        chain_id = id(chain)
        chain_uri = None
        if not chain_id in self.known_chains:
            chain_uri = self.known_chains[chain_id] = f"<Chain#{chain_id}>"
            self.dump_triple__(chain_uri, "rdf:type", "<Chain>")
            #ipdb.set_trace()
            self.dump_triple__(chain_uri, "rdf:label", f'"{chain.chain_name}"' if chain else "rdf:nil")
            if chain and chain.parent_chain:
                parent_chain_uri = self.register_chain(chain.parent_chain)
                self.dump_triple__(chain_uri, "<parent-chain>", parent_chain_uri)
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
            
    def dump_obj_state(self, obj):
        obj_uri = self.register_obj(obj)
        obj_state_uri = f"<ObjState#{self.random_id}>"; self.random_id += 1
        chain_uri = self.register_chain(obj.obj_chain)
        
        if isinstance(obj.u_obj, pd.DataFrame):
            df = obj.u_obj
            #ipdb.set_trace()
            self.dump_triple__(obj_state_uri, "rdf:type", "<ObjState>")
            self.dump_triple__(obj_state_uri, "<obj>", obj_uri)
            self.dump_triple__(obj_state_uri, "<version>", f'"{obj.last_version_num}"')
            self.dump_triple__(obj_state_uri, "<chain>", chain_uri)
            self.dump_triple__(obj_state_uri, "<df-shape>", f'"{df.shape}"')
            #self.dump_triple__(obj_state_uri, "<df-columns>", f'"{df.columns}"')
        return obj_state_uri

    def dump_method_call_in(self, thread_id, obj, method_name, method_args, method_kwargs):
        rdfl = self
        
        obj_chain_uri = rdfl.register_chain(obj.obj_chain)
        thread_uri = rdfl.register_thread(thread_id)
        method_call_id = rdfl.random_id; rdfl.random_id += 1
        method_call_uri = f"<MethodCall#{method_call_id}>"

        rdfl.dump_triple__(method_call_uri, "rdf:type", "<MethodCall>")
        rdfl.dump_triple__(method_call_uri, "rdf:label", '"' + method_name + '"')
        rdfl.dump_triple__(method_call_uri, "<method-thread>", thread_uri)
        global method_counter
        rdfl.dump_triple__(method_call_uri, "<method-counter>", method_counter); method_counter += 1
        rdfl.dump_triple__(method_call_uri, "<method-call-chain>", obj_chain_uri)

        if obj.last_obj_state_uri is None:
            obj.last_obj_state_uri = rdfl.dump_obj_state(obj)
        rdfl.dump_triple__(method_call_uri, "<method-call-arg0>", obj.last_obj_state_uri)

        c = 1
        for arg_obj in method_args:
            if isinstance(arg_obj, uw.UWObject):
                if arg_obj.last_obj_state_uri is None:
                    arg_obj.last_obj_state_uri = rdfl.dump_obj_state(arg_obj)
                rdfl.dump_triple__(method_call_uri, f"<method-call-arg{c}>", arg_obj.last_obj_state_uri)
            c += 1

        return method_call_uri
    
