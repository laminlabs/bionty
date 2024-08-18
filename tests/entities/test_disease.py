import bionty.base as bt_base
import pandas as pd


def test_mondo_disease_inspect_name():
    df = pd.DataFrame(
        index=[
            "supraglottis cancer",
            "alexia",
            "trigonitis",
            "paranasal sinus disorder",
            "This disease does not exist",
        ]
    )

    ds = bt_base.Disease(source="mondo")
    inspected_df = ds.inspect(df.index, field=ds.name, return_df=True)

    inspect = inspected_df["__validated__"].reset_index(drop=True)
    expected_series = pd.Series([True, True, True, True, False])

    assert inspect.equals(expected_series)


def test_doid_disease_inspect_ontology_id():
    df = pd.DataFrame(
        index=[
            "DOID:0001816",
            "DOID:0002116",
            "DOID:5547",
            "DOID:5551",
            "This disease does not exist",
        ]
    )

    ds = bt_base.Disease(source="doid")
    inspected_df = ds.inspect(df.index, field=ds.ontology_id, return_df=True)

    inspect = inspected_df["__validated__"].reset_index(drop=True)
    expected_series = pd.Series([True, True, True, True, False])

    assert inspect.equals(expected_series)


def test_icd_9_disease_inspect_name():
    df = pd.DataFrame(
        index=[
            "Cholera d/t vib cholerae",
            "Typhoid fever",
            "Mult gest-plac/sac NOS",
            "Paratyphoid fever a",
            "This disease does not exist",
        ]
    )

    ds = bt_base.Disease(source="icd", version="icd-9-2011")
    inspected_df = ds.inspect(df.index, field=ds.name, return_df=True)

    inspect = inspected_df["__validated__"].reset_index(drop=True)
    expected_series = pd.Series([True, True, True, True, False])

    assert inspect.equals(expected_series)


def test_icd_10_disease_inspect_name():
    df = pd.DataFrame(
        index=[
            "Vaping-related disorder",
            "COVID-19",
            "Typhoid fever with heart involvement",
            "Typhoid fever, unspecified",
            "This disease does not exist",
        ]
    )

    ds = bt_base.Disease(source="icd", version="icd-10-2020")
    inspected_df = ds.inspect(df.index, field=ds.name, return_df=True)

    inspect = inspected_df["__validated__"].reset_index(drop=True)
    expected_series = pd.Series([True, True, True, True, False])

    assert inspect.equals(expected_series)


def test_icd_11_disease_inspect_name():
    df = pd.DataFrame(
        index=[
            "Certain infectious or parasitic diseases",
            "Cholera",
            "Intestinal infection due to other Vibrio",
            "Gastroenteritis or colitis of infectious origin",
            "This disease does not exist",
        ]
    )

    ds = bt_base.Disease(source="icd", version="icd-11-2023")
    inspected_df = ds.inspect(df.index, field=ds.name, return_df=True)

    inspect = inspected_df["__validated__"].reset_index(drop=True)
    expected_series = pd.Series([True, True, True, True, False])

    assert inspect.equals(expected_series)
