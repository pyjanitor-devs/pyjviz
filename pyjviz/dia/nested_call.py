import sys
from . import obj_tracking
from . import obj_state
from . import wb_stack
from . import dia_objs
from ..rdf import nested_call_rdf


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


class NestedCall(dia_objs.DiagramObj):
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
    """  # noqa : E501

    def __init__(self, arg_name, arg_func):
        super().__init__(nested_call_rdf.NestedCallRDF, None)
        self.label = f"nested_call({arg_name})"
        self.arg_name = arg_name
        self.arg_func = arg_func
        self.ret = None

    def __call__(self, *args, **kwargs):
        self.ctx = profile_objs()
        with self.ctx:
            ret_obj = self.arg_func(*args, **kwargs)

        ret_obj_id, found = obj_tracking.get_tracking_obj(ret_obj)
        if not found:
            self.ret = obj_state.ObjState(ret_obj, ret_obj_id)
        else:
            self.ret = ret_obj_id.last_obj_state

        self.back.dump_return()
        return ret_obj
