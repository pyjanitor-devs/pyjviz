import ipdb
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

if __name__ == "__main__":
    # configure pyjviz
    rdflog_fn = pyjviz.get_rdflog_filename(sys.argv[0])
    pyjviz.RDFLogger.init(rdflog_fn)
        
    df = pd.DataFrame({'a': range(10)})

    #ipdb.set_trace()
    if 0:
        with pyjviz.MethodsChain("c"):
            df0 = df.a0()
            df1 = df.assign(b = df.a)

    def test_func(x):
        #ipdb.set_trace()
        return x.a + x.a

    #A = df.a
    with pyjviz.MethodsChain("cc"):
        df2 = df.assign(c = lambda x: x.a)
        #df2 = df.assign(c = df.a)
        #df2 = df.assign(c = df.a, cc = lambda x: x.a)
        #df2 = df.assign(c = df.a, b = lambda x: x.c, bb = lambda x: x.a + x.b + x.c, d = lambda x: x.a)
        #df2 = df.assign(c = df.a, b = test_func)
        #df2 = df.assign(b = lambda x: x.a, c = lambda x: x.b)

    #ipdb.set_trace()
    print(df.describe())

    pyjviz.render_rdflog(rdflog_fn, vertical = True, show_objects = True)
