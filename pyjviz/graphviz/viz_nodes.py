import ipdb
import os.path
import uuid
#import tempfile
import rdflib
import pandas as pd
import re, html
from ..rdf import fstriplestore
from . import viz_utils

def dot_pseudo_html_escape(s):
    """
    this function will escape some characters like <, >
    it has to be done in such complicated way to avoid corruption of html tags
    supported by graphviz dot pseudo-html used in dot labels
    label pseudo-html description: https://graphviz.org/doc/info/shapes.html#html
    """
    tags = ["<BR>", "<br/>", "<hr/>", "<B>", "</B>", "<i>", "</i>"]
    pseudo_tags = [x[1:-1].lower() for x in tags]
    tokens = [x for x in re.split("(<|>)", s) if len(x) > 0]
    i = 0
    l = len(tokens)
    #ipdb.set_trace()
    while i < l:
        t = tokens[i]
        if t == '<':
            n_t = tokens[i+1] if i+1 < l else None
            if n_t is None:
                break
            close_bracket_i = tokens.index(">", i+1)
            if n_t.lower().split(' ')[0] in pseudo_tags and close_bracket_i:
                i = close_bracket_i + 1
                continue
        
        tokens[i] = html.escape(t)
        i += 1
                
    ret = "".join(tokens)        
    return ret


def to_uri(s):
    return rdflib.URIRef(s, base=fstriplestore.base_uri)


def uri_to_dot_id(uri):
    return str(hash(uri)).replace("-", "d")


def rq_d(g, rq, init_bindings):
    rq_res = g.query(
        rq, base=fstriplestore.base_uri, initBindings=init_bindings
    )
    if len(rq_res) != 1:
        raise Exception(
            f"rq_d: query result has length {len(rq_res)}, expected to be 1"
        )
    return {k.toPython()[1:]: v for k, v in rq_res.bindings[0].items()}


def rq_df(g, rq, init_bindings):
    rq_res = g.query(
        rq, base=fstriplestore.base_uri, initBindings=init_bindings
    )
    return (
        pd.DataFrame.from_dict(rq_res.bindings).loc[:, rq_res.vars]
        if len(rq_res) > 0
        else pd.DataFrame(columns=rq_res.vars)
    )


def make_table_popup_href(head_html, popup_output):
    if head_html is None:
        return ""

    table_html = fstriplestore.from_base64(head_html.toPython())

    # svg output generation with inline tables and images
    # graphviz href will be replaced with onclick to provide popup window functionality
    popup_size = (800, 200)
    s_id = str(uuid.uuid4())
    viz_utils.big_strings_table[s_id] = table_html
    href = f"""href="javascript:
    window.open('', '_blank', 'width={popup_size[0]},height={popup_size[1]}').document.body.innerHTML = `%%{s_id}%%`
    "
    """

    return href


def make_image_popup_href(image_b64, popup_output):
    img_html = (
        "<img src='data:image/png;base64," + image_b64.toPython() + "'></img>"
    )

    popup_size = (900, 500)
    s_id = str(uuid.uuid4())
    viz_utils.big_strings_table[s_id] = img_html
    href = f"""href="javascript:
    window.open('', '_blank', 'width={popup_size[0]},height={popup_size[1]}').document.body.innerHTML = `%%{s_id}%%`
    "
    """

    return href


