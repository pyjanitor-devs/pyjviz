# pyjrdf to keep all rdf logging functionality
#
import ipdb
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
        self.known_oscas = {} # osca - object state chain assignment
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
            self.dump_triple__(ret_uri, "obj-type", "<DataFrame>")
            self.dump_triple__(ret_uri, "obj-uuid", f'"{obj_uuid}"')

        return ret_uri
        
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
    
    def register_osca(self, obj, chain):
        k = (obj.uuid, obj.last_version_num, chain.uuid)
        if k in self.known_oscas:
            osca_uri = self.known_oscas[k]
        else:
            osca_uri = self.known_oscas[k] = f"<ObjStateChainAssignment#{self.random_id}>"; self.random_id += 1
            self.dump_triple__(osca_uri, "rdf:type", "<ObjStateChainAssignment>")
            obj_state_uri = self.dump_obj_state(obj)
            self.dump_triple__(osca_uri, "<obj-state>", obj_state_uri)
            chain_uri = self.register_chain(chain)
            self.dump_triple__(osca_uri, "<chain>", chain_uri)
            
        return osca_uri
    
    def dump_obj_state(self, obj):
        obj_uri = self.register_obj(obj)
        obj_state_uri = f"<ObjState#{self.random_id}>"; self.random_id += 1

        if obj is None:
            print("got you")
            ipdb.set_trace()
            
        if isinstance(obj.u_obj, pd.DataFrame):
            df = obj.u_obj
            self.dump_triple__(obj_state_uri, "rdf:type", "<ObjState>")
            self.dump_triple__(obj_state_uri, "<obj>", obj_uri)
            self.dump_triple__(obj_state_uri, "<version>", f'"{obj.last_version_num}"')
            self.dump_triple__(obj_state_uri, "<df-shape>", f'"{df.shape}"')
            self.dump_triple__(obj_state_uri, "<df-columns>", f'"{df.columns}"')
        return obj_state_uri
