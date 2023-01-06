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
    with pyjviz.MethodsChain("c"):
        df0 = df.a0()
        df1 = df.assign(b = df.a)
        
    with pyjviz.MethodsChain("cc"):
        #df2 = df.assign(c = df.a, b = lambda x: x.c)
        df2 = df.assign(b = lambda x: x.a)

    #ipdb.set_trace()
    print(df.describe())

    pyjviz.render_rdflog(rdflog_fn, vertical = False, show_objects = True)
