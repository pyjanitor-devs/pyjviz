import ipdb
import os, os.path
import tempfile
import io
import rdflib

class FSTripleOutput:
    def __init__(self, base_uri, out_fd):
        self.base_uri = base_uri
        self.out_fd = out_fd
        
    def dump_prefixes__(self):
        print(f"@base <{self.base_uri}> .", file = self.out_fd)
        print("@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .", file = self.out_fd)
        print("@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .", file = self.out_fd)

    def dump_triple(self, subj, pred, obj):
        print(f"{subj} {pred} {obj} .", file = self.out_fd)

    def flush(self):
        self.out_fd.flush()

class FSTripleOutputOneShot(FSTripleOutput):
    def __init__(self, base_uri, output_dir, output_filename):
        self.output_fn = None
        if output_dir is None:
            out_fd = io.StringIO()
        else:
            #ipdb.set_trace()
            output_dir = os.path.expanduser(output_dir)            
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            if output_filename:
                self.output_fn = os.path.join(output_dir, output_filename)
                out_fd = open(self.output_fn, "w+")

        super().__init__(base_uri, out_fd)
        self.dump_prefixes__()
        
    def get_graph(self):
        g = rdflib.Graph()
        self.out_fd.seek(0)
        g.parse(self.out_fd)
        return g
        
            
