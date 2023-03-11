import ipdb
# pyjviz module implements basic visualisation of pyjviz rdf log
# there is no dependency of this code to other part of pyjanitor
#
import rdflib
from io import StringIO
import graphviz

from ..rdf import fstriplestore
from . import nb_utils
from . import viz_nodes
from .viz_nodes import uri_to_dot_id


def dump_subgraph(g, cc_uri, out_fd, popup_output):
    rq = """
    select ?pp ?pl {
      ?pp rdf:type <CodeBlock>; rdf:label ?pl; <part-of> ?sg
    }
    """
    rq_res = g.query(
        rq, base=fstriplestore.base_uri, initBindings={"sg": cc_uri}
    )

    for subgraph, subgraph_label in rq_res:
        if subgraph_label != rdflib.RDF.nil:
            print(
                f"""
            subgraph cluster_{uri_to_dot_id(subgraph)} {{
            label = "{subgraph_label}";
            """,
                file=out_fd,
            )

        dump_subgraph(g, subgraph, out_fd, popup_output)

        rq = """
        select ?obj_state {
            ?obj_state rdf:type <ObjState>; <part-of> ?sg .
        }
        """
        rq_res = g.query(
            rq, base=fstriplestore.base_uri, initBindings={"sg": subgraph}
        )

        for obj_state in rq_res:
            obj_state = obj_state[0]
            n = viz_nodes.ObjStateGraphVizNode(g, obj_state, popup_output)
            n.build_label()
            n.build_popup_content()
            n.dump(out_fd)

        rq = """
        select ?method_call_obj ?method_name ?method_display ?method_count
               ?method_stack_depth ?method_stack_trace {
          ?method_call_obj rdf:type <MethodCall>;
                           rdf:label ?method_name;
                           <method-counter> ?method_count;
                           <method-display> ?method_display;
                           <method-stack-depth> ?method_stack_depth;
                           <method-stack-trace> ?method_stack_trace;
                           <part-of> ?sg .
          ?method_call_obj <method-call-arg0> ?m_arg0; <method-call-return> ?m_ret
          filter(?m_arg0 != ?m_ret)
        }
        """
        for (
            method_call_obj,
            method_name,
            method_display,
            method_count,
            method_stack_depth,
            method_stack_trace,
        ) in g.query(
            rq, base=fstriplestore.base_uri, initBindings={"sg": subgraph}
        ):
            method_display = fstriplestore.from_base64(
                method_display.toPython()
            )
            print(
                f"""
            node_{uri_to_dot_id(method_call_obj)} [ label = <<TABLE border="0" align="left"><TR><TD>{method_display}</TD></TR></TABLE>> ];
            """,
                file=out_fd,
            )

        rq = """
        select ?nested_call ?sg {
          ?nested_call rdf:type <NestedCall>; <part-of> ?method_call.
          ?method_call rdf:type <MethodCall>; <part-of> ?sg.
        }
        """
        for nested_call, sg in g.query(
            rq, base=fstriplestore.base_uri, initBindings={"sg": subgraph}
        ):
            print(
                f"""
            node_{uri_to_dot_id(nested_call)} [ label = "NestedCall" ];
            """,
                file=out_fd,
            )

        rq = "select ?s ?title ?text { ?s rdf:type <Text>; <title> ?title; <text> ?text; <part-of> ?sg }"
        r_df = viz_nodes.rq_df(g, rq, {})
        for ii, s, title, text in r_df.itertuples():
            text_s = (
                fstriplestore.from_base64(text)
                .replace(">", "&gt;")
                .replace("\n", "<br/>")
            )
            print(
                f"""
            node_{uri_to_dot_id(s)} [
            shape = rect
            label = <<table>
            <tr><td>{title}</td></tr>
            <tr><td>{text_s}</td></tr>
            </table>>
            ];
            """,
                file=out_fd,
            )


            
        if subgraph_label != rdflib.RDF.nil:
            print("}", file=out_fd)


