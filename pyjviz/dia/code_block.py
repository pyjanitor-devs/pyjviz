from ..rdf import code_block_rdf
from . import wb_stack


class CodeBlock(wb_stack.WithBlock):
    """
    CodeBlock (also has name alias CB) is diagram object representing code block defined via *with* statement.
    ```python
    with pyjviz.CB("test-code"):
       .. python code is here ..

    ```
    """  # noqa : 501

    def __init__(self, label=None):
        super().__init__(label)
        self.back = code_block_rdf.CodeBlockRDF(self)

        self.back.dump_rdf()

    def on_exit__(self):
        self.back.flush_triples()


CB = CodeBlock
