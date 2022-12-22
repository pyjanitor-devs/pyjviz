import threading
import janitor
import pandas as pd
import pandas_flavor as pf
import pyjviz
import os.path, sys

class CustomThread(threading.Thread):
    def __init__(self, t_func):
        threading.Thread.__init__(self)
        self.t_func = t_func
        self.value = None

    # function executed in a new thread
    def run(self):
        self.value = self.t_func()

def prun(t_func):
    t = CustomThread(t_func)
    t.start()
    return t

def pwait(t):
    t.join()
    t_ret = t.value
    return t_ret

@pf.register_dataframe_method
def m(df, l_df, r_df):
    print("df:", df.shape)
    print("l_df:", l_df.shape)
    print("r_df:", r_df.shape)
    return df

@pf.register_dataframe_method
def x(df):
    print("x:", df.shape)
    return df

@pf.register_dataframe_method
def y(df, int_arg):
    print("y:", df.shape, int_arg)
    return df

if __name__ == "__main__":
    # configure pyjviz
    rdflog_fn = pyjviz.get_rdflog_filename(sys.argv[0])
    pyjviz.RDFLogger.init(rdflog_fn)
    
    print("Main Thread Here!!")

    df = pd.DataFrame({'a': range(10)})
    
    with pyjviz.Chain("c") as c:
        r1 = c.pin(df).x()
        r20 = prun(lambda: c.pin(df).y(0))
        r21 = prun(lambda: c.pin(df).y(1))
        res = r1.m(pwait(r20), pwait(r21))
    
    pyjviz.render_rdflog(rdflog_fn)
