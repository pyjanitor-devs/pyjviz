from functools import singledispatchmethod
import pandas as pd
import textwrap
import io, base64

def to_base64(s):
    return base64.b64encode(s.encode('ascii')).decode('ascii')

class CCGraphvizObjStateLabel:
    def __init__(self, triple_store):
        self.triple_store = triple_store

    @singledispatchmethod
    def to_rdf(self, obj, uri):
        raise Exception(f"can't find impl to_rdf for {type(obj)}, uri was {uri}")

    @to_rdf.register
    def to_rdf_impl(self, obj: pd.DataFrame, uri: str) -> None:
        ts = self.triple_store
        df = obj
        ts.dump_triple(uri, "rdf:type", "<CCGraphVizObjStateLabel>")
        obj_type = type(obj).__name__
        shape = df.shape
        label = f"<tr> <td>{obj_type}</td><td>{df.shape}</td> </tr>"        
        ts.dump_triple(uri, "<graphviz-obj-state-label>", '"' + to_base64(label) + '"')        

    @to_rdf.register
    def to_rdf_impl(self, obj: pd.Series, uri: str) -> None:
        ts = self.triple_store
        df = obj
        ts.dump_triple(uri, "rdf:type", "<CCGraphVizObjStateLabel>")
        obj_type = type(obj).__name__
        size = obj.shape
        label = f"<tr> <td>{obj_type}</td><td>{size}</td> </tr>"
        ts.dump_triple(uri, "<graphviz-obj-state-label>", '"' + to_base64(label) + '"')        

        
class CCGlance:
    def __init__(self, triple_store):
        self.triple_store = triple_store

    @singledispatchmethod
    def to_rdf(self, obj, uri):
        raise Exception(f"can't find impl to_rdf for {type(obj)}, uri was {uri}")

    @to_rdf.register    
    def to_rdf_impl(self, obj: pd.DataFrame, uri: str) -> None:
        ts = self.triple_store
        df = obj
        ts.dump_triple(uri, "rdf:type", "<CCGlance>")
        ts.dump_triple(uri, "<shape>", f'"{df.shape}"')
        df_head_html = (
            df.head(10)
            .applymap(lambda x: textwrap.shorten(str(x), 50))
            .to_html()
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("\n", "&#10;")
        )
        ts.dump_triple(uri, "<df-head>", '"' + df_head_html + '"')

    @to_rdf.register
    def to_rdf_impl(self, obj: pd.Series, uri: str) -> None:        
        ts = self.triple_store
        s = obj
        ts.dump_triple(uri, "rdf:type", "<CCGlance>")
        ts.dump_triple(uri, "<shape>", f"{len(s)}")
        ts.dump_triple(uri, "<df-head>", '"NONE"')

class CCBasicPlot:
    def __init__(self, triple_store):
        self.triple_store = triple_store

    @singledispatchmethod
    def to_rdf(self, obj, uri):
        raise Exception(f"can't find impl to_rdf for {type(obj)}, uri was {uri}")

    @to_rdf.register
    def to_rdf_impl(self, obj: pd.DataFrame, uri: str) -> None:
        ts = self.triple_store
        df = obj
        ts.dump_triple(uri, "rdf:type", "<CCBasicPlot>")
        ts.dump_triple(uri, "<shape>", f'"{df.shape}"')
        out_fd = io.BytesIO()
        fig = df.plot().get_figure()
        fig.savefig(out_fd)
        # ipdb.set_trace()
        im_s = base64.b64encode(out_fd.getvalue()).decode("ascii")
        ts.dump_triple(uri, "<plot-im>", '"' + im_s + '"')

    @to_rdf.register
    def to_rdf_impl(self, obj: pd.Series, uri: str) -> None:
        ts = self.triple_store
        ts.dump_triple(uri, "rdf:type", "<CCBasicPlot>")
        ts.dump_triple(uri, "<shape>", f"{len(s)}")
        out_fd = io.BytesIO()
        fig = s.plot().get_figure()
        fig.savefig(out_fd)
        # ipdb.set_trace()
        im_s = base64.b64encode(out_fd.getvalue()).decode("ascii")
        ts.dump_triple(uri, "<plot-im>", '"' + im_s + '"')
