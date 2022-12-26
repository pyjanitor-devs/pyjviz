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
        #ipdb.set_trace()
        obj_chain_uri = rdfl.register_chain(self.obj.obj_chain)

        if 1: # self.obj.obj_chain.is_active:
            thread_id = threading.get_native_id()
            thread_uri = rdfl.register_thread(thread_id)
            method_call_id = rdfl.random_id; rdfl.random_id += 1
            method_call_uri = f"<MethodCall#{method_call_id}>"

            rdfl.dump_triple__(method_call_uri, "rdf:type", "<MethodCall>")
            rdfl.dump_triple__(method_call_uri, "rdf:label", '"' + self.method_name + '"')
            rdfl.dump_triple__(method_call_uri, "<method-thread>", thread_uri)
            global method_counter
            rdfl.dump_triple__(method_call_uri, "<method-counter>", method_counter); method_counter += 1
            rdfl.dump_triple__(method_call_uri, "<method-call-chain>", obj_chain_uri)

            if self.obj.last_obj_state_uri is None:
                self.obj.last_obj_state_uri = rdfl.dump_obj_state(self.obj)
            rdfl.dump_triple__(method_call_uri, "<method-call-arg0>", self.obj.last_obj_state_uri)

            c = 1
            for arg_obj in method_args:
                if isinstance(arg_obj, UWObject):
                    if arg_obj.last_obj_state_uri is None:
                        arg_obj.last_obj_state_uri = rdfl.dump_obj_state(arg_obj)
                    rdfl.dump_triple__(method_call_uri, f"<method-call-arg{c}>", arg_obj.last_obj_state_uri)
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
            else:
                ret_obj.obj_chain = self.obj.obj_chain
                
        if 1: # self.obj.obj_chain.is_active:
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

    def pin(self, chain):
        self.obj_chain = chain
        if 0: # create obj chain assignment
            chain_uri = None
            obj_uri = None
            obj_chain_assignment_uri = None
        return self
            
    def continue_to(self, method_call_chain):
        self.obj_chain = method_call_chain
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
    
    
uw_object_factory = UWObjectFactory()
