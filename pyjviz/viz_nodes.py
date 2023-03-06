import os.path
import uuid
import tempfile
import rdflib
import pandas as pd
from . import fstriplestore


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


big_strings_table = {}


def make_table_popup_href(head_html, popup_output):
    if head_html is None:
        return ""

    href = ""
    table_html = fstriplestore.from_base64(head_html.toPython())
    if fstriplestore.triple_store.output_dir:
        temp_dir = os.path.join(fstriplestore.triple_store.output_dir, "tmp")
        temp_file = tempfile.NamedTemporaryFile(
            dir=temp_dir, suffix=".html", delete=False
        )
        with temp_file:
            popup_size = (800, 200)
            temp_file.write(table_html.encode("ascii"))

            if popup_output:
                href = f"""href="javascript:
                {{ window.open(location.pathname.match(/.*\//) + 'tmp/' + '{os.path.basename(temp_file.name)}', '_blank', 'width={popup_size[0]},height={popup_size[1]}'); }}
                "
                """
            else:
                href = 'href="tmp/' + os.path.basename(temp_file.name) + '"'
    else:
        # svg output generation with inline tables and images
        # graphviz href will be replaced with onclick to provide popup window functionality
        popup_size = (800, 200)
        s_id = str(uuid.uuid4())
        global big_strings_table
        big_strings_table[s_id] = table_html
        href = f"""href="javascript:
        window.open('', '_blank', 'width={popup_size[0]},height={popup_size[1]}').document.body.innerHTML = `%%{s_id}%%`
        "
        """

    return href


def make_image_popup_href(image_b64, popup_output):
    img_html = (
        "<img src='data:image/png;base64," + image_b64.toPython() + "'></img>"
    )

    href = ""
    if fstriplestore.triple_store.output_dir:
        temp_dir = os.path.join(fstriplestore.triple_store.output_dir, "tmp")
        with tempfile.NamedTemporaryFile(
            dir=temp_dir, suffix=".html", delete=False
        ) as temp_fp:
            popup_size = (900, 500)
            temp_fp.write(img_html.encode("ascii"))
            if popup_output:
                href = f"""href="javascript:
                {{ window.open(location.pathname.match(/.*\//) + 'tmp/' + '{os.path.basename(temp_fp.name)}', '_blank', 'width={popup_size[0]},height={popup_size[1]}'); }}
                "
                """
            else:
                href = 'href="tmp/' + os.path.basename(temp_fp.name) + '"'
    else:
        popup_size = (900, 500)
        s_id = str(uuid.uuid4())
        global big_strings_table
        big_strings_table[s_id] = img_html
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
        select ?cc_type ?df_shape ?s_size {
          ?obj_state rdf:type ?cc_type.
          ?cc_type rdfs:subClassOf <CCObjStateLabel>.
          optional {?obj_state <df-shape> ?df_shape}
          optional {?obj_state <s-size> ?s_size}
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
