import weakref
import uuid

class TrackingObj:
    def __init__(self, obj):
        self.obj_wref = weakref.ref(obj)
        self.uuid = uuid.uuid4()
        self.pyid = id(obj)
        self.version = 0

    def is_alive(self):
        return not self.obj_wref() is None

    def incr_version(self):
        ret = self.version
        self.version += 1
        return ret

class TrackingStore:
    def __init__(self):
        self.tracking_objs = {} # id(obj) -> TrackingObj
        self.tracking_objs_by_wrapped_obj_id = {} # id(obj.obj) -> TrackingObj

    def get_tracking_obj(self, obj):
        obj_pyid = id(obj)
        tracking_obj = None
        if obj_pyid in self.tracking_objs:
            candidate_tracking_obj = self.tracking_objs.get(obj_pyid)
            if candidate_tracking_obj.is_alive():
                tracking_obj = candidate_tracking_obj

        if tracking_obj is None:
            tracking_obj = self.tracking_objs[obj_pyid] = TrackingObj(obj)
            self.tracking_objs_by_wrapped_obj_id[id(obj.u_obj)] = tracking_obj

        return tracking_obj

    def find_tracking_obj(self, wrapped_obj):
        return self.tracking_objs_by_wrapped_obj_id.get(id(wrapped_obj))
    
    def set_tracking_obj_attr(self, obj, attr_name, attr_value):
        tracking_obj = self.get_tracking_obj(obj)
        setattr(tracking_obj, attr_name, attr_value)
        return tracking_obj

tracking_store = TrackingStore()
