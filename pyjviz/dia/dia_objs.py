"""
diag_obj.py and diag_obj_rdf.py define base classes to be used to implement python obejct RDF representation logic.
Let's consider example of class [Text](/pyjviz/api/test/#pyjviz.dia_objs.Text). Text is class of visible objects which we should be able to represented as RDF.

[text_class_doc]: /pyjviz/api/test/#pyjviz.dia_objs.Text

TextRDF is the class which defines method [dump_rdf()](/pyjviz/user_guide/#about-dump_rdf-and-related-methods) which suppose to produce RDF triples correspnonding to Text obj.
    ```mermaid
    classDiagram
    RDFRep <|-- TextRDF
    DiagramObject <|-- Text
    Text --> TextRDF:back
    TextRDF --> Text:front
    class RDFRep {
    + front
    + uri
    + rdf_type_uri
    }
    class DiagramObject {
    + back
    }
    class Text {
    + title
    + text
    }
    class TextRDF {
    + dump_rdf()
    }
    ```
"""  # noqa : 501
from . import wb_stack
from ..rdf import dia_objs_rdf


class DiagramObj:
    """
    base class of python objects which will have visible diagram representation.
    The diagram object has corresponding <b>back</b> object which class belongs to RDFRep.
    E.g. Text class will have back ref to TextRDF class object.
    """  # noqa : 501

    def __init__(self):
        self.back = None


class Text(DiagramObj):
    """
    Text class is to represent text box primitive for pyjviz diagram.
    """

    def __init__(self, title, text, parent_obj=None):
        if not parent_obj:
            parent_obj = wb_stack.wb_stack.get_top()

        if not isinstance(parent_obj, DiagramObj):
            msg = (
                f"parent_obj is not subclass of DiagramObj, {type(parent_obj)}"
            )
            raise Exception(msg)

        self.back = TextRDF(self)
        self.parent_obj = parent_obj
        self.title = title
        self.text = text
