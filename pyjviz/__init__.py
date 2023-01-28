from .rdflogging import *
from .fstriplestore import FSTripleOutputOneShot
from .call_stack_entries import *
from .viz import *

from .pf_pandas import enable_pf_pandas__

pyjviz_enabled = not ('PYJVIZ_DISABLED' in os.environ and os.environ.get('PYJVIZ_DISABLED').lower() in ['1', 'true','yes'])

if pyjviz_enabled:
    if os.path.basename(sys.argv[0]) == 'ipykernel_launcher.py':
        triple_store = FSTripleOutputOneShot(base_uri, None, None) # -- NB: how can we detect that this is notebook run
    else:
        triple_store = FSTripleOutputOneShot(base_uri, "pyjviz-test-output", os.path.basename(sys.argv[0]) + ".ttl")
    set_rdflogger__(RDFLogger(triple_store))
    enable_pf_pandas__()

