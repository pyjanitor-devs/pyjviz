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

if __name__ == "__main__":
    # configure pyjviz
    rdflog_fn = pyjviz.get_rdflog_filename(sys.argv[0])
    pyjviz.RDFLogger.init(rdflog_fn)

    print(TestDF, TestDF.__name__, TestDF.__supertype__)
    print(TestDF.columns)

    #ipdb.set_trace()
    with pyjviz.Chain("c") as c:
        df = pyjviz.UWObject(pd.DataFrame({'a': range(10)}))
        df1 = df.a0()
        df2 = df.pin(c).a0()
        #df2 = df.a0()
        res1 = df2.a0()
        res2 = df2.a0()

    print(df1.describe())

    pyjviz.render_rdflog(rdflog_fn)