class ObjStateGraphVizNode:
    def __init__(self, g, obj_state, popup_output):
        self.popup_output = popup_output
        self.g = g
        self.obj_state = obj_state

        self.version = None
        self.node_bgcolor = "#88000022"
        self.df_shape = None
        self.s_size = None

        self.href = ""

    def build_label(self):
        obj_state_rq = """
        select ?obj_type ?version {
          ?obj_state <obj> ?obj; <version> ?version.
          ?obj rdf:type <ObjId>; <obj-type> ?obj_type.
        }
        """
        res_d = rq_d(self.g, obj_state_rq, {"obj_state": self.obj_state})
        self.version = res_d.get("version")
        self.obj_type = res_d.get("obj_type").toPython()

        cc_rq = """
        select ?cc_type ?df_shape ?s_size ?text {
          ?obj_state rdf:type ?cc_type.
          ?cc_type rdfs:subClassOf <CCObjStateLabel>.
          optional {?obj_state <df-shape> ?df_shape}
          optional {?obj_state <s-size> ?s_size}
          optional {?obj_state <text> ?text}
        }
        """
        res_d = rq_d(self.g, cc_rq, {"obj_state": self.obj_state})
        
        cc_type = res_d.get("cc_type")        
        if cc_type == rdflib.URIRef(
            "CCObjStateLabelDataFrame", base=fstriplestore.base_uri
        ):
            self.df_shape = res_d.get("df_shape").toPython()
        elif cc_type == rdflib.URIRef(
            "CCObjStateLabelSeries", base=fstriplestore.base_uri
        ):
            self.s_size = res_d.get("s_size").toPython()
        else:
            raise Exception(f"unknown cc_type {cc_type}")

        self.text = res_d.get("text").toPython() if "text" in res_d else None

    def build_popup_content(self):
        rq = """
        select ?obj_state ?cc_type {
           ?obj_state rdf:type ?cc_type.
           ?cc_type rdfs:subClassOf+ <CC>.
        }
        """
        res_df = rq_df(self.g, rq, {"obj_state": self.obj_state})

        for _, obj_state, cc_type in res_df.itertuples():
            if cc_type == to_uri("CCGlance"):
                if self.obj_type == "DataFrame":
                    rq = "select ?df_head { ?obj_state <df-head> ?df_head }"
                    rq_res = rq_d(self.g, rq, {"obj_state": obj_state})
                    self.node_bgcolor = "#88000022"
                    self.href = make_table_popup_href(
                        rq_res.get("df_head"), self.popup_output
                    )
                elif self.obj_type == "Series":
                    rq = "select ?s_head { ?obj_state <s-head> ?s_head }"
                    rq_res = rq_d(self.g, rq, {"obj_state": obj_state})
                    self.node_bgcolor = "#88000022"
                    self.href = make_table_popup_href(
                        rq_res.get("s_head"), self.popup_output
                    )
                else:
                    raise Exception(f"unknown obj_type {self.obj_type}")
            elif cc_type == to_uri("CCBasicPlot"):
                rq = "select ?plot_im { ?obj_state <plot-im> ?plot_im }"
                rq_res = rq_d(self.g, rq, {"obj_state": obj_state})
                self.node_bgcolor = "#44056022"
                self.href = make_image_popup_href(
                    rq_res.get("plot_im"), self.popup_output
                )
            else:
                raise Exception(f"unknown cc_type {cc_type}")

    def dump(self, out_fd):
        version_s = (
            " " if self.version.toPython() == "0" else self.version.toPython()
        )
        shape_s = None
        if self.df_shape:
            shape_s = f"{self.df_shape}"
        elif self.s_size:
            shape_s = f"{self.s_size}"
        else:
            raise Exception("neither df nor series params are set")

        if self.text:
            #ipdb.set_trace()
            text_s = dot_pseudo_html_escape(fstriplestore.from_base64(self.text))
            print(f"""
            node_{uri_to_dot_id(self.obj_state)} [
                color="{self.node_bgcolor}"
                shape = rect
                label = <{text_s}>
                {self.href}
            ];
            """, file = out_fd)
        else:
            print(
                f"""
                node_{uri_to_dot_id(self.obj_state)} [
                color="{self.node_bgcolor}"
                shape = rect
                label = <<table border="0" cellborder="0" cellspacing="0" cellpadding="4">
                <tr> <td>{self.obj_type}</td><td>{shape_s}</td> </tr>
                <tr> <td> <font face="small" point-size="8px"><b>{self.obj_state.split('/')[-1]}</b> <i>{version_s}</i></font></td></tr>
                </table>>
                {self.href}
                ];
                """,
                file=out_fd,
            )
