import ipdb
import rdflib, sys
from pyjviz import base_uri

if __name__ == "__main__":
    rdflog_ttl_fn = sys.argv[1]
    g = rdflib.Graph()
    g.parse(rdflog_ttl_fn)
    
    rq = """
    #base <https://github.com/pyjanitor-devs/pyjviz/rdflog.shacl.ttl/>
    #select ?s { ?s rdf:type <https://github.com/pyjanitor-devs/pyjviz/Chain> }
    select ?s { ?s rdf:type <Chain> }
    #select ?s ?p ?o { ?s ?p ?o }
    """

    for l in g.query(rq, base = base_uri):
        print(l)
        
