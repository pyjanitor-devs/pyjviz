import threading
import pandas as pd
from . import rdflogging

method_counter = 0

class MethodCallWrapper:
    def __init__(self, self_w, method_name, bound_method, method_call_chain):
        self.self_w = self_w
        self.method_name = method_name
        self.bound_method = bound_method
        self.method_call_chain = method_call_chain if method_call_chain else self.self_w.obj_chain

    def __call__(self, *method_args_, **method_kwargs):
        #ipdb.set_trace()
        chain_is_active = self.self_w.obj_chain.is_active
        if chain_is_active:
            thread_id = threading.get_native_id()

            method_args = []
            for m_arg in method_args_:
                if isinstance(m_arg, ObjWrapper):
                    method_args.append(m_arg.obj)
                else:
                    method_args.append(m_arg)
                    
            ret_obj = self.bound_method(*method_args, **method_kwargs)            

            if rdflogging.rdflogger:
                if id(ret_obj) == id(self.self_w.obj):
                    ret_obj = pd.DataFrame(self.self_w.obj)
                rdfl = rdflogging.rdflogger
                thread_uri = rdfl.register_thread(thread_id)
                method_call_chain_uri = rdfl.register_chain(self.method_call_chain)
                method_call_id = rdfl.random_id; rdfl.random_id += 1
                method_call_uri = f"<pyjviz:MethodCall:{method_call_id}>"
                
                rdfl.dump_triple__(method_call_uri, "rdf:type", "<pyjviz:MethodCall>")
                rdfl.dump_triple__(method_call_uri, "rdf:label", f'"{self.method_name}"')
                rdfl.dump_triple__(method_call_uri, "<pyjviz:method-thread>", thread_uri)
                global method_counter
                rdfl.dump_triple__(method_call_uri, "<pyjviz:method-counter>", method_counter); method_counter += 1
                rdfl.dump_triple__(method_call_uri, "<pyjviz:method-call-chain>", method_call_chain_uri)
                pinned_arg0_uri = rdfl.register_pinned_obj_on_chain(self.self_w.obj, self.self_w.obj_chain)
                rdfl.dump_triple__(method_call_uri, "<pyjviz:method-call-arg0>", pinned_arg0_uri)
                pinned_ret_uri = rdfl.register_pinned_obj_on_chain(ret_obj, self.method_call_chain)
                rdfl.dump_triple__(method_call_uri, "<pyjviz:method-call-return>", pinned_ret_uri)

                c = 1
                for arg in method_args_:
                    if isinstance(arg, ObjWrapper):
                        arg_uri = rdfl.register_pinned_obj_on_chain(arg.obj, arg.obj_chain)
                        rdfl.dump_triple__(method_call_uri, f"<pyjviz:method-call-arg{c}>", arg_uri)
                    c += 1
                
            ret = ObjWrapper(ret_obj, self.method_call_chain, None)
        else:
            ret = ObjWrapper(self.bound_method(*method_args_, **method_kwargs), None, None)
            
        return ret

class ObjWrapper:
    def __init__(self, obj, obj_chain, method_call_chain):
        self.obj = obj
        self.obj_chain = obj_chain
        self.method_call_chain = method_call_chain

    def __str__(self):
        obj = self.__getattribute__('obj')
        return str(obj)

    def pin(self, obj_chain):
        return ObjWrapper(self.obj, obj_chain, None)

    def continue_to(self, method_call_chain):
        return ObjWrapper(self.obj, self.obj_chain, method_call_chain)

    def return_to(self, method_call_return_chain):
        rdfl = rdflogging.rdflogger
        pinned_obj_uri = rdfl.register_pinned_obj_on_chain(self.obj, self.obj_chain)
        replacement_chain_uri = rdfl.register_chain(method_call_return_chain)
        rdflogging.rdflogger.dump_triple__(pinned_obj_uri, "<pyjviz:chain-replacement>", replacement_chain_uri)
        return ObjWrapper(self.obj, self.obj_chain, method_call_return_chain)
    
    def __getattr__(self, attr):
        obj = self.__getattribute__('obj')
        method_name = attr
        bound_method = getattr(obj, method_name)
        return MethodCallWrapper(self, method_name, bound_method, self.method_call_chain)
    
class Chain:
    def __init__(self, chain_name, parent_chain = None):
        self.is_active = False
        self.chain_name = chain_name
        self.parent_chain = parent_chain
        
    def __enter__(self):
        self.is_active = True
        print(f"enter chain {self.chain_name}")
        return self

    def __exit__(self, type, value, traceback):
        self.is_active = False
        print(f"exit chain {self.chain_name}")

    def __del__(self):
        print(f"deleting chain {self.chain_name} {id(self)}")
        
    def pin(self, obj: object) -> ObjWrapper:
        print(f"pin obj {id(obj)} to chain {self.chain_name}")
        return ObjWrapper(obj, self, None)
