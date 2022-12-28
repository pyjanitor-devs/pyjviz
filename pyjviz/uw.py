import ipdb
import threading
import uuid
#from . import obj_tracking
from . import rdflogging
from . import methods_chain

class UWMethodCall:
    def __init__(self, obj, method_name, bound_method):
        self.obj = obj
        self.method_name = method_name
        self.bound_method = bound_method
        
    def __call__(self, *method_args, **method_kwargs):
        rdfl = rdflogging.rdflogger

        print("__call__", self.method_name)
        #ipdb.set_trace()

        if methods_chain.curr_methods_chain:
            thread_id = threading.get_native_id()
            self.obj.obj_chain = methods_chain.curr_methods_chain
            method_call_uri = rdfl.dump_method_call_in(thread_id, self.obj, self.method_name, method_args, method_kwargs)
            
        real_method_args = [x.u_obj if isinstance(x, UWObject) else x for x in method_args]
        ret = self.bound_method(*real_method_args, **method_kwargs)

        if not methods_chain.curr_methods_chain:
            ret_obj = ret
        else:
            ret_obj, obj_found = uw_object_factory.get_obj(ret)
            if obj_found:
                ret_obj.incr_version()
            else:
                ret_obj.obj_chain = self.obj.obj_chain

            ret_obj.last_obj_state_uri = rdfl.dump_obj_state(ret_obj)
            rdfl.dump_triple__(method_call_uri, "<method-call-return>", ret_obj.last_obj_state_uri)
            
        return ret_obj

class UWObject:
    def __init__(self, u_obj):
        if isinstance(u_obj, UWObject):
            raise Exception("attempt to create UWObject with u_obj of type UWObject")
        self.u_obj = u_obj

        self.uuid = uuid.uuid4()
        self.pyid = id(self)
        self.last_version_num = 0
        self.last_obj_state_uri = None
        self.obj_chain = None

        uw_object_factory.objs[id(u_obj)] = self
        
    def incr_version(self):
        ret = self.last_version_num
        self.last_version_num += 1
        return ret
        
    def __getattr__(self, attr):
        u_obj = self.__getattribute__('u_obj')
        method_name = attr
        bound_method = getattr(u_obj, method_name)
        return UWMethodCall(self, method_name, bound_method)

    def continue_to(self, chain):
        self.obj_chain = chain            
        return self

    def return_to(self, method_call_return_chain):
        rdfl = rdflogging.rdflogger
        method_call_return_chain_uri = rdfl.register_chain(method_call_return_chain)
        self.obj_chain = method_call_return_chain
        rdfl.dump_triple__(self.last_obj_state_uri, "<chain-replacement>", method_call_return_chain_uri)
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
