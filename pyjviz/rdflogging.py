# pyjrdf to keep all rdf logging functionality
#
import sys
import os.path
import pandas as pd

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
    print("@base <https://github.com/pyjanitor-devs/pyjviz/rdflog.shacl.ttl#> .", file = out_fd)
    print("@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .", file = out_fd)
    print("@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .", file = out_fd)
    print("<ObjOnChain> rdf:type rdfs:Class .", file = out_fd)
    
    return out_fd

rdflogger = None

class RDFLogger:
    @staticmethod
    def init(out_filename): 
        global rdflogger
        rdflogger = RDFLogger(out_filename)
    
    def __init__(self, out_filename):        
        self.out_fd = open_pyjrdf_output__(out_filename)
        self.known_objs = {}
        self.known_chains = {}
        self.known_obj_chain_pairs = {}
        self.known_threads = {}
        self.random_id = 0 # should be better way

    def flush__(self):
        self.out_fd.flush()
        
    def dump_triple__(self, subj, pred, obj):
        print(subj, pred, obj, ".", file = self.out_fd)

    def register_obj(self, obj):
        obj_id = id(obj)
        obj_uri = None
        if not obj_id in self.known_objs:
            obj_uri = self.known_objs[obj_id] = f"<Obj#{obj_id}>"
            self.dump_triple__(obj_uri, "rdf:type", "<DataFrame>")
            self.dump_triple__(obj_uri, "<df-shape>", f'"{obj.shape}"')
            self.dump_triple__(obj_uri, "<df-columns>", '"' + f"{','.join(obj.columns)}" + '"')
        else:
            obj_uri = self.known_objs[obj_id]
        return obj_uri

    def register_chain(self, chain):
        chain_id = id(chain)
        chain_uri = None
        if not chain_id in self.known_chains:
            chain_uri = self.known_chains[chain_id] = f"<Chain#{chain_id}>"
            self.dump_triple__(chain_uri, "rdf:type", "<Chain>")
            self.dump_triple__(chain_uri, "rdf:label", f'"{chain.chain_name}"')
            if chain.parent_chain:
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

    def register_pinned_obj_on_chain(self, obj, chain):
        obj_id = id(obj)
        chain_id = id(chain)
        k = (obj_id, chain_id)
        if not k in self.known_obj_chain_pairs:
            obj_uri = self.register_obj(obj)
            chain_uri = self.register_chain(chain)
            pinned_obj_on_chain_uri = self.known_obj_chain_pairs[k] = f"<ObjOnChain#{self.random_id}>"; self.random_id += 1
            self.dump_triple__(pinned_obj_on_chain_uri, "rdf:type", "<ObjOnChain>")
            self.dump_triple__(pinned_obj_on_chain_uri, "<pinned_obj>", obj_uri)
            self.dump_triple__(pinned_obj_on_chain_uri, "<chain>", chain_uri)
        else:
            pinned_obj_on_chain_uri = self.known_obj_chain_pairs[k]
        return pinned_obj_on_chain_uri
            
