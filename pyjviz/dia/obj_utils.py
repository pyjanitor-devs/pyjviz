import uuid
import weakref

from . import dia_objs
from ..rdf import obj_utils_rdf


def obj_del_cb(ref):
    print("obj deleted", ref)


random_id = 0


class ObjId:
    def __init__(self, obj):
        self.obj_wref = weakref.ref(obj, obj_del_cb)
        self.obj_type = type(obj).__name__
        self.uuid = uuid.uuid4()
        self.pyid = id(obj)
        self.last_obj_state = None
        self.last_version_num = 0
        self.back = obj_utils_rdf.ObjIdRDF(self)

    def is_alive(self):
        return not self.obj_wref() is None

    def incr_version(self):
        ret = self.last_version_num
        self.last_version_num += 1
        return ret


class ObjState(dia_objs.DiagramObj):
    def __init__(self, obj, obj_id):
        super().__init__(obj_utils_rdf.ObjStateRDF, None)
        self.obj = obj
        self.obj_id = obj_id
        self.obj_id.last_obj_state = self
