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
    #return pd.DataFrame(df)
    #ret = df.shift()
    ret = df; ret['a'] += 1
    if 'b' in ret.columns:
        ret = ret.drop('b', axis = 1, inplace = False)
    return ret
    
if __name__ == "__main__":
    print(TestDF, TestDF.__name__, TestDF.__supertype__)
    print(TestDF.columns)

    if 1:
        # NB: fix bug when projection is used
        df = pd.DataFrame({'a': range(10)})
        df['b'] = df.a
    else:
        df = pd.DataFrame({'a': range(10), 'b': range(10)})
        
    #ipdb.set_trace()
    with pyjviz.CB("c"):
        df0 = df.a0()
        df1 = df.a0().a0()
        df2 = df.a0()

    #ipdb.set_trace()
    print(df1.describe())

    pyjviz.save_dot(vertical = False, show_objects = True)
