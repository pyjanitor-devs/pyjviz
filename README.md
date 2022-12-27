# pyjviz
visualization of pyjanitor method chains

to run examples install pyjanitor, rdflib and graphviz. After that you can install pyjviz:

```
pip install pyjanitor rdflib graphviz
cd $PYJVIZ_HOME
pip install -e .
cd examples/scripts
python a0.py
```

Resulting logs are in ~/.pyjviz/rdflog - visualized output stored in .png files.

pyjviz visualization of pyjanitor method pipes (or chains) is based on dumping of RDF log of pyjanitor method calls into rdf log file. Resulting RDF log file contains graph of method calls where user could trace method execution as well as user-defined data useful for visual inspection. Note that visualisation of pyjviz RDF log is not a main goal of provided package. Graphviz visualization avaiable in the package is rather reference implementation with quite limited capablities. However RDF structure defined in rdflog.shacl.ttl could be used by SPARQL processor for visualization and other tasks.

Obj is representation of pyjanitor object like pandas DataFrame. However input args are not objects rather object states. The state of object is represeneted by RDF class ObjState. The idea to separate object and object state is introduced to enable pyjviz to visualize situation when object has mutliple states used in method chain due to in-place operations. Such practice is discouraged by most of data packages but still may be used. In most cases where object has only state defined when object is created there is not difference betwen object and object state since there is one-to-one correspondence (isomorfism). So in some context below refernce to an object may imply object state instead.

pyjviz also introduce MethodCall RDF class. It represents pyjanitor method call. MethodCall object has incoming links from input objects and outgoing link an object representing retirn object.

Aslo pyjviz introduces python class Chain. Chain is set of sequences of pyjanitor method calls grouped together. pyjantitor method calls are represented by RDF class MethodCall. Each MethodCall has one or more input objects and one return object. In pyjviz input args and return are presented by RDF class ObjState. Each ObjState has reference to RDF class Obj.

