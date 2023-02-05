#
# example https://github.com/pyjanitor-devs/pyjanitor/blob/dev/examples/notebooks/conditional_join.ipynb
#
import ipdb
import sys
import pandas as pd
import janitor, pyjviz
import pandas_flavor as pf
import io, base64

wb_stack = pyjviz.wb_stack
fstriplestore = pyjviz.fstriplestore

old_plot = pd.DataFrame.plot
@pf.register_dataframe_method
def plot2(df, title = None):
    out_fd = io.BytesIO()
    fig = df.plot().get_figure()
    fig.savefig(out_fd)

    im_s = base64.b64encode(out_fd.getvalue()).decode('ascii')
    #ipdb.set_trace()
    #curr_n, _ = obj_tracking.tracking_store.get_tracking_obj(df)
    curr_n = wb_stack.wb_stack.get_top().uri
    parent_n = wb_stack.wb_stack.get_parent_of_current_entry().uri
    fstriplestore.triple_store.dump_triple(curr_n, 'rdf:type', "<ShowObj>")
    fstriplestore.triple_store.dump_triple(curr_n, '<part-of>', parent_n)
    fstriplestore.triple_store.dump_triple(curr_n, '<df-plot-im>', '"' + im_s + '"')
    
    return df

if __name__ == "__main__":
    df1 = pd.DataFrame({'id': [1,1,1,2,2,3],
                        'value_1': [2,5,7,1,3,4]})
    df2 = pd.DataFrame({'id': [1,1,1,1,2,2,2,3],
                        'value_2A': [0,3,7,12,0,2,3,1],
                        'value_2B': [1,5,9,15,1,4,6,3]})

    with pyjviz.CB("top") as top:
        with pyjviz.CB("c1") as c1:
            res1 = df1.conditional_join(df2,
                                        ('id', 'id', "<"),
                                        df_columns = {'id':'df_id'},
                                        right_columns = {'id':'right_id'}
                                        )
            res1.plot2('res1')
            
    res2 = df1.describe()
    print(res1)
    res1.describe()

    with top:
        with pyjviz.CB("c2"):        
            #ipdb.set_trace()
            res2 = df1.select_columns('value_1').conditional_join(
                df2.select_columns('val*'),
                ('value_1', 'value_2A', '>'),
                ('value_1', 'value_2B', '<'),
            ).plot2('res2')

    print(res2)
    res2.describe()

    pyjviz.save_dot(vertical = True, show_objects = False)
