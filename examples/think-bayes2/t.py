import pandas as pd
import numpy as np
from scipy.stats import poisson
import pandas_flavor as pf
import pyjviz

from empiricaldist import Pmf

if __name__ == "__main__":
    with pyjviz.CB() as cb:
        d6 = Pmf.from_seq([1, 2, 3, 4, 5, 6])
        d6.pin()

        lam = 1.4
        qs = np.arange(10)
        ps = poisson(lam).pmf(qs)
        d_poison = Pmf(ps, qs)
        d_poison.pin()

        #pyjviz.arrow(d6, "goes to", d_poison)

    pyjviz.save_dot()
