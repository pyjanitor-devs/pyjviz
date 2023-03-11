from __future__ import annotations
from ..dia import dia_objs

from . import fstriplestore
from . import rdf_utils


class TextRDF(rdf_utils.RDFRep):
    def __init__(self, text_obj: dia_objs.Text):
        self.front = text_obj
        self.set_rdf_rep(rdf_type="Text")
        self.was_dumped = False
        
    def dump_rdf(self):
        if self.was_dumped:
            return
        self.was_dumped = True
        ts = fstriplestore.triple_store
        ts.dump_triple(self.uri, "rdf:type", self.rdf_type_uri)
        parent_obj = self.front.part_of
        parent_uri = parent_obj.back.uri if parent_obj else "rdf:nil"
        ts.dump_triple(self.uri, "<part-of>", parent_uri)
        ts.dump_triple(self.uri, "<title>", '"' + self.front.title + '"')
        text_b64 = '"' + fstriplestore.to_base64(self.front.text) + '"'
        ts.dump_triple(self.uri, "<text>", text_b64)


class ArrowRDF(rdf_utils.RDFRep):
    def __init__(self, arrow_obj: dia_obj.Arrow):
        self.front = arrow_obj
        self.set_rdf_rep(rdf_type = "Arrow")

    def dump_rdf(self):
        ts = fstriplestore.triple_store
        ts.dump_triple(self.uri, "rdf:type", self.rdf_type_uri)
        parent_obj = self.front.part_of
        parent_uri = parent_obj.back.uri if parent_obj else "rdf:nil"
        ts.dump_triple(self.uri, "<part-of>", parent_uri)

        self.front.from_dia_obj.back.dump_rdf()
        ts.dump_triple(self.uri, "<arrow-from>", self.front.from_dia_obj.back.uri)
        self.front.to_dia_obj.back.dump_rdf()
        ts.dump_triple(self.uri, "<arrow-to>", self.front.to_dia_obj.back.uri)

        if self.front.label:
            ts.dump_triple(self.uri, "<arrow-label>", '"' + self.front.label + '"')