def dump_dot_code(g, vertical, show_objects, popup_output):
    # ipdb.set_trace()

    out_fd = StringIO()

    rankdir = "TB" if vertical else "LR"

    print(
        """
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
    """.replace(
            "{rankdir}", rankdir
        ),
        file=out_fd,
    )

    dump_subgraph(g, rdflib.RDF.nil, out_fd, popup_output)

    # for subgraph, subgraph_label in subgraphs:
    if 1:
        # ipdb.set_trace()
        rq = """
        select ?method_call_obj ?arg0_obj ?arg0_name ?ret_obj ?arg1_name ?arg1_obj ?arg2_name ?arg2_obj ?arg3_name ?arg3_obj {
          ?method_call_obj rdf:type <MethodCall>;
                           <method-call-arg0> ?arg0_obj; <method-call-arg0-name> ?arg0_name;
                           <method-call-return> ?ret_obj 
                           filter (?arg0_obj != ?ret_obj) .          
          optional { ?arg1_obj rdf:type <ObjState>. ?method_call_obj <method-call-arg1> ?arg1_obj; <method-call-arg1-name> ?arg1_name }
          optional { ?arg2_obj rdf:type <ObjState>. ?method_call_obj <method-call-arg2> ?arg2_obj; <method-call-arg2-name> ?arg2_name }
          optional { ?arg3_obj rdf:type <ObjState>. ?method_call_obj <method-call-arg3> ?arg3_obj; <method-call-arg3-name> ?arg3_name }
        }
        """
        for (
            method_call_obj,
            arg0_obj,
            arg0_name,
            ret_obj,
            arg1_name,
            arg1_obj,
            arg2_name,
            arg2_obj,
            arg3_name,
            arg3_obj,
        ) in g.query(rq, base=fstriplestore.base_uri):
            print(
                f"""
            node_{uri_to_dot_id(arg0_obj)} -> node_{uri_to_dot_id(method_call_obj)} [label="{arg0_name}"];
            node_{uri_to_dot_id(method_call_obj)} -> node_{uri_to_dot_id(ret_obj)};
            """,
                file=out_fd,
            )

            # NB: copy-paste is bad
            if arg1_obj:
                print(
                    f"""
                node_{uri_to_dot_id(arg1_obj)} -> node_{uri_to_dot_id(method_call_obj)} [label="{arg1_name}"];
                """,
                    file=out_fd,
                )
            if arg2_obj:
                print(
                    f"""
                node_{uri_to_dot_id(arg2_obj)} -> node_{uri_to_dot_id(method_call_obj)} [label="{arg2_name}"];
                """,
                    file=out_fd,
                )
            if arg3_obj:
                print(
                    f"""
                node_{uri_to_dot_id(arg3_obj)} -> node_{uri_to_dot_id(method_call_obj)} [label="{arg3_name}"];
                """,
                    file=out_fd,
                )

    if show_objects:  # show transient objects
        rq = """
        select ?obj ?obj_type ?obj_uuid ?obj_pyid {
          ?obj rdf:type <ObjId>; <obj-type> ?obj_type; <obj-uuid> ?obj_uuid; <obj-pyid> ?obj_pyid
        }
        """
        for obj, obj_type, obj_uuid, obj_pyid in g.query(
            rq, base=fstriplestore.base_uri
        ):
            print(
                f"""
            node_{uri_to_dot_id(obj)} [
            color="#88000022"
            shape = rect
            label = <<table border="0" cellborder="0" cellspacing="0" cellpadding="4">
            <tr> <td> <b>{obj_type}</b><br/>{obj_uuid}<br/>{obj_pyid}</td> </tr>
            </table>>
            ];
            """,
                file=out_fd,
            )

        rq = """
        select ?obj ?obj_state { ?obj_state rdf:type <ObjState>; <obj> ?obj }
        """
        for obj, obj_state in g.query(rq, base=fstriplestore.base_uri):
            print(
                f"""
            node_{uri_to_dot_id(obj)} -> node_{uri_to_dot_id(obj_state)} [label="obj_state"];
            """,
                file=out_fd,
            )

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
        for (
            method_call,
            arg0,
            nested_call1_ret_obj_state,
            arg1_name,
            nested_call1,
        ) in g.query(rq, base=fstriplestore.base_uri):
            print(
                f"""
            node_{uri_to_dot_id(nested_call1_ret_obj_state)} -> node_{uri_to_dot_id(method_call)} [label="{arg1_name.toPython()}"];
            node_{uri_to_dot_id(nested_call1)} -> node_{uri_to_dot_id(nested_call1_ret_obj_state)};
            node_{uri_to_dot_id(arg0)} -> node_{uri_to_dot_id(nested_call1)} [label="REF"];
            """,
                file=out_fd,
            )

        # nested call refs
        rq = """
        select ?nested_call ?ref_obj_state {
          ?nested_call rdf:type <NestedCall>.
          ?ref_obj_state rdf:type <ObjState>.
          ?nested_call <nested-call-ref> ?ref_obj_state.
        }
        """
        for nested_call, ref_obj_state in g.query(
            rq, base=fstriplestore.base_uri
        ):
            print(
                f"""
            node_{uri_to_dot_id(ref_obj_state)} -> node_{uri_to_dot_id(nested_call)} [label="ref"];
            """,
                file=out_fd,
            )

        rq = """
        select ?from_obj ?to_obj ?pred {
          ?from_obj <df-projection>|<to_datetime> ?to_obj;
                    ?pred ?to_obj
        }
        """
        for from_obj, to_obj, pred in g.query(rq, base=fstriplestore.base_uri):
            pred_s = pred.toPython().split("/")[-1]
            print(
                f"""
            node_{uri_to_dot_id(to_obj)} -> node_{uri_to_dot_id(from_obj)} [label="{pred_s}", penwidth=2.5];
            """,
                file=out_fd,
            )

    if 1:
        rq = """
        select ?from ?to ?arrow_label { 
          ?arr rdf:type <Arrow>; <arrow-from> ?from; <arrow-to> ?to .
          optional {?arr <arrow-label> ?arrow_label }
        }
        """
        for from_obj, to_obj, arrow_label in g.query(
            rq, base=fstriplestore.base_uri
        ):
            arrow_label_s = arrow_label.toPython() if arrow_label else ""
            print(
                f"""
            node_{uri_to_dot_id(from_obj)} -> node_{uri_to_dot_id(to_obj)} [label="{arrow_label_s}", penwidth=4.5];
            """,
                file=out_fd,
            )

    print("}", file=out_fd)
    return out_fd.getvalue()


