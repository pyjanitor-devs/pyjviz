# pyjviz module implements basic visualisation of pyjviz rdf log
# there is no dependency of this code to other part of pyjanitor
#
import ipdb
import os.path
import collections
import html
import sys

import rdflib
from io import StringIO

import graphviz as gv

from . import rdflogging

def uri_to_dot_id(uri):
    return str(hash(uri)).replace("-", "d")

def dump_dot_code(g):
    #ipdb.set_trace()
    chains = [r for r in g.query("select ?pp ?pl { ?pp rdf:type <pyjviz:Chain>; rdf:label ?pl }")]

    out_fd = StringIO()
    
    print("""
    digraph G {
    rankdir = "LR"
    fontname="Helvetica,Arial,sans-serif"
    node [ 
      style=filled
      shape=rect
      pencolor="#00000044" // frames color
      fontname="Helvetica,Arial,sans-serif"
      shape=plaintext
    ]
    edge [fontname="Helvetica,Arial,sans-serif"]    
    """, file = out_fd)
    #print('rankdir = "TB"', file = out_fd)

    #ipdb.set_trace()
    for chain, chain_label in chains:
        print(f"""
        subgraph cluster_{uri_to_dot_id(chain)} {{
          label = "{chain_label}";
        """, file = out_fd)

        if 0:
            test_rq = """
            select ?pinned_obj ?obj ?orig_chain ?chain_decision ?chain { 
            ?pinned_obj rdf:type <pyjviz:ObjOnChain>; <pyjviz:pinned_obj> ?obj .
            ?pinned_obj <pyjviz:chain> ?orig_chain .
            optional { ?pinned_obj <pyjviz:chain-replacement> ?repl_chain }
            bind(if(bound(?repl_chain), ?repl_chain, ?orig_chain) as ?chain_decision)
            filter( ?chain_decision = ?chain ) .
            }
            """
            for l in g.query(test_rq, initBindings = {'chain': chain}):
                print(l)        
        
        rq = """
        select ?pinned_obj ?obj ?df_shape ?df_cols { 
          ?pinned_obj rdf:type <pyjviz:ObjOnChain>; <pyjviz:pinned_obj> ?obj .
          ?pinned_obj <pyjviz:chain> ?orig_chain .
          optional { ?pinned_obj <pyjviz:chain-replacement> ?repl_chain }
          filter(if(bound(?repl_chain), ?repl_chain, ?orig_chain) = ?chain ) .
          ?obj <pyjviz:df-shape> ?df_shape; <pyjviz:df-columns> ?df_cols .
        }
        """
        for pinned_obj, obj, df_shape, df_cols in g.query(rq, initBindings = {'chain': chain}):
            cols = "\n".join(['<tr><td align="left"><FONT POINT-SIZE="8px">' + html.escape(x) + "</FONT></td></tr>" for x in df_cols.toPython().split(",")])
            print(f"""
            node_{uri_to_dot_id(pinned_obj)} [
                color="#88000022"
                shape = rect
                label = <<table border="0" cellborder="0" cellspacing="0" cellpadding="4">
                         <tr> <td> <b>{obj}</b><br/>{df_shape}</td> </tr>
                         <tr> <td align="left"><i>columns:</i><br align="left"/></td></tr>
                {cols}
                         </table>>
                ];

            """, file = out_fd)

        rq = """
        select ?method_call_obj ?method_name ?method_count ?chain { 
          ?method_call_obj rdf:type <pyjviz:MethodCall>; 
                           rdf:label ?method_name; 
                           <pyjviz:method-counter> ?method_count;
                           <pyjviz:method-call-chain> ?chain .
        }
        """
        for method_call_obj, method_name, method_count, chain in g.query(rq, initBindings = {'chain': chain}):
            print(f"""
            node_{uri_to_dot_id(method_call_obj)} [ label = "{method_name}#{method_count}" ];
            """, file = out_fd)

        print(f"}}", file = out_fd)
            
            
    for chain, chain_label in chains:
        #ipdb.set_trace()
        rq = """
        select ?method_call_obj ?caller_obj ?ret_obj ?arg1_obj { 
          ?method_call_obj rdf:type <pyjviz:MethodCall>; <pyjviz:method-call-chain> ?chain;
                           <pyjviz:method-call-arg0> ?caller_obj;
                           <pyjviz:method-call-return> ?ret_obj .
          optional { ?method_call_obj <pyjviz:method-call-arg1> ?arg1_obj }
        }
        """
        for method_call_obj, caller_obj, ret_obj, arg1_obj in g.query(rq, initBindings = {'chain': chain}):
            print(f"""
            node_{uri_to_dot_id(caller_obj)} -> node_{uri_to_dot_id(method_call_obj)};
            node_{uri_to_dot_id(method_call_obj)} -> node_{uri_to_dot_id(ret_obj)};
            """, file = out_fd)
            if arg1_obj:
                print(f"""
                node_{uri_to_dot_id(arg1_obj)} -> node_{uri_to_dot_id(method_call_obj)};
                """, file = out_fd)
                

            
    print("}", file = out_fd)
    return out_fd.getvalue()

def get_rdflog_filename(argv0):
    rdflog_fn = os.path.basename(argv0).replace(".py", ".ttl")
    return os.path.join("rdflog", rdflog_fn)

def render_rdflog(rdflog_ttl_fn, verbose = True):
    rdflogging.rdflogger.flush__()
    g = rdflib.Graph()
    g.parse(rdflog_ttl_fn)

    dot_code = dump_dot_code(g)
    gv_src = gv.Source(dot_code)
    gv_src.render(rdflog_ttl_fn + '.dot', format = 'png', engine = 'dot')

    if verbose:
        print(f"\nsaved diagram file {rdflog_ttl_fn + '.dot' + '.png'}")
