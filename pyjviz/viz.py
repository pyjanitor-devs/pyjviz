# pyjviz module implements basic visualisation of pyjviz rdf log
# there is no dependency of this code to other part of pyjanitor
#
import ipdb
import os.path
import collections
import html
import sys, base64

import rdflib
from io import StringIO

import graphviz as gv

from . import rdflogging

def uri_to_dot_id(uri):
    return str(hash(uri)).replace("-", "d")

def dump_dot_code(g, vertical, show_objects):
    #ipdb.set_trace()
    chains = [r for r in g.query("select ?pp ?pl { ?pp rdf:type <Chain>; rdf:label ?pl }", base = rdflogging.base_uri)]

    out_fd = StringIO()

    rankdir = "TB" if vertical else "LR"
    
    print("""
    digraph G {
    rankdir = "{rankdir}"
    fontname="Helvetica,Arial,sans-serif"
    node [ 
      style=filled
      shape=rect
      pencolor="#00000044" // frames color
      fontname="Helvetica,Arial,sans-serif"
      shape=plaintext
    ]
    edge [fontname="Helvetica,Arial,sans-serif"]    
    """.replace("{rankdir}", rankdir), file = out_fd)

    #ipdb.set_trace()    
    for chain, chain_label in chains:
        print(f"""
        subgraph cluster_{uri_to_dot_id(chain)} {{
          label = "{chain_label}";
        """, file = out_fd)
            
        rq = """
        select ?obj_state ?version ?obj_type ?obj_uuid ?df_shape ?df_head { 
          ?obj_state rdf:type <ObjState>; <obj> ?obj.
          ?obj rdf:type <Obj>; <obj-type> ?obj_type; <obj-uuid> ?obj_uuid.
          ?obj_state <chain> ?chain; <version> ?version .
          ?obj_state <df-shape> ?df_shape .
          optional {?obj_state <df-head> ?df_head} .
        }
        """

        for obj_state, version, obj_type, obj_uudi, df_shape, df_head in g.query(rq, base = rdflogging.base_uri, initBindings = {'chain': chain}):
            #cols = "\n".join(['<tr><td align="left"><FONT POINT-SIZE="8px">' + html.escape(x) + "</FONT></td></tr>" for x in df_cols.toPython().split(",")])
            df_head = base64.b64decode(df_head.encode('ascii')).decode('ascii') if df_head else ""
            df_head = df_head.replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>")
            print(f"""
            node_{uri_to_dot_id(obj_state)} [
                color="#88000022"
                shape = rect
                label = <<table border="0" cellborder="0" cellspacing="0" cellpadding="4">
                         <tr> <td> <b>{obj_state}</b><br/>{obj_type} {version} {obj_uudi}<br/>{df_shape}</td> </tr>
            <tr><td align="left">{df_head}</td></tr>
                         </table>>
                ];

            """, file = out_fd)

        rq = """
        select ?method_call_obj ?method_name ?method_count ?method_stack_depth ?chain { 
          ?method_call_obj rdf:type <MethodCall>; 
                           rdf:label ?method_name; 
                           <method-counter> ?method_count;
                           <method-stack-depth> ?method_stack_depth;
                           <method-call-chain> ?chain .
        }
        """
        for method_call_obj, method_name, method_count, method_stack_depth, chain in g.query(rq, base = rdflogging.base_uri, initBindings = {'chain': chain}):
            print(f"""
            node_{uri_to_dot_id(method_call_obj)} [ label = "{method_name}#{method_count}({method_stack_depth})" ];
            """, file = out_fd)

        rq = """
        select ?callback_obj ?chain {
          ?callback_obj rdf:type <CallbackObj>; <chain> ?chain.
        }
        """
        for callback_obj, chain in g.query(rq, base = rdflogging.base_uri, initBindings = {'chain': chain}):
            print(f"""
            node_{uri_to_dot_id(callback_obj)} [ label = "CallbackObj" ];
            """, file = out_fd)

        print(f"}}", file = out_fd)
            
    for chain, chain_label in chains:
        #ipdb.set_trace()
        rq = """
        select ?method_call_obj ?caller_obj ?ret_obj ?arg1_obj ?arg2_obj ?arg3_obj { 
          ?method_call_obj rdf:type <MethodCall>; <method-call-chain> ?chain;
                           <method-call-arg0> ?caller_obj;
                           <method-call-return> ?ret_obj .
          optional { ?method_call_obj <method-call-arg1> ?arg1_obj }
          optional { ?method_call_obj <method-call-arg2> ?arg2_obj }
          optional { ?method_call_obj <method-call-arg3> ?arg3_obj }
        }
        """
        for method_call_obj, caller_obj, ret_obj, arg1_obj, arg2_obj, arg3_obj in g.query(rq, base = rdflogging.base_uri, initBindings = {'chain': chain}):
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
            if arg3_obj:
                print(f"""
                node_{uri_to_dot_id(arg3_obj)} -> node_{uri_to_dot_id(method_call_obj)};
                """, file = out_fd)
                
    if show_objects: # show transient objects
        rq = """
        select ?obj ?obj_type ?obj_uuid ?obj_pyid { 
          ?obj rdf:type <Obj>; <obj-type> ?obj_type; <obj-uuid> ?obj_uuid; <obj-pyid> ?obj_pyid
        }
        """
        for obj, obj_type, obj_uuid, obj_pyid in g.query(rq, base = rdflogging.base_uri):
            print(f"""
            node_{uri_to_dot_id(obj)} [
            color="#88000022"
            shape = rect
            label = <<table border="0" cellborder="0" cellspacing="0" cellpadding="4">
            <tr> <td> <b>{obj_type}</b><br/>{obj_uuid}<br/>{obj_pyid}</td> </tr>
            </table>>
            ];
            """, file = out_fd)

        rq = """
        select ?obj ?obj_state { ?obj_state rdf:type <ObjState>; <obj> ?obj }
        """
        for obj, obj_state in g.query(rq, base = rdflogging.base_uri):
            print(f"""
            node_{uri_to_dot_id(obj)} -> node_{uri_to_dot_id(obj_state)} [label="obj_state"];
            """, file = out_fd)
            
    if 1:
        rq = """
        select ?obj ?obj_state { ?obj_state <ret-val> ?obj }
        """
        for obj, obj_state in g.query(rq, base = rdflogging.base_uri):
            print(f"""
            node_{uri_to_dot_id(obj)} -> node_{uri_to_dot_id(obj_state)} [label="ret_val"];
            """, file = out_fd)

        rq = """
        select ?from_obj ?to_obj ?pred { 
          ?from_obj <df-projection>|<to_datetime> ?to_obj;
                    ?pred ?to_obj 
        }
        """
        for from_obj, to_obj, pred in g.query(rq, base = rdflogging.base_uri):
            pred_s = pred.toPython().split('/')[-1]
            print(f"""
            node_{uri_to_dot_id(to_obj)} -> node_{uri_to_dot_id(from_obj)} [label="{pred_s}"];
            """, file = out_fd)
            
    print("}", file = out_fd)
    return out_fd.getvalue()

def render_rdflog(rdflog_ttl_fn, verbose = True, vertical = True, show_objects = False):
    rdflogging.rdflogger.flush__()

    g = rdflib.Graph()
    g.parse(rdflog_ttl_fn)

    #ipdb.set_trace()
    if len(g) == 0:
        print(f"render_rdflog: empty graph found in {rdflog_ttl_fn}, no viz output will be produced")
        
    dot_code = dump_dot_code(g, vertical, show_objects)
    gv_src = gv.Source(dot_code)
    gv_src.render(rdflog_ttl_fn + '.dot', format = 'png', engine = 'dot')

    if verbose:
        print(f"\nsaved diagram file {rdflog_ttl_fn + '.dot' + '.png'}")
