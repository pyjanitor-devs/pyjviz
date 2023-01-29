import ipdb
import janitor
import pandas_flavor as pf
import pyjviz
import os.path, sys

import typing
import pandas as pd

TestDF = typing.NewType('TestDF', pd.DataFrame)
TestDF.columns = ['a']

@pf.register_dataframe_method
def a0(df: pd.DataFrame) -> TestDF:
    print("a0")
    return pd.DataFrame(df)
    #return df

if __name__ == "__main__":
    print(TestDF, TestDF.__name__, TestDF.__supertype__)
    print(TestDF.columns)

    df = pd.DataFrame({'a': range(10)})

    #ipdb.set_trace()

    #df.obj_chain_path = "c"
    #pyjviz.curr_methods_chain_path = "c"
    with pyjviz.CB("c"):
        df0 = df.a0()
        df1 = df.a0().a0()
        df2 = df.a0()
        
    #df.obj_chain_path = None
    print(df.describe())
    
    #df1.obj_chain_path = None
    print(df1.describe())

    pyjviz.save_dot()
