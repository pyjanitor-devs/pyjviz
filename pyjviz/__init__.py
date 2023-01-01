from .uw import *
from .pf_pandas import enable_pf_pandas__, pf_pandas_can_handle_the_obj
from .rdflogging import *
from .methods_chain import *
from .viz import *

pyjviz_use_custom_pf = 'PYJVIZ_USE_CUSTOM_PF' in os.environ and os.environ.get('PYJVIZ_USE_CUSTOM_PF').lower() in ['1', 'true','yes']

if pyjviz_use_custom_pf:
    print('enable pf_pandas methods handling')
    enable_pf_pandas__()
else:
    print('use UW for all objects')
    
