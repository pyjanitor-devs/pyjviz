from . import obj_state


class TrackingStore:
    """
    Singleton used to track ObjState objects
    """
    def __init__(self):
        self.tracking_objs = {}  # id(obj) -> TrackingObj

    def get_uuid(self, obj_pyid):
        t_obj = self.tracking_objs.get(obj_pyid)
        return t_obj.uuid if t_obj and t_obj.is_alive() else None

    def get_last_obj_state_uri(self, obj_pyid):
        t_obj = self.tracking_objs.get(obj_pyid)
        ret = None
        if t_obj and t_obj.is_alive():
            ret = t_obj.last_obj_state.back.uri
        return ret

    def find_tracking_obj(self, obj):
        t_obj, obj_found = self.get_tracking_obj(obj, add_missing=False)
        return t_obj

    def get_tracking_obj(self, obj, add_missing):
        obj_found = False
        obj_pyid = id(obj)
        tracking_obj = None
        if obj_pyid in self.tracking_objs:
            obj_found = True
            candidate_tracking_obj = self.tracking_objs.get(obj_pyid)
            if candidate_tracking_obj.is_alive():
                tracking_obj = candidate_tracking_obj

        if tracking_obj is None and add_missing:
            tracking_obj = self.tracking_objs[obj_pyid] = obj_state.ObjId(obj)

        return tracking_obj, obj_found


tracking_store = TrackingStore()


def get_tracking_obj(obj, add_missing=True):
    global tracking_store
    return tracking_store.get_tracking_obj(obj, add_missing)
