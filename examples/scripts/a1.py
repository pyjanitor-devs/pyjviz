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

@pf.register_dataframe_method
def a2(df: pd.DataFrame) -> TestDF:
    return df.a0().a0()

if __name__ == "__main__":
    # configure pyjrdf
    rdflog_fn = pyjviz.get_rdflog_filename(sys.argv[0])
    pyjviz.RDFLogger.init(rdflog_fn)

    print(TestDF, TestDF.__name__, TestDF.__supertype__)
    print(TestDF.columns)

    #ipdb.set_trace()
    with pyjviz.MethodsChain("c") as c:
        df = pyjviz.UWObject(pd.DataFrame({'a': range(10)}))
        df1 = df.a0()
    print(df1.describe())
        
    with c:
        df2 = df.a0()
    print(df2.describe())

    c1 = pyjviz.MethodsChain("c")
    df3 = df.continue_to(c1).a0()
    print(df3.describe())

    cc = pyjviz.MethodsChain("cc")
    df4 = df.continue_to(cc).a0().a0().a2()
    print(df4.describe())

    df5 = df.continue_to(cc).a0().a0().a2()#.return_to(c)
    print(df5.describe())
    
    pyjviz.render_rdflog(rdflog_fn)
