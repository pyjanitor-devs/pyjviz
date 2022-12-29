import pandas_flavor.register

def enable_pf_pandas():
    pandas_flavor.register.handle_pandas_method_call = handle_pandas_method_call

def handle_pandas_method_call(obj, method_name, args, kwargs, ret):
    print("handle_pandas_method_call", id(obj))
    return
    
    if methods_chain.curr_methods_chain_path:
        self.obj.obj_chain_path = methods_chain.curr_methods_chain_path if self.obj.obj_chain_path is None else self.obj.obj_chain_path

    if self.obj.obj_chain_path:
        thread_id = threading.get_native_id()
        method_call_uri = rdfl.dump_method_call_in(thread_id, self.obj, self.method_name, method_args, method_kwargs)

    real_method_args = [x.u_obj if isinstance(x, UWObject) else x for x in method_args]
    ret = self.bound_method(*real_method_args, **method_kwargs)

    if self.obj.obj_chain_path is None:
        ret_obj = ret
    else:
        ret_obj, obj_found = uw_object_factory.get_obj(ret)
        if obj_found:
            ret_obj.incr_version()
        else:
            ret_obj.obj_chain_path = self.obj.obj_chain_path

        ret_obj.last_obj_state_uri = rdfl.dump_obj_state(ret_obj)
        rdfl.dump_triple__(method_call_uri, "<method-call-return>", ret_obj.last_obj_state_uri)


    ret_obj.last_obj_state_uri = rdfl.dump_obj_state(ret_obj)
    rdfl.dump_triple__(method_call_uri, "<method-call-return>", ret_obj.last_obj_state_uri)
