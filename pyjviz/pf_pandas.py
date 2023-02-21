import pandas as pd
import pandas_flavor as pf
import pandas_flavor.register
import inspect
from contextlib import nullcontext

from . import wb_stack
from . import method_call


class DataFrameFunc:
    def __init__(self, func_name, func):
        self.func_name = func_name
        self.func = func
        self.func_signature = inspect.signature(func)

    def __call__(self, *args, **kwargs):
        # ipdb.set_trace()
        if wb_stack.wb_stack.size() == 0:
            method_ctx = nullcontext()

        latest_method_call = wb_stack.wb_stack.get_latest_method_call()
        if latest_method_call is None:
            method_ctx = method_call.MethodCall(self.func_name)
        else:
            method_ctx = nullcontext()

        with method_ctx:
            if not isinstance(method_ctx, nullcontext):
                new_args, new_kwargs = method_ctx.handle_start_method_call(
                    self.func_name, self.func_signature, args, kwargs
                )
                args = new_args
                kwargs = new_kwargs
            ret_obj = self.func(*args, **kwargs)
            if not isinstance(method_ctx, nullcontext):
                method_ctx.handle_end_method_call(ret_obj)

        return ret_obj


class PandasFlavorMethodCallFactory:
    @staticmethod
    def create(method_name, method_args, method_kwargs):
        if wb_stack.wb_stack.size() == 0:
            return nullcontext()

        latest_method_call = wb_stack.wb_stack.get_latest_method_call()
        if latest_method_call is None:
            ret = method_call.MethodCall(method_name)
        else:
            ret = nullcontext()

        return ret


def enable_pf_pandas__():
    # ipdb.set_trace()
    pandas_flavor.register.method_call_ctx_factory = (
        PandasFlavorMethodCallFactory.create
    )

    old_DataFrame_init = pd.DataFrame.__init__

    def aux_init(func, *x, **y):
        # print("aux init")
        # ipdb.set_trace()
        ret = func(*x, **y)
        return ret

    pd.DataFrame.__init__ = lambda *x, **y: aux_init(
        old_DataFrame_init, *x, **y
    )

    if 1:
        old_getattr = pd.DataFrame.__getattr__
        pd.DataFrame.__getattr__ = lambda *x, **y: DataFrameFunc(
            "df-projection", old_getattr
        )(*x, *y)

    if 1:
        old_to_datetime = pd.to_datetime
        pd.to_datetime = lambda *x, **y: DataFrameFunc(
            "to_datetime", old_to_datetime
        )(*x, **y)

    if 1:
        # we need those registration of pin method to make sure method call syntax work
        # actual pin implementation is in MethodCall handle_* methods
        @pf.register_series_method
        def pin(s: pd.Series, output_type="head"):
            return s

        @pf.register_dataframe_method
        def pin(df: pd.DataFrame, output_type="head"):
            return df

    old_describe = pd.DataFrame.describe
    # del pd.DataFrame.describe

    @pf.register_dataframe_method
    def describe(df: pd.DataFrame) -> pd.DataFrame:
        print("override describe")
        return old_describe(df)

    old_dropna = pd.DataFrame.dropna
    del pd.DataFrame.dropna
    old_drop = pd.DataFrame.drop
    del pd.DataFrame.drop
    old_rename = pd.DataFrame.rename
    del pd.DataFrame.rename
    old_assign = pd.DataFrame.assign
    del pd.DataFrame.assign
    old_copy = pd.DataFrame.copy

    @pf.register_dataframe_method
    def dropna(df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        print("call dropna")
        ret = old_dropna(df, **kwargs)
        # print("my dropna", id(df), id(ret))
        return ret

    @pf.register_dataframe_method
    def drop(df: pd.DataFrame, *x, **y) -> pd.DataFrame:
        # ipdb.set_trace()
        ret = old_drop(df, *x, **y)
        # print("my drop", id(df), id(ret))
        return ret

    @pf.register_dataframe_method
    def rename(df: pd.DataFrame, columns) -> pd.DataFrame:
        print("my rename", id(df))
        # ipdb.set_trace()
        ret = old_rename(df, columns=columns)
        return ret

    @pf.register_dataframe_method
    def assign(df: pd.DataFrame, **kw) -> pd.DataFrame:
        ret = old_assign(df, **kw)
        # print("my assign", id(df), id(ret))
        return ret

    @pf.register_dataframe_method
    def copy(df: pd.DataFrame, *x, **y) -> pd.DataFrame:
        print("new copy:", x, y)
        ret = old_copy(df, *x, **y)
        return ret

    if 0:
        old_combine_first = pd.Series.combine_first

        @pf.register_series_method
        def combine_first(s: pd.Series, other) -> pd.Series:
            ret = old_combine_first(s, other)
            return ret

    if 0:
        old_apply = pd.Series.apply

        @pf.register_series_method
        def apply(s: pd.Series, func) -> pd.Series:
            ret = old_apply(s, func)
            return ret
