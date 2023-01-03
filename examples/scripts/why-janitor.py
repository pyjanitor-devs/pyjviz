# using example from https://pyjanitor-devs.github.io/pyjanitor/#why-janitor as base

import numpy as np
import pandas as pd
import janitor
import pyjviz, sys

# configure pyjviz
rdflog_fn = pyjviz.get_rdflog_filename(sys.argv[0])
pyjviz.RDFLogger.init(rdflog_fn)

# Sample Data curated for this example
company_sales = {
        'SalesMonth': ['Jan', 'Feb', 'Mar', 'April'],
        'Company1': [150.0, 200.0, 300.0, 400.0],
        'Company2': [180.0, 250.0, np.nan, 500.0],
        'Company3': [400.0, 500.0, 600.0, 675.0]
    }

print(pd.DataFrame.from_dict(company_sales))
#  SalesMonth  Company1  Company2  Company3
#  0        Jan     150.0     180.0     400.0
#  1        Feb     200.0     250.0     500.0
#  2        Mar     300.0       NaN     600.0
#  3      April     400.0     500.0     675.0

with pyjviz.MethodsChain():
    df = (
        pd.DataFrame.from_dict(company_sales)
        .remove_columns(["Company1"])
        #.set_chain("most-cleaning")
        .dropna(subset=["Company2", "Company3"])
        .rename_column("Company2", "Amazon")
        .rename_column("Company3", "Facebook")
        #.reset_chain()
        .add_column("Google", [450.0, 550.0, 800.0])
    )
    
    # Output looks like this:
    # Out[15]:
    #   SalesMonth  Amazon  Facebook  Google
    # 0        Jan   180.0     400.0   450.0
    # 1        Feb   250.0     500.0   550.0
    # 3      April   500.0     675.0   800.0

    print(df)

pyjviz.render_rdflog(rdflog_fn)
