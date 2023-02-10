# pyjviz

`pyjviz` is Python package to visual support of programmers and data engeneers efforts using `pyjanitor` package.
`pyjviz` provides simple way to see method call chains flow and intermidiate results.

## Quick start

to run examples install pyjanitor, rdflib and graphviz. After that you can install pyjviz:

```
pip install pyjanitor rdflib graphviz
cd $PYJVIZ_HOME
pip install -e .
cd examples/scripts
python a0.py
```

Resulting logs are in ~/.pyjviz/rdflog - visualized output stored in .svg files.

## How pyjviz helps pyjanitor users?

Consider pyjanitor example why-janitor.py. Modified version is given below (also avaliable here):

```python
import numpy as np
import pandas as pd
import janitor
import pyjviz

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

with pyjviz.CB() as sg:
    df = (
          pd.DataFrame.from_dict(company_sales)
		      .remove_columns(["Company1"])
		      .dropna(subset=["Company2", "Company3"])
		      .rename_column("Company2", "Amazon")
		      .rename_column("Company3", "Facebook")
		      .add_column("Google", [450.0, 550.0, 800.0])
         )

# Output looks like this:
# Out[15]:
#   SalesMonth  Amazon  Facebook  Google
# 0        Jan   180.0     400.0   450.0
# 1        Feb   250.0     500.0   550.0
# 3      April   500.0     675.0   800.0

# comment line below to fix spurious apply calls caused by pandas printing implementation
print(df)

pyjviz.save_dot(vertical = True)
```

The besides usual output to stdout the code will produce this SVG file.
pyjviz visualization of pyjanitor method pipes (or chains) is based on dumping of RDF log of pyjanitor method calls into rdf log file. Resulting RDF log file contains graph of method calls where user could trace method execution as well as user-defined data useful for visual inspection. Note that visualisation of pyjviz RDF log is not a main goal of provided package. Graphviz visualization avaiable in the package is rather reference implementation with quite limited capablities. However RDF structure defined in rdflog.shacl.ttl could be used by SPARQL processor for visualization and other tasks.

Obj is representation of pyjanitor object like pandas DataFrame. However input args are not objects rather object states. The state of object is represeneted by RDF class ObjState. The idea to separate object and object state is introduced to enable pyjviz to visualize situation when object has mutliple states used in method chain due to in-place operations. Such practice is discouraged by most of data packages but still may be used. In most cases where object has only state defined when object is created there is not difference betwen object and object state since there is one-to-one correspondence (isomorfism). So in some context below refernce to an object may imply object state instead.

pyjviz also introduce MethodCall RDF class. It represents pyjanitor method call. MethodCall object has incoming links from input objects and outgoing link an object representing retirn object.

Aslo pyjviz introduces python class MethodsChain. MethodsChain is set of sequences of pyjanitor method calls grouped together. pyjantitor method calls are represented by RDF class MethodCall. Each MethodCall has one or more input objects and one return object. In pyjviz input args and return are presented by RDF class ObjState. Each ObjState has reference to RDF class Obj.

