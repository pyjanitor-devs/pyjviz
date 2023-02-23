from . import code_block_rdf
from . import wb_stack

class CodeBlock(wb_stack.WithBlock):
    def __init__(self, label = None):
        super().__init__(label)
        self.back = code_block_rdf.CodeBlockRDF(self)
        self.back.to_rdf()

    def on_exit__(self):
        self.back.flush_triples()
        
CB = CodeBlock