def print_dot(vertical=False, show_objects=False):
    # ipdb.set_trace()
    g = fstriplestore.triple_store.get_graph()
    print(dump_dot_code(g, vertical=vertical, show_objects=show_objects))


def save_dot(
    dot_output_fn=None, vertical=False, show_objects=False, popup_output=True
):
    ts = fstriplestore.triple_store
    if dot_output_fn is None:
        if hasattr(ts, "output_fn") and ts.output_fn is not None:
            ttl_output_fn = ts.output_fn
            dot_output_fn = ttl_output_fn + ".dot"
        else:
            raise Exception("can't guess dot_output_fn")

    g = ts.get_graph()
    dot_code = dump_dot_code(
        g,
        vertical=vertical,
        show_objects=show_objects,
        popup_output=popup_output,
    )
    gvz = graphviz.Source(dot_code)
    gvz.render(dot_output_fn, format="svg", engine="dot")


def show(vertical=False, show_objects=False):
    ts = fstriplestore.triple_store
    if not (hasattr(ts, "output_fn") and ts.output_fn is None):
        raise Exception("triple sink is not in-memory file")

    g = ts.get_graph()
    dot_code = dump_dot_code(
        g, vertical=vertical, show_objects=show_objects, popup_output=False
    )
    nb_utils.show_method_chain(dot_code)
