import sys
from . import obj_tracking
from . import obj_utils
from . import wb_stack
from . import fstriplestore
from . import rdf_node


class profile_objs:
    def __init__(self):
        self.collected_ids = set()

    def collect_obj_ids(self, frame, event, arg):
        trs = obj_tracking.tracking_store

        gs = frame.f_globals
        global_ids = [
            (
                trs.get_uuid(id(gs.get(x))),
                trs.get_last_obj_state_uri(id(gs.get(x))),
            )
            for x in frame.f_code.co_names
            if x in gs
        ]
        self.collected_ids.update(global_ids)

        ls = frame.f_locals
        local_ids = [
            (
                trs.get_uuid(id(ls.get(x))),
                trs.get_last_obj_state_uri(id(ls.get(x))),
            )
            for x in frame.f_code.co_varnames
            if x in ls
        ]
        self.collected_ids.update(local_ids)

        sys.setprofile(self.collect_obj_ids)

    def __enter__(self):
        sys.setprofile(self.collect_obj_ids)

    def __exit__(self, type, value, traceback):
        sys.setprofile(None)

    def dump_nested_call_refs(self, nested_call_uri):
        print("nested call:", nested_call_uri)
        print("collected ids:", self.collected_ids)
        ts = fstriplestore.triple_store

        for _, ref_obj_state_uri in self.collected_ids:
            if ref_obj_state_uri:
                ts.dump_triple(
                    nested_call_uri, "<nested-call-ref>", ref_obj_state_uri
                )


class NestedCall(rdf_node.RDFNode):
    """
    NestedCall object is to represent situation like this:
    ```python
    df.assign(date_as_obj = lambda x: pd.to_datetime(x.date_string),
              description = lambda x: x.description.lower)
    ```

    Corresponding NestedCall objects are:

    ```python
    NestedCall(arg_name = 'date_as_obj', arg_func = lambda x: pd.to_datetime(x.date_string))
    NestedCall(arg_name = 'description', arg_func = lambda x: x.description.lower)
    ```

    During method handling (`assign` in example above, see MethodCall.handle_start_method_call) the arguments which are isfunction(arg) == True will be converted to NestedCall object.
    The code then proceed and causes controlled call of `nested_call_func` via __call__ implementation. Results are saved as self.ret and later used by MethodCall.handle_end_method_call
    """

    def __init__(self, arg_name, arg_func):
        super().__init__(
            rdf_type="NestedCall", label=f"nested_call({arg_name})"
        )
        rdfl = fstriplestore.triple_store
        parent_uri = wb_stack.wb_stack.stack_entries__[-1].uri
        rdfl.dump_triple(self.uri, "<part-of>", parent_uri)

        # ipdb.set_trace()
        self.arg_name = arg_name
        self.arg_func = arg_func
        self.ret = None

    def __call__(self, *args, **kwargs):
        ts = fstriplestore.triple_store
        print("NestedCall called")

        ctx = profile_objs()
        # ctx = contextlib.nullcontext()
        with ctx:
            self.ret = self.arg_func(*args, **kwargs)

        ctx.dump_nested_call_refs(self.uri)

        ret_t_obj, obj_found = obj_tracking.tracking_store.get_tracking_obj(
            self.ret
        )
        if not obj_found:
            ret_t_obj = obj_utils.dump_obj_state(self.ret)
        return self.ret
