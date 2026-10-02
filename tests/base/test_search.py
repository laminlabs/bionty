import pandas as pd
import pytest
from bionty.base._public_ontology import search


@pytest.fixture(scope="module")
def df():
    records = [
        {
            "ontology_id": "CL:0000084",
            "name": "T cell",
            "synonyms": "T-cell|T lymphocyte|T-lymphocyte",
            "description": "A Type Of Lymphocyte Whose Defining Characteristic Is The Expression Of A T Cell Receptor Complex.",
            "children": ["CL:0000798", "CL:0002420", "CL:0002419", "CL:0000789"],
        },
        {
            "ontology_id": "CL:0000236",
            "name": "B cell",
            "synonyms": "B lymphocyte|B-lymphocyte|B-cell",
            "description": "A Lymphocyte Of B Lineage That Is Capable Of B Cell Mediated Immunity.",
            "children": ["CL:0009114", "CL:0001201"],
        },
        {
            "ontology_id": "CL:0000696",
            "name": "PP cell",
            "synonyms": "type F enteroendocrine cell",
            "description": "A Cell That Stores And Secretes Pancreatic Polypeptide Hormone.",
            "children": ["CL:0002680"],
        },
        {
            "ontology_id": "CL:0002072",
            "name": "nodal myocyte",
            "synonyms": "cardiac pacemaker cell|myocytus nodalis|P cell",
            "description": "A Specialized Cardiac Myocyte In The Sinoatrial And Atrioventricular Nodes. The Cell Is Slender And Fusiform Confined To The Nodal Center, Circumferentially Arranged Around The Nodal Artery.",
            "children": ["CL:1000409", "CL:1000410"],
        },
        {
            "ontology_id": "",
            "name": "cat[*_*]",
            "synonyms": "",
            "description": "",
            "children": [],
        },
    ]
    return pd.DataFrame.from_records(records)


# these tests also check ranks of the searches values (res["rank"] below)
# this is needed to perform cross-check with lamindb search
# to recompute the ranks via lamindb
# change .alias to .annotate in lamindb/_record.py def _search(...)
# then run the code below in an empty instance with bionty schema
# import lamindb as ln
# import bionty as bt
# cts = ["CL:0000084", "CL:0000236", "CL:0000696", "CL:0002072"]
# ln.save([bt.CellType.from_source(ontology_id=oid) for oid in cts])
# results = bt.CellType.search("P cell")
# print([(result.name, result.rank) for result in results.list()])
# results = bt.CellType.search("b cell")
# print([(result.name, result.rank) for result in results.list()])
# results = bt.CellType.search("type F enteroendocrine", field="synonyms")
# print([(result.name, result.rank) for result in results.list()])


def test_search_general(df):
    res = search(df=df, string="P cell", _show_rank=True)
    assert res.iloc[0]["name"] == "nodal myocyte"
    assert res.iloc[0]["rank"] == 223
    assert len(res) == 2
    assert res.iloc[1]["rank"] == 3

    # search in name, without synonyms search
    res = search(df=df, string="P cell", field="name", _show_rank=True)
    assert res.iloc[0]["name"] == "PP cell"
    assert res.iloc[0]["rank"] == 3


def test_search_limit(df):
    res = search(df=df, string="P cell", limit=1)
    assert res.shape[0] == 1


def test_search_return_df(df):
    res = search(df=df, string="P cell")
    assert res.shape == (2, 5)
    assert res.iloc[0]["name"] == "nodal myocyte"


def test_search_pass_fields(df):
    res = search(
        df=df,
        string="type F enteroendocrine",
        field=["synonyms", "children"],
        _show_rank=True,
    )
    assert res.iloc[0]["synonyms"] == "type F enteroendocrine cell"
    assert res.iloc[0]["rank"] == 15


def test_search_case_sensitive(df):
    res = search(df=df, string="b cell", case_sensitive=True)
    assert len(res) == 0
    res = search(df=df, string="b cell", case_sensitive=False, _show_rank=True)
    assert res.iloc[0]["name"] == "B cell"
    assert res.iloc[0]["rank"] == 438


def test_search_empty_df():
    res = search(pd.DataFrame(columns=["a", "b", "c"]), string="")
    assert res.shape == (0, 3)


def test_escape_string(df):
    res = search(df=df, string="cat[")
    assert len(res) == 1
    assert res.iloc[0]["name"] == "cat[*_*]"

    res = search(df=df, string="*_*")
    assert len(res) == 1
    assert res.iloc[0]["name"] == "cat[*_*]"
