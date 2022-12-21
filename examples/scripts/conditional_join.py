#
# example https://github.com/pyjanitor-devs/pyjanitor/blob/dev/examples/notebooks/conditional_join.ipynb
#
import sys
import pandas as pd
import janitor, pyjviz

if __name__ == "__main__":
    # configure pyjviz
    rdflog_fn = pyjviz.get_rdflog_filename(sys.argv[0])
    pyjviz.RDFLogger.init(rdflog_fn)

    df1 = pd.DataFrame({'id': [1,1,1,2,2,3],
                        'value_1': [2,5,7,1,3,4]})

    df2 = pd.DataFrame({'id': [1,1,1,1,2,2,2,3],
                        'value_2A': [0,3,7,12,0,2,3,1],
                        'value_2B': [1,5,9,15,1,4,6,3]})

    with pyjviz.Chain("c1") as c1:
        res1 = c1.pin(df1).conditional_join(df2,
                                             ('id', 'id', "<"),
                                             df_columns = {'id':'df_id'},
                                             right_columns = {'id':'right_id'}
                                             )
        res2 = c1.pin(df1).describe()  
    print(res1)
    res1.describe()

    with c1:
        with pyjviz.Chain("c2", c1) as c2:
            res2 = c1.pin(df1).select_columns('value_1').conditional_join(
                c2.pin(df2).select_columns('val*'), # someday soon this line should work - df2.pin(c2).select_columns('val*'),
                ('value_1', 'value_2A', '>'),
                ('value_1', 'value_2B', '<'),
            )
            
    print(res2)
    res2.describe()

    pyjviz.render_rdflog(rdflog_fn)
