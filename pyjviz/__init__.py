import os
import sys
from .rdf.fstriplestore import set_triple_store__, FSTripleOutputOneShot
from .pf_pandas import enable_pf_pandas__
from .dia.code_block import CodeBlock, CB
from .dia.dia_objs import Text
from .graphviz.viz import save_dot, show

pyjviz_enabled = not (
    "PYJVIZ_DISABLED" in os.environ
    and os.environ.get("PYJVIZ_DISABLED").lower() in ["1", "true", "yes"]
)

if pyjviz_enabled:
    if os.path.basename(sys.argv[0]) == "ipykernel_launcher.py":
        from .graphviz.nb_utils import (
            register_pre_run,
            get_cell_id,
            cell_triplestores_d,
        )

        def pre_run_cell():
            curr_cell_id = get_cell_id()
            # print("pre_run_cell: cell_id:", curr_cell_id)
            if not curr_cell_id in cell_triplestores_d:
                cell_triplestores_d[curr_cell_id] = FSTripleOutputOneShot(
                    None, None
                )
            ts = cell_triplestores_d.get(curr_cell_id)
            ts.clear()
            set_triple_store__(ts)

        pre_run_cell()
        dummy_reg_pre_run = register_pre_run(pre_run_cell)
    else:
        pyjviz_output_dir = os.environ.get("PYJVIZ_OUTPUT_DIR", "~/.pyjviz")
        pyjviz_output_dir = os.path.expanduser(pyjviz_output_dir)
        tstr = FSTripleOutputOneShot(
            pyjviz_output_dir, os.path.basename(sys.argv[0]) + ".ttl"
        )
        set_triple_store__(tstr)

    enable_pf_pandas__()
