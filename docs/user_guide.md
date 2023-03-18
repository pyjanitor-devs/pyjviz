# User Guide

## about dump_rdf() and related methods

*dump_rdf* or similarly named methods suppose to produce RDF triples which represent python object accessible via *front* obj ref.
E.g. having diagram object of class Text implies you have also TextRDF object. Text object has attributes *title* and *text*.
If *TextRDF.dump_rdf* method is called we will have following RDF triples in triplestore:

```
<Text#1> rdf:type <Text> .
<Text#1> <title> "Hello, world!" .
<Text#1> <text> "This is a test of Text" .
```

## Examples

### Why janitor?

examples.scripts.why-janitor

### Conditional Join

conditional-join-w-cmp.ipynb

### Glutten sensitivity

from Think Bayes 2, ch 6
