import ipdb
import janitor
import pandas_flavor as pf
import pyjviz
import os.path, sys

import typing
import pandas as pd

TestDF = typing.NewType("TestDF", pd.DataFrame)
TestDF.columns = ["a"]


@pf.register_dataframe_method
def a0(df: pd.DataFrame) -> TestDF:
    print("a0")
    return pd.DataFrame(df)


@pf.register_dataframe_method
def a2(df: pd.DataFrame) -> TestDF:
    return df.a0().a0()


if __name__ == "__main__":
    print(TestDF, TestDF.__name__, TestDF.__supertype__)
    print(TestDF.columns)

    # ipdb.set_trace()
    with pyjviz.CB("c") as c:
        df = pd.DataFrame({"a": range(10)})
        df1 = df.a0()
    print(df1.describe())

    with c:
        df2 = df.a0()
    print(df2.describe())

    with pyjviz.CB("/c"):
        df3 = df.a0().a0()
    print(df3.describe())

    with pyjviz.CB("/cc") as cc:
        df4 = df.a0().a0().a2()
    print(df4.describe())

    with cc:
        df5 = df.a0().a0().a0().a2()
    print(df5.describe())

    pyjviz.save()
