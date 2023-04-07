import ipdb
import janitor
import pandas_flavor as pf
import pyjviz
import os.path, sys

import typing
import pandas as pd


@pf.register_dataframe_method
def shift1(df: pd.DataFrame) -> pd.DataFrame:
    df = df.shift(axis=0, fill_value=0)
    # return pd.DataFrame(res_df)
    return df


if __name__ == "__main__":
    df = pd.DataFrame({"a0": range(10)})
    if 0:
        for i in range(1, 5):
            col = f"a{i}"
            df[col] = df.a0

    # ipdb.set_trace()
    with pyjviz.CB("c") as c:
        df0 = df.shift1()
        df1 = df.shift1().shift1()
        df2 = df.shift1()

    # ipdb.set_trace()
    print(df1.describe())

    pyjviz.save(vertical=False, show_objects=True)
