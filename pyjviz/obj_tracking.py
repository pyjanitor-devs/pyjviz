import weakref
import uuid
from . import fstriplestore

def obj_del_cb(ref):
    print("obj deleted", ref)
    
class TrackingObj:
    def __init__(self, obj):
        self.obj_wref = weakref.ref(obj, obj_del_cb)
        self.uuid = uuid.uuid4()
        self.pyid = id(obj)
        self.last_version_num = 0
        self.last_obj_state_uri = None
        
        self.uri = f"<Obj#{self.uuid}>"

        fstriplestore.triple_store.dump_triple(self.uri, "rdf:type", "<Obj>")
        fstriplestore.triple_store.dump_triple(self.uri, "<obj-type>", f'"{type(obj).__name__}"')
        fstriplestore.triple_store.dump_triple(self.uri, "<obj-uuid>", f'"{self.uuid}"')
        fstriplestore.triple_store.dump_triple(self.uri, "<obj-pyid>", f'{self.pyid}')
        
    def is_alive(self):
        return not self.obj_wref() is None

    def incr_version(self):
        ret = self.last_version_num
        self.last_version_num += 1
        return ret
    
class TrackingStore:
    def __init__(self):
        self.tracking_objs = {} # id(obj) -> TrackingObj

    def find_tracking_obj(self, obj):
        t_obj, obj_found = self.get_tracking_obj(obj, add_missing = False)
        return t_obj
        
    def get_tracking_obj(self, obj, add_missing = True):
        obj_found = False
        obj_pyid = id(obj)
        tracking_obj = None
        if obj_pyid in self.tracking_objs:
            obj_found = True
            candidate_tracking_obj = self.tracking_objs.get(obj_pyid)
            if candidate_tracking_obj.is_alive():
                tracking_obj = candidate_tracking_obj

        if tracking_obj is None and add_missing:
            tracking_obj = self.tracking_objs[obj_pyid] = TrackingObj(obj)

        return tracking_obj, obj_found

tracking_store = TrackingStore()
