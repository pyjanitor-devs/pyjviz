import ipdb
import threading
import uuid
#from . import obj_tracking
from . import rdflogging

method_counter = 0

class UWMethodCall:
    def __init__(self, obj, method_name, bound_method):
        self.obj = obj
        self.method_name = method_name
        self.bound_method = bound_method
        
    def __call__(self, *method_args, **method_kwargs):
        rdfl = rdflogging.rdflogger

        print("__call__", self.method_name)
        ipdb.set_trace()
        obj_chain = self.obj.obj_chain
        method_call_chain = self.obj.method_chain
        method_call_chain = method_call_chain if method_call_chain else obj_chain

        if rdflogging.rdflogger:
            if obj_chain and obj_chain.is_active:
                thread_id = threading.get_native_id()
                thread_uri = rdfl.register_thread(thread_id)
                method_call_chain_uri = rdfl.register_chain(method_call_chain)
                method_call_id = rdfl.random_id; rdfl.random_id += 1
                method_call_uri = f"<MethodCall#{method_call_id}>"

                rdfl.dump_triple__(method_call_uri, "rdf:type", "<MethodCall>")
                rdfl.dump_triple__(method_call_uri, "rdf:label", '"' + self.method_name + '"')
                rdfl.dump_triple__(method_call_uri, "<method-thread>", thread_uri)
                global method_counter
                rdfl.dump_triple__(method_call_uri, "<method-counter>", method_counter); method_counter += 1
                rdfl.dump_triple__(method_call_uri, "<method-call-chain>", method_call_chain_uri)
                
                arg0_tobj = obj_tracking.tracking_store.get_tracking_obj(self.obj)
                arg0_osca_uri = rdfl.register_osca(arg0_tobj, obj_chain)
                rdfl.dump_triple__(method_call_uri, "<method-call-arg0>", arg0_osca_uri)        

                c = 1
                for arg_obj in method_args:
                    if isinstance(arg_obj, UWObject):
                        arg_tobj = obj_tracking.tracking_store.get_tracking_obj(arg_obj)
                        arg_obj_chain = arg_tobj.obj_chain
                        arg_osca_uri = rdfl.register_osca(arg_tobj, arg_obj_chain)
                        rdfl.dump_triple__(method_call_uri, f"<method-call-arg{c}>", arg_osca_uri)
                    c += 1
                
        real_method_args = [x.u_obj if isinstance(x, UWObject) else x for x in method_args]
        ret = self.bound_method(*real_method_args, **method_kwargs)

        if ret is None:
            ret_obj = self.obj
            ret_obj.incr_version()
        else:
            ret_obj, obj_found = uw_object_factory.get_obj(ret)
            if obj_found:
                ret_obj.incr_version()

        ret_obj.obj_chain = self.obj.obj_chain
                
        if rdflogging.rdflogger:
            if obj_chain and obj_chain.is_active:                
                ret_osca_uri = rdfl.register_osca(ret_obj, method_call_chain)
                rdfl.dump_triple__(method_call_uri, "<method-call-return>", ret_osca_uri)                
            
        return ret_obj

class UWObject:
    def __init__(self, u_obj, right_way = False):
        if not right_way:
            raise Exception("use UWObjectFactory to create UWObject")
        self.u_obj = u_obj

        self.uuid = uuid.uuid4()
        self.pyid = id(self)
        self.last_version_num = 0
        self.obj_chain = None
        self.method_chain = None

    def incr_version(self):
        ret = self.last_version_num
        self.last_version_num += 1
        return ret
        
    def __getattr__(self, attr):
        u_obj = self.__getattribute__('u_obj')
        method_name = attr
        bound_method = getattr(u_obj, method_name)
        return UWMethodCall(self, method_name, bound_method)
    
    def continue_to(self, method_call_chain):
        self.method_call_chain = method_call_chain
        return self

    def return_to(self, method_call_return_chain):
        rdfl = rdflogging.rdflogger
        method_call_return_chain_uri = rdfl.register_chain(method_call_return_chain)
        self.method_call_chain = method_call_return_chain
        osca_uri = rdfl.register_osca(self, method_call_return_chain)
        rdfl.dump_triple__(osca_uri, "<chain-replacement>", method_call_return_chain_uri)
        return self

class UWObjectFactory:
    def __init__(self):
        self.objs = {} # id(obj.u_obj) -> obj

    def create_obj(self, u_obj):
        ret = UWObject(u_obj, True)
        self.objs[id(u_obj)] = ret
        return ret

    def get_obj(self, wrapped_obj):
        ret0 = self.objs.get(id(wrapped_obj), None)
        return (ret0, True) if ret0 else (self.create_obj(wrapped_obj), False)
    
    
uw_object_factory = UWObjectFactory()
