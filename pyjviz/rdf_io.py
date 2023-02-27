from functools import singledispatchmethod
import pandas as pd
import textwrap
import io
import base64
from . import fstriplestore


class CCObjStateLabel:
    """
    CCObjStateLabel - provides to_rdf methods to convert objects to RDF class CCObjStateLabel.
    Note that produced RDF node *uri* is subclass of CCObjStateLabel. Full hierarchy of CCObjStateLabel:
    ```mermaid
    graph TD
    CCObjStateLabelDataFrame --> CCObjStateLabel
    CCObjStateLabelSeries --> CCObjStateLabel
    ```
    """
    def __init__(self):
        pass
    
    @singledispatchmethod
    def to_rdf(self, obj, uri):
        raise Exception(f"can't find impl to_rdf for {type(obj)}, uri was {uri}")

    @to_rdf.register
    def to_rdf_impl(self, obj: pd.DataFrame, uri: str) -> None:
        ts = fstriplestore.triple_store
        df = obj
        #ts.dump_triple(uri, "rdf:type", "<CCObjStateLabel>")
        ts.dump_triple(uri, "rdf:type", "<CCObjStateLabelDataFrame>")
        ts.dump_triple(uri, "<df-shape>", f'"{df.shape}"')

    @to_rdf.register
    def to_rdf_impl(self, obj: pd.Series, uri: str) -> None:
        ts = fstriplestore.triple_store
        s = obj
        #ts.dump_triple(uri, "rdf:type", "<CCObjStateLabel>")
        ts.dump_triple(uri, "rdf:type", "<CCObjStateLabelSeries>")
        ts.dump_triple(uri, "<s-size>", f'"{s.shape}"')

        
class CCGlance:
    def __init__(self):
        pass

    @singledispatchmethod
    def to_rdf(self, obj, uri):
        raise Exception(f"can't find impl to_rdf for {type(obj)}, uri was {uri}")

    @to_rdf.register    
    def to_rdf_impl(self, obj: pd.DataFrame, uri: str) -> None:
        ts = fstriplestore.triple_store
        df = obj
        ts.dump_triple(uri, "rdf:type", "<CCGlance>")
        ts.dump_triple(uri, "<shape>", f'"{df.shape}"')
        df_head = df.head(10).applymap(lambda x: textwrap.shorten(str(x), 50)).to_html()
        df_head_b64 = fstriplestore.to_base64(df_head)
        ts.dump_triple(uri, "<df-head>", '"' + df_head_b64 + '"')

    @to_rdf.register
    def to_rdf_impl(self, obj: pd.Series, uri: str) -> None:        
        ts = fstriplestore.triple_store
        s = obj
        ts.dump_triple(uri, "rdf:type", "<CCGlance>")
        ts.dump_triple(uri, "<shape>", f"{len(s)}")
        s_head = "NONE"
        s_head_b64 = fstriplestore.to_base64(s_head)
        ts.dump_triple(uri, "<s-head>", '"' + s_head_b64 + '"')

class CCBasicPlot:
    def __init__(self):
        pass

    @singledispatchmethod
    def to_rdf(self, obj, uri):
        raise Exception(f"can't find impl to_rdf for {type(obj)}, uri was {uri}")

    @to_rdf.register
    def to_rdf_impl(self, obj: pd.DataFrame, uri: str) -> None:
        ts = fstriplestore.triple_store
        df = obj
        ts.dump_triple(uri, "rdf:type", "<CCBasicPlot>")
        ts.dump_triple(uri, "<shape>", f'"{df.shape}"')
        out_fd = io.BytesIO()

        if 1:
            fig = df.plot(backend = 'plotly')
            fig.write_image(file = out_fd, format = 'png')
            im_s = base64.b64encode(out_fd.getvalue()).decode("ascii")
        else:
            out_fd.write("""&lt;img src='data:image/png;base64, iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4
            //8/w38GIAXDIBKE0DHxgljNBAAO
            9TXL0Y4OHwAAAABJRU5ErkJggg==' alt='hello'/&gt;""".encode('ascii'))
            im_s = base64.b64encode(out_fd.getvalue()).decode("ascii")

        ts.dump_triple(uri, "<plot-im>", '"' + im_s + '"')

    @to_rdf.register
    def to_rdf_impl(self, obj: pd.Series, uri: str) -> None:
        ts = fstriplestore.triple_store
        s = obj
        ts.dump_triple(uri, "rdf:type", "<CCBasicPlot>")
        ts.dump_triple(uri, "<shape>", f"{len(s)}")
        out_fd = io.BytesIO()
        fig = s.plot().get_figure()
        fig.savefig(out_fd)
        # ipdb.set_trace()
        im_s = base64.b64encode(out_fd.getvalue()).decode("ascii")
        ts.dump_triple(uri, "<plot-im>", '"' + im_s + '"')
