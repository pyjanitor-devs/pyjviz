import os
import sys
from .fstriplestore import set_triple_store__, FSTripleOutputOneShot
from .pf_pandas import enable_pf_pandas__
from .code_block import CodeBlock, CB
from .dia_objs import Text
from .viz import save_dot, show

pyjviz_enabled = not (
    "PYJVIZ_DISABLED" in os.environ
    and os.environ.get("PYJVIZ_DISABLED").lower() in ["1", "true", "yes"]
)

if pyjviz_enabled:
    if os.path.basename(sys.argv[0]) == "ipykernel_launcher.py":
        tstr = FSTripleOutputOneShot(
            None, None
        )  # -- NB: how can we detect that this is notebook run

        from .nb_utils import register_pre_run, get_cell_id
        
        def pre_run_cell():
            print("pre_run_cell: This function will be called before every cell is executed.")
            print("cell_id:", get_cell_id())

        dummy_reg_pre_run = register_pre_run(pre_run_cell)
        pre_run_cell()
    else:
        pyjviz_output_dir = os.environ.get("PYJVIZ_OUTPUT_DIR", "~/.pyjviz")
        pyjviz_output_dir = os.path.expanduser(pyjviz_output_dir)
        tstr = FSTripleOutputOneShot(
            pyjviz_output_dir, os.path.basename(sys.argv[0]) + ".ttl"
        )

    set_triple_store__(tstr)
    enable_pf_pandas__()
