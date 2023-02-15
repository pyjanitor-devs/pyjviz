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


if __name__ == "__main__":
    print(TestDF, TestDF.__name__, TestDF.__supertype__)
    print(TestDF.columns)

    with pyjviz.CB("c") as c:
        df = pd.DataFrame({"a": range(10)})
        df1 = df.a0()
        df2 = df.a0()
        res1 = df2.a0()
        res2 = df2.a0()

    print(df1.describe())

    pyjviz.save_dot(show_objects=False)
