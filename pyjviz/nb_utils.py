import warnings
import graphviz
from bs4 import BeautifulSoup
from IPython.display import display, HTML
from IPython import get_ipython
from IPython.core.events import pre_run_cell

from . import viz_nodes

warnings.filterwarnings("ignore", category=DeprecationWarning)


def replace_a_href_with_onclick(output):
    soup = BeautifulSoup(output, features="xml")

    for a_tag in soup.find_all('a'):
        on_click_code = a_tag.attrs.get('xlink:href')
        on_click_code = on_click_code.replace('javascript:', '')
        # NB: really bad way to do string replacement,
        # quadratic complexity for overall code execution
        for k, v in viz_nodes.big_strings_table.items():
            on_click_code = on_click_code.replace(f'%%{k}%%', v)
        a_tag.parent.attrs['onclick'] = on_click_code
        a_tag.parent.attrs['cursor'] = 'pointer'
        del a_tag.attrs['xlink:href']
        del a_tag.attrs['xlink:title']

    for a_tag in soup.find_all('a'):
        p_tag = a_tag.parent
        for c in a_tag.find_all():
            p_tag.insert(-1, c)
        a_tag.decompose()

    # Print the modified HTML output
    return soup.prettify()

def get_cell_id():
    cell_id = get_ipython().parent_header.get('metadata').get('cellId')
    return cell_id

def register_pre_run(my_pre_run_cell):
    print("register_pre_run")
    get_ipython().events.register('pre_run_cell', my_pre_run_cell)
    return None

def show_method_chain(dot_code):
    gvz = graphviz.Source(dot_code)

    output = gvz.pipe(engine='dot', format='svg').decode('ascii')
    mod_output = replace_a_href_with_onclick(output)
    display(HTML(mod_output))

