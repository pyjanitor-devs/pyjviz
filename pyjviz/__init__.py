from .fstriplestore import set_triple_store__, FSTripleOutputOneShot
from .wb_stack import get_wb_stack
from .wb_stack_entries import *
from .obj_utils import *
from .viz import *
from .rdf_node import arrow

from .pf_pandas import enable_pf_pandas__

pyjviz_enabled = not ('PYJVIZ_DISABLED' in os.environ and os.environ.get('PYJVIZ_DISABLED').lower() in ['1', 'true','yes'])

if pyjviz_enabled:
    if os.path.basename(sys.argv[0]) == 'ipykernel_launcher.py':
        tstr = FSTripleOutputOneShot(None, None) # -- NB: how can we detect that this is notebook run
    else:        
        pyjviz_output_dir = os.environ.get('PYJVIZ_OUTPUT_DIR') if 'PYJVIZ_OUTPUT_DIR' in os.environ else "~/.pyjviz"            
        pyjviz_output_dir = os.path.expanduser(pyjviz_output_dir)
        tstr = FSTripleOutputOneShot(pyjviz_output_dir,
                                     os.path.basename(sys.argv[0]) + ".ttl")

    set_triple_store__(tstr)
    enable_pf_pandas__()

