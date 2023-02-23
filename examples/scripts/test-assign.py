# import ipdb
import inspect, dis
import janitor
import pandas_flavor as pf
import pyjviz
import os.path, sys

import typing
import pandas as pd


@pf.register_dataframe_method
def a0(df: pd.DataFrame) -> pd.DataFrame:
    print("a0")
    return pd.DataFrame(df)
    #return df


def test_f(x):
    # print(x)
    # print(id(x))
    # curr_frame = inspect.currentframe()
    # print(dis.dis(curr_frame.f_code))
    # print(curr_frame.f_code.co_varnames)
    # collect_ids = set([id(curr_frame.f_locals.get(i)) for i in curr_frame.f_code.co_varnames])
    # print(collect_ids)
    # print([curr_frame.f_locals.get(i) for i in collect_ids])
    return x.a


if __name__ == "__main__":
    df = pd.DataFrame({"a": range(10)})

    # ipdb.set_trace()
    if 0:
        with pyjviz.MethodsChain("c"):
            df0 = df.a0()
            df1 = df.assign(b=df.a)

    def test_func(x):
        # ipdb.set_trace()
        return x.a + x.a

    # A = df.a
    if 1:
        with pyjviz.CB("c1") as cc:
            df2 = df.assign(c=df.a)
            # df2 = df.assign(c = df.a, cc = lambda x: x.a)
            # df2 = df.assign(c = df.a, b = lambda x: x.c, bb = lambda x: x.a + x.b + x.c, d = lambda x: x.a)
            # df2 = df.assign(c = df.a, b = test_func)
            # df2 = df.assign(b = lambda x: x.a, c = lambda x: x.b)

    if 1:
        with pyjviz.CB("c2") as cc:
            aux_df = pd.DataFrame({"b": range(5)}).a0()
            df2 = df.assign(c=lambda x: x.a + aux_df.shape[0])

            # df2 = df.assign(c = test_f)
            # df2 = df.assign(c = df.a, cc = lambda x: x.a)
            # df2 = df.assign(c = df.a, b = lambda x: x.c, bb = lambda x: x.a + x.b + x.c, d = lambda x: x.a)
            # df2 = df.assign(c = df.a, b = test_func)
            # df2 = df.assign(b = lambda x: x.a, c = lambda x: x.b)

    print(df.describe())

    # ipdb.set_trace()
    pyjviz.save_dot(vertical=True, show_objects=False)
