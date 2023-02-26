"""
a0.py - basic unit test, nothing else and more
"""

# import ipdb
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
    """
    test test test 123
    """
    # ipdb.set_trace()
    print("a0")
    return pd.DataFrame(df)
    #return df


if __name__ == "__main__":
    print(TestDF, TestDF.__name__, TestDF.__supertype__)
    print(TestDF.columns)

    df = pd.DataFrame({"a": range(10)})

    with pyjviz.CB("c") as C:
        df0 = df.a0()
        df1 = df.a0().a0()
        df2 = df.a0()

    # ipdb.set_trace()
    print(df1.describe())

    pyjviz.save_dot(show_objects=True, popup_output = True)
    #pyjviz.save_dot(show_objects=True, popup_output = False)
