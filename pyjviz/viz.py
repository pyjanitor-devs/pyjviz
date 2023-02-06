# pyjviz module implements basic visualisation of pyjviz rdf log
# there is no dependency of this code to other part of pyjanitor
#
import ipdb
import os.path, tempfile
import collections
import html
import sys, base64
import pandas as pd
import textwrap

import rdflib
from io import StringIO

import graphviz

from . import fstriplestore
from . import nb_utils

def uri_to_dot_id(uri):
    return str(hash(uri)).replace("-", "d")

def dump_subgraph(g, cc_uri, out_fd):
    subgraphs = [r for r in g.query("select ?pp ?pl { ?pp rdf:type <CodeBlock>; rdf:label ?pl; <part-of> ?sg }", base = fstriplestore.base_uri, initBindings = {'sg': cc_uri})]
    for subgraph, subgraph_label in subgraphs:
        if subgraph_label != rdflib.RDF.nil:
            print(f"""
            subgraph cluster_{uri_to_dot_id(subgraph)} {{
            label = "{subgraph_label}";
            """, file = out_fd)

        dump_subgraph(g, subgraph, out_fd)
        
        rq = """
        select ?obj_state ?version ?obj_type ?obj_uuid ?df_shape ?df_head ?df_im { 
          ?obj_state rdf:type <ObjState>; <obj> ?obj.
          ?obj rdf:type <Obj>; <obj-type> ?obj_type; <obj-uuid> ?obj_uuid.
          ?obj_state <part-of>+ ?sg; <version> ?version .
          ?obj_state <df-shape> ?df_shape .
          optional {?obj_state <df-head> ?df_head}
          optional {?obj_state <df-plot> ?df_im}
        }
        """
        for obj_state, version, obj_type, obj_uudi, df_shape, df_head, df_im in g.query(rq, base = fstriplestore.base_uri, initBindings = {'sg': subgraph}):
            with tempfile.NamedTemporaryFile(dir = './pyjviz-test-output/tmp', suffix = '.html', delete = False) as temp_fp:
                if df_head:
                    node_bgcolor = "#88000022"
                    popup_size = (800, 200)
                    temp_fp.write(df_head.toPython().replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", "'").replace("&#10;", "\n").encode('ascii'))
                elif df_im:
                    node_bgcolor = "#44056022"
                    popup_size = (900, 500)
                    temp_fp.write(("<img src='data:image/png;base64," + df_im.toPython() + "'></img>").encode('ascii'))
                else:
                    node_bgcolor = "#88000022"
                    popup_size = (800, 200)
                    temp_fp.write('NONE'.encode('ascii'))
            
            #ipdb.set_trace()
            print(f"""
            node_{uri_to_dot_id(obj_state)} [
                color="{node_bgcolor}"
                shape = rect
                label = <<table border="0" cellborder="0" cellspacing="0" cellpadding="4">
                         <tr> <td> <b>{obj_state.split('/')[-1]}</b><br/>{obj_type} {df_shape} {version}</td> </tr>
                         </table>>
                href="javascript: 
                {{ window.open('tmp/{os.path.basename(temp_fp.name)}', '_blank', 'width={popup_size[0]},height={popup_size[1]}'); }}
                "
                ];

            """, file = out_fd)

        rq = """
        select ?method_call_obj ?method_name ?method_display ?method_count ?method_stack_depth ?method_stack_trace { 
          ?method_call_obj rdf:type <MethodCall>; 
                           rdf:label ?method_name; 
                           <method-counter> ?method_count; <method-display> ?method_display;
                           <method-stack-depth> ?method_stack_depth;
                           <method-stack-trace> ?method_stack_trace;
                           <part-of>+ ?sg .
        }
        """
        for method_call_obj, method_name, method_display, method_count, method_stack_depth, method_stack_trace in g.query(rq, base = fstriplestore.base_uri, initBindings = {'sg': subgraph}):
            method_display = base64.b64decode(method_display.toPython().encode('ascii')).decode('ascii')
            #method_display = "<br/>".join(textwrap.wrap(method_display, width = 40))
            print(f"""
            node_{uri_to_dot_id(method_call_obj)} [ label = <<TABLE border="0" align="left"><TR><TD>{method_display}</TD></TR></TABLE>> ];
            """, file = out_fd)

        rq = """
        select ?nested_call ?sg {
          ?nested_call rdf:type <NestedCall>; <part-of>+ ?sg.
        }
        """
        for nested_call, sg in g.query(rq, base = fstriplestore.base_uri, initBindings = {'sg': subgraph}):
            print(f"""
            node_{uri_to_dot_id(nested_call)} [ label = "NestedCall" ];
            """, file = out_fd)

        if subgraph_label != rdflib.RDF.nil:
            print(f"}}", file = out_fd)
    

def dump_dot_code(g, vertical, show_objects):
    #ipdb.set_trace()

    out_fd = StringIO()

    rankdir = "TB" if vertical else "LR"
    
    print("""
    digraph G {
    #splines=false;
    #ratio=fill;
    #size="800px,600px";
    #center=true;
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


    dump_subgraph(g, rdflib.RDF.nil, out_fd)
    
    #for subgraph, subgraph_label in subgraphs:
    if 1:
        #ipdb.set_trace()
        rq = """
        select ?method_call_obj ?arg0_obj ?arg0_name ?ret_obj ?arg1_name ?arg1_obj ?arg2_name ?arg2_obj ?arg3_name ?arg3_obj { 
          ?method_call_obj rdf:type <MethodCall>;
                           <method-call-arg0> ?arg0_obj; <method-call-arg0-name> ?arg0_name;
                           <method-call-return> ?ret_obj .
          optional { ?arg1_obj rdf:type <ObjState>. ?method_call_obj <method-call-arg1> ?arg1_obj; <method-call-arg1-name> ?arg1_name }
          optional { ?arg2_obj rdf:type <ObjState>. ?method_call_obj <method-call-arg2> ?arg2_obj; <method-call-arg2-name> ?arg2_name }
          optional { ?arg3_obj rdf:type <ObjState>. ?method_call_obj <method-call-arg3> ?arg3_obj; <method-call-arg3-name> ?arg3_name }
        }
        """
        for method_call_obj, arg0_obj, arg0_name, ret_obj, arg1_name, arg1_obj, arg2_name, arg2_obj, arg3_name, arg3_obj in g.query(rq, base = fstriplestore.base_uri):
            print(f"""
            node_{uri_to_dot_id(arg0_obj)} -> node_{uri_to_dot_id(method_call_obj)} [label="{arg0_name}"];
            node_{uri_to_dot_id(method_call_obj)} -> node_{uri_to_dot_id(ret_obj)};
            """, file = out_fd)

            # NB: copy-paste is bad
            if arg1_obj:
                print(f"""
                node_{uri_to_dot_id(arg1_obj)} -> node_{uri_to_dot_id(method_call_obj)} [label="{arg1_name}"];
                """, file = out_fd)
            if arg2_obj:
                print(f"""
                node_{uri_to_dot_id(arg2_obj)} -> node_{uri_to_dot_id(method_call_obj)} [label="{arg2_name}"];
                """, file = out_fd)
            if arg3_obj:
                print(f"""
                node_{uri_to_dot_id(arg3_obj)} -> node_{uri_to_dot_id(method_call_obj)} [label="{arg3_name}"];
                """, file = out_fd)
                
    if show_objects: # show transient objects
        rq = """
        select ?obj ?obj_type ?obj_uuid ?obj_pyid { 
          ?obj rdf:type <Obj>; <obj-type> ?obj_type; <obj-uuid> ?obj_uuid; <obj-pyid> ?obj_pyid
        }
        """
        for obj, obj_type, obj_uuid, obj_pyid in g.query(rq, base = fstriplestore.base_uri):
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
        for obj, obj_state in g.query(rq, base = fstriplestore.base_uri):
            print(f"""
            node_{uri_to_dot_id(obj)} -> node_{uri_to_dot_id(obj_state)} [label="obj_state"];
            """, file = out_fd)
            
    if 1:
        # taking care of NestedCall arrows
        rq = """
        select ?method_call ?arg0 ?nested_call1_ret_obj_state ?arg1_name ?nested_call1 { 
          ?nested_call1_ret_obj_state rdf:type <ObjState>.
          ?nested_call1 rdf:type <NestedCall>; <ret-val> ?nested_call1_ret_obj_state.
          ?method_call rdf:type <MethodCall>; 
                       <method-call-arg0> ?arg0;
                       <method-call-arg1> ?nested_call1;
                       <method-call-arg1-name> ?arg1_name.
        }
        """
        for method_call, arg0, nested_call1_ret_obj_state, arg1_name, nested_call1 in g.query(rq, base = fstriplestore.base_uri):
            print(f"""
            node_{uri_to_dot_id(nested_call1_ret_obj_state)} -> node_{uri_to_dot_id(method_call)} [label="{arg1_name.toPython()}"];
            node_{uri_to_dot_id(nested_call1)} -> node_{uri_to_dot_id(nested_call1_ret_obj_state)};
            node_{uri_to_dot_id(arg0)} -> node_{uri_to_dot_id(nested_call1)} [label="REF"];
            """, file = out_fd)

        # nested call refs
        rq = """
        select ?nested_call ?ref_obj_state {
          ?nested_call rdf:type <NestedCall>.
          ?ref_obj_state rdf:type <ObjState>.
          ?nested_call <nested-call-ref> ?ref_obj_state.
        }
        """
        for nested_call, ref_obj_state in g.query(rq, base = fstriplestore.base_uri):
            print(f"""
            node_{uri_to_dot_id(ref_obj_state)} -> node_{uri_to_dot_id(nested_call)} [label="ref"];
            """, file = out_fd)
            
        rq = """
        select ?from_obj ?to_obj ?pred { 
          ?from_obj <df-projection>|<to_datetime> ?to_obj;
                    ?pred ?to_obj 
        }
        """
        for from_obj, to_obj, pred in g.query(rq, base = fstriplestore.base_uri):
            pred_s = pred.toPython().split('/')[-1]
            print(f"""
            node_{uri_to_dot_id(to_obj)} -> node_{uri_to_dot_id(from_obj)} [label="{pred_s}", penwidth=2.5];
            """, file = out_fd)
        
            
    print("}", file = out_fd)
    return out_fd.getvalue()

def print_dot(vertical = False, show_objects = False):
    #ipdb.set_trace()
    g = fstriplestore.triple_store.get_graph()
    print(dump_dot_code(g, vertical = vertical, show_objects = show_objects))

def save_dot(dot_output_fn = None, vertical = False, show_objects = False):
    ts = fstriplestore.triple_store
    if dot_output_fn is None:
        if hasattr(ts, 'output_fn') and ts.output_fn is not None:
            ttl_output_fn = ts.output_fn
            dot_output_fn = ttl_output_fn + ".dot"
        else:
            raise Exception("can't guess dot_output_fn")

    g = ts.get_graph()
    dot_code = dump_dot_code(g, vertical = vertical, show_objects = show_objects)
    gvz = graphviz.Source(dot_code)
    gvz.render(dot_output_fn, format = 'svg', engine = 'dot')

def show(vertical = False, show_objects = False):
    ts = fstriplestore.triple_store
    if not (hasattr(ts, 'output_fn') and ts.output_fn is None):
        raise Exception("triple sink is not in-memory file")

    g = ts.get_graph()
    dot_code = dump_dot_code(g, vertical = vertical, show_objects = show_objects)
    nb_utils.show_method_chain(dot_code)
