# using https://stackoverflow.com/a/55266233/1181482 as starting point

from setuptools import setup, find_packages

setup(
    name="pyjviz",
    version="0.0",
    packages=find_packages(),
    install_requires=[
        "pandas-flavor >= 0.5.0",
        "rdflib",
        "graphviz",
        "bs4",
        "lxml",
        "plotly",
        "kaleido",
    ],
)
