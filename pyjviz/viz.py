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
    chains = [r for r in g.query("select ?pp ?pl { ?pp rdf:type <Chain>; rdf:label ?pl }", base = rdflogging.base_uri)]

    out_fd = StringIO()
    
    print("""
    digraph G {
    rankdir = "TB"
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
        
        rq = """
        select ?obj ?obj_type ?obj_uuid { 
          [] rdf:type <ObjChainAssignment>; <obj> ?obj; <chain> ?chain.
          ?chain rdf:type <Chain>.
          ?obj rdf:type <Obj>; <obj-type> ?obj_type; <obj-uuid> ?obj_uuid.
        }
        """
        for obj, obj_type, obj_uuid in g.query(rq, base = rdflogging.base_uri, initBindings = {'chain': chain}):
            print(f"""
            node_{uri_to_dot_id(obj)} [
            color="#88000022"
            shape = rect
            label = <<table border="0" cellborder="0" cellspacing="0" cellpadding="4">
            <tr> <td> <b>{obj_type}</b><br/>{obj_uuid}</td> </tr>
            </table>>
            ];
            """, file = out_fd)
        
        if 0:
            rq = """
            select ?obj_state ?df_shape ?df_cols { 
            ?obj_state rdf:type <ObjState>; <obj> ?obj .
            ?obj_state <chain> ?orig_chain .
            optional { obj_state <chain-replacement> ?repl_chain }
            filter(if(bound(?repl_chain), ?repl_chain, ?orig_chain) = ?chain ) .
            ?obj_state <df-shape> ?df_shape; <df-columns> ?df_cols .
            }
            """
            
        rq = """
        select ?obj_state ?df_shape { 
          ?obj_state rdf:type <ObjState>; <obj> ?obj .
          ?obj_state <chain> ?chain .
          ?obj_state <df-shape> ?df_shape .
        }
        """

        for obj_state, df_shape in g.query(rq, base = rdflogging.base_uri, initBindings = {'chain': chain}):
            #cols = "\n".join(['<tr><td align="left"><FONT POINT-SIZE="8px">' + html.escape(x) + "</FONT></td></tr>" for x in df_cols.toPython().split(",")])
            cols = "TBC"
            print(f"""
            node_{uri_to_dot_id(obj_state)} [
                color="#88000022"
                shape = rect
                label = <<table border="0" cellborder="0" cellspacing="0" cellpadding="4">
                         <tr> <td> <b>{obj_state}</b><br/>{df_shape}</td> </tr>
                         <tr> <td align="left"><i>columns:</i><br align="left"/></td></tr>
                {cols}
                         </table>>
                ];

            """, file = out_fd)

        rq = """
        select ?method_call_obj ?method_name ?method_count ?chain { 
          ?method_call_obj rdf:type <MethodCall>; 
                           rdf:label ?method_name; 
                           <method-counter> ?method_count;
                           <method-call-chain> ?chain .
        }
        """
        for method_call_obj, method_name, method_count, chain in g.query(rq, base = rdflogging.base_uri, initBindings = {'chain': chain}):
            print(f"""
            node_{uri_to_dot_id(method_call_obj)} [ label = "{method_name}#{method_count}" ];
            """, file = out_fd)

        print(f"}}", file = out_fd)
            
            
    for chain, chain_label in chains:
        #ipdb.set_trace()
        rq = """
        select ?method_call_obj ?caller_obj ?ret_obj ?arg1_obj ?arg2_obj { 
          ?method_call_obj rdf:type <MethodCall>; <method-call-chain> ?chain;
                           <method-call-arg0> ?caller_obj;
                           <method-call-return> ?ret_obj .
          optional { ?method_call_obj <method-call-arg1> ?arg1_obj }
          optional { ?method_call_obj <method-call-arg2> ?arg2_obj }
        }
        """
        for method_call_obj, caller_obj, ret_obj, arg1_obj, arg2_obj in g.query(rq, base = rdflogging.base_uri, initBindings = {'chain': chain}):
            print(f"""
            node_{uri_to_dot_id(caller_obj)} -> node_{uri_to_dot_id(method_call_obj)};
            node_{uri_to_dot_id(method_call_obj)} -> node_{uri_to_dot_id(ret_obj)};
            """, file = out_fd)

            # NB: copy-paste is bad
            if arg1_obj:
                print(f"""
                node_{uri_to_dot_id(arg1_obj)} -> node_{uri_to_dot_id(method_call_obj)};
                """, file = out_fd)
            if arg2_obj:
                print(f"""
                node_{uri_to_dot_id(arg2_obj)} -> node_{uri_to_dot_id(method_call_obj)};
                """, file = out_fd)

    rq = """
    select ?obj ?obj_state { 
      [] rdf:type <ObjChainAssignment>; <obj> ?obj. 
      ?obj_state rdf:type <ObjState>; <obj> ?obj 
    }
    """
    #ipdb.set_trace()
    for obj, obj_state in g.query(rq, base = rdflogging.base_uri):
        print(f"node_{uri_to_dot_id(obj)} -> node_{uri_to_dot_id(obj_state)}", file = out_fd)
                
    if 0: # show transient objects
        rq = """
        select ?obj ?obj_type ?obj_uuid { ?obj rdf:type <Obj>; <obj-type> ?obj_type; <obj-uuid> ?obj_uuid }
        """
        for obj, obj_type, obj_uuid in g.query(rq, base = rdflogging.base_uri):
            print(f"""
            node_{uri_to_dot_id(obj)} [
            color="#88000022"
            shape = rect
            label = <<table border="0" cellborder="0" cellspacing="0" cellpadding="4">
            <tr> <td> <b>{obj_type}</b><br/>{obj_uuid}</td> </tr>
            </table>>
            ];
            """, file = out_fd)
                
        rq = """
        select ?obj ?obj_state { ?obj_state <obj> ?obj }
        """
        for obj, obj_state in g.query(rq, base = rdflogging.base_uri):
            print(f"""
            node_{uri_to_dot_id(obj)} -> node_{uri_to_dot_id(obj_state)};
            """, file = out_fd)
        
            
    print("}", file = out_fd)
    return out_fd.getvalue()

def render_rdflog(rdflog_ttl_fn, verbose = True):
    rdflogging.rdflogger.flush__()

    g = rdflib.Graph()
    g.parse(rdflog_ttl_fn)

    dot_code = dump_dot_code(g)
    gv_src = gv.Source(dot_code)
    gv_src.render(rdflog_ttl_fn + '.dot', format = 'png', engine = 'dot')

    if verbose:
        print(f"\nsaved diagram file {rdflog_ttl_fn + '.dot' + '.png'}")
