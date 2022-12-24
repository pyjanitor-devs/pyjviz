import pyjviz
import fractions
import pandas as pd

fractions.Fraction.mult = lambda self, x: self * x

if __name__ == "__main__":
    f1 = fractions.Fraction(1, 2)
    f2 = fractions.Fraction(2, 3)

    res = f1.mult(f2)
    print(res)
    
    res = pyjviz.UWObject(f1).mult(pyjviz.UWObject(f2))
    print(res)

    df = pd.DataFrame({'a': range(10)}); df['b'] = 0
    res_df = pyjviz.tracking_store.set_tracking_obj_attr(pyjviz.UWObject(df), 'chain', 'c').drop('b', axis = 1, inplace = False).rename(columns = {'a': 'A'})
    print(res_df)

    print(id(df), id(res_df))
