from . import fstriplestore
from . import rdf_utils
from . import rdf_io


def obj_del_cb(ref):
    print("obj deleted", ref)


class ObjIdRDF(rdf_utils.RDFRep):
    def __init__(self, obj_id):
        self.set_rdf_rep(rdf_type="ObjId")
        self.front = obj_id
        self.was_dumped = False

    def dump_rdf(self):
        if self.was_dumped is False:
            self.was_dumped = True
            ts = fstriplestore.triple_store
            ts.dump_triple(self.uri, "rdf:type", self.rdf_type_uri)
            ts.dump_triple(self.uri, "<obj-type>", f'"{self.front.obj_type}"')
            ts.dump_triple(self.uri, "<obj-uuid>", f'"{self.front.uuid}"')
            ts.dump_triple(self.uri, "<obj-pyid>", f"{self.front.pyid}")


obj_state_counter = 0


class ObjStateRDF(rdf_utils.RDFRep):
    def __init__(self, obj_state):
        super().__init__()
        self.front = obj_state
        self.was_dumped = False

        global obj_state_counter
        self.set_rdf_rep(rdf_type="ObjState", obj_id=str(obj_state_counter))
        obj_state_counter += 1

    def dump_rdf(self):
        if self.was_dumped is False:
            self.was_dumped = True
            obj_id = self.front.obj_id
            obj_id.back.dump_rdf()

            ts = fstriplestore.triple_store

            ts.dump_triple(self.uri, "rdf:type", self.rdf_type_uri)
            ts.dump_triple(self.uri, "<obj>", obj_id.back.uri)
            ts.dump_triple(self.uri, "<part-of>", self.front.part_of.back.uri)
            ts.dump_triple(self.uri, "<version>", f'"{obj_id.last_version_num}"')
            if self.front.text:
                ts.dump_triple(self.uri, "<text>", '"' + self.front.text + '"')
            
            obj_state_label_dumper = rdf_io.CCObjStateLabel()
            obj_state_label_dumper.to_rdf(self.front.obj, self.uri)

            # if we dumping DataFrame we want to put content of .head() call
            # into related CC object
            if type(self.front.obj).__name__ in ["DataFrame", "Series"]:
                # put glance to DataFrame
                rdf_io.CCGlance().to_rdf(self.front.obj, self.uri)

    def dump_rdf_text_triple(self):
        ts = fstriplestore.triple_store
        ts.dump_triple(self.uri, "<text>", '"' + self.front.text + '"')
