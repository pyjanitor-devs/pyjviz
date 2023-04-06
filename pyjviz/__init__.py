import os
import sys
from .rdf.fstriplestore import set_triple_store__, FSTripleOutputOneShot
from .pf_pandas import enable_pf_pandas__
from .dia.code_block import CodeBlock, CB
from .dia.dia_objs import Text
from .dia.arrow import Arrow
from .graphviz.viz import save_dot, show
from .graphviz.viz_utils import set_is_nb_run

pyjviz_enabled = not (
    "PYJVIZ_DISABLED" in os.environ
    and os.environ.get("PYJVIZ_DISABLED").lower() in ["1", "true", "yes"]
)

if pyjviz_enabled:
    if os.path.basename(sys.argv[0]) == "ipykernel_launcher.py":
        set_is_nb_run(True)
        ts = FSTripleOutputOneShot(None, None)
        set_triple_store__(ts)
    else:
        pyjviz_output_dir = os.environ.get("PYJVIZ_OUTPUT_DIR", "~/.pyjviz")
        pyjviz_output_dir = os.path.expanduser(pyjviz_output_dir)
        tstr = FSTripleOutputOneShot(
            pyjviz_output_dir, os.path.basename(sys.argv[0]) + ".ttl"
        )
        set_triple_store__(tstr)

    enable_pf_pandas__()
