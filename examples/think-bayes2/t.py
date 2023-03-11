import pandas as pd
import numpy as np
from scipy.stats import poisson
import pandas_flavor as pf
import pyjviz

from empiricaldist import Pmf

if __name__ == "__main__":
    with pyjviz.CB() as cb:
        d6 = Pmf.from_seq([1, 2, 3, 4, 5, 6])
        d6.make_plot()

        lam = 1.4
        qs = np.arange(10)
        ps = poisson(lam).pmf(qs)
        d_poison = Pmf(ps, qs)
        d_poison.make_plot()
        
        #pyjviz.Arrow(d6, d_poison, label = "goes to")

        #t = pyjviz.Text("test", "test")


    pyjviz.save_dot()
