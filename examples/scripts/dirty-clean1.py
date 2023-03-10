#
# first example from https://github.com/samukweku/pyjanitor_presentation/blob/main/janitor/pyjanitor_PyData_Sydney.ipynb
#

import sys
import pandas as pd
import janitor
import pyjviz

if __name__ == "__main__":
    if 1:
        url = "https://github.com/pyjanitor-devs/pyjanitor/blob/dev/examples/notebooks/dirty_data.xlsx?raw=true"
        dirty = pd.read_excel(url, engine="openpyxl")
    else:
        dirty = pd.read_excel("../data/dirty_data.xlsx")

    print(dirty)

    with pyjviz.CB("from_dirty_to_clean") as c:
        clean = (
            dirty.clean_names()
            .dropna(axis="columns", how="all")
            .dropna(axis="rows", how="all")
            .rename(
                columns={
                    "%_allocated": "percent_allocated",
                    "full_time_": "full_time",
                }
            )
            .assign(
                certification=lambda df: df.certification.combine_first(
                    df.certification_1
                )
            )
            .drop(columns="certification_1")
        )
        clean = clean.assign(
            hire_date1=clean.hire_date
        )  # , hire_date = pd.to_datetime(clean.hire_date, unit='D', origin='1899-12-30'))

    print(clean)

    pyjviz.save_dot(vertical=True, show_objects=False)
