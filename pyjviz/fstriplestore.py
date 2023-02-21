import os
import os.path
import textwrap
import io
import rdflib

base_uri = "https://github.com/pyjanitor-devs/pyjviz/rdflog.shacl.ttl#"


class FSTripleOutput:
    def __init__(self, out_fd):
        global base_uri
        self.base_uri = base_uri
        self.out_fd = out_fd

    def dump_prefixes__(self):
        print(f"@base <{self.base_uri}> .", file=self.out_fd)
        print(
            "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .",
            file=self.out_fd,
        )
        print(
            "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .",
            file=self.out_fd,
        )

        print(
            textwrap.dedent(
                """
        <WithBlock> rdf:type rdfs:Class .
        <CodeBlock> rdf:type rdfs:Class .
        <CodeBlock> rdfs:subClassOf <WithBlock> .
        <MethodCall> rdf:type rdfs:Class .
        <MethodCall> rdfs:subClassOf <WithBlock> .
        <NestedCall> rdf:type rdfs:Class .

        <Obj> rdf:type rdfs:Class .
        <ObjState> rdf:type rdfs:Class .
        <ObjStateCC> rdf:type rdfs:Class .

        <CC> rdf:type rdfs:Class .
        <CCObjStateLabel> rdf:type rdfs:Class .
        <CCObjStateLabelDataFrame> rdf:type rdfs:Class; rdfs:subClassOf <CCObjStateLabel> .
        <CCObjStateLabelSeries> rdf:type rdfs:Class; rdfs:subClassOf <CCObjStateLabel> .
        <CCGlance> rdf:type rdfs:class; rdfs:subClassOf <CC> .
        <CCBasicPlot> rdf:type rdfs:Class; rdfs:subClassOf <CC> .
        """
            ),
            file=self.out_fd,
        )

    def dump_triple(self, subj, pred, obj):
        print(f"{subj} {pred} {obj} .", file=self.out_fd)

    def flush(self):
        self.out_fd.flush()


class FSTripleOutputOneShot(FSTripleOutput):
    def __init__(self, output_dir, output_filename):
        self.output_dir = output_dir
        self.output_fn = None

        if self.output_dir is None:
            out_fd = io.StringIO()
        else:
            # ipdb.set_trace()
            self.output_dir = os.path.expanduser(self.output_dir)
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)
                os.makedirs(os.path.join(self.output_dir, "tmp"))

            if output_filename:
                self.output_fn = os.path.join(self.output_dir, output_filename)
                out_fd = open(self.output_fn, "w+")

        super().__init__(out_fd)
        self.dump_prefixes__()

    def get_graph(self):
        g = rdflib.Graph()
        self.out_fd.seek(0)
        g.parse(self.out_fd)
        return g


class FSTripleOutputNull:
    def dump_triple(self, s, p, o):
        pass


triple_store = None


def set_triple_store__(o):
    print("setting up triple_store:", o)
    global triple_store
    triple_store = o
