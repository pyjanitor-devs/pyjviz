import ipdb
import threading
import uuid
from . import obj_tracking
from . import rdflogging
from . import methods_chain

from pandas import DataFrame

class UWMethodCall:
    def __init__(self, obj, method_name, bound_method):
        self.obj = obj
        self.method_name = method_name
        self.bound_method = bound_method
        
    def __call__(self, *method_args, **method_kwargs):
        rdfl = rdflogging.rdflogger

        print("__call__", self.method_name)
        ipdb.set_trace()

        if methods_chain.curr_methods_chain_path:
            t_obj = obj_tracking.tracking_store.get_tracking_obj(self.obj)
            chain_path = "/" + "/".join(methods_chain.curr_methods_chain_path)            

            thread_id = threading.get_native_id()
            method_call_uri = rdfl.dump_method_call_in(chain_path, thread_id, self.obj, t_obj, self.method_name, method_args, method_kwargs)
            
        real_method_args = [x.u_obj if isinstance(x, UWObject) else x for x in method_args]
        ret = self.bound_method(*real_method_args, **method_kwargs)

        if ret is None:
            ret = self.obj.u_obj
        
        if not methods_chain.curr_methods_chain_path:
            ret_obj = ret
        else:
            ret_obj, obj_found = uw_object_factory.get_obj(ret)
            ret_t_obj = obj_tracking.tracking_store.get_tracking_obj(ret_obj)
            if obj_found:
                ret_t_obj.incr_version()

            ret_t_obj.last_obj_state_uri = rdfl.dump_obj_state(chain_path, ret_obj, ret_t_obj)
            rdfl.dump_triple__(method_call_uri, "<method-call-return>", ret_t_obj.last_obj_state_uri)
            
        return ret_obj

class UWObject:
    def __init__(self, u_obj):
        if isinstance(u_obj, UWObject):
            raise Exception("attempt to create UWObject with u_obj of type UWObject")

        if isinstance(u_obj, DataFrame):
            raise Exception("can't create wrapped DataFrame")

        self.u_obj = u_obj

        if 0: # all atributes are kept in tracking object
            self.uuid = uuid.uuid4()
            self.pyid = id(self)
            self.last_version_num = 0
            self.last_obj_state_uri = None
            self.obj_chain_path = None

        uw_object_factory.objs[id(u_obj)] = self

    """
    def incr_version(self):
        ret = self.last_version_num
        self.last_version_num += 1
        return ret
    """
    
    def __getattr__(self, attr):
        u_obj = self.__getattribute__('u_obj')
        method_name = attr
        bound_method = getattr(u_obj, method_name)
        return UWMethodCall(self, method_name, bound_method)

    def set_chain(self, chain_path):
        if methods_chain.curr_methods_chain_path is None:
            methods_chain.curr_methods_chain_path = []
        methods_chain.curr_methods_chain_path.append(chain_path)
        return self

    def reset_chain(self):
        methods_chain.curr_methods_chain_path.pop()
        if len(methods_chain.curr_methods_chain_path) == 0:
            methods_chain.curr_methods_chain_path = None
        return self

class UWObjectFactory:
    def __init__(self):
        self.objs = {} # id(obj.u_obj) -> obj

    def get_obj(self, wrapped_obj):
        ret0 = self.objs.get(id(wrapped_obj), None)
        return (ret0, True) if ret0 else (UWObject(wrapped_obj), False)

    def find_obj(self, wrapper_obj):
        return id(wrapper_obj) in self.objs
    
uw_object_factory = UWObjectFactory()
