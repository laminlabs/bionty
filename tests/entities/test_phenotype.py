import bionty.base as bt_base
import pandas as pd


def test_hp_phenotype_inspect_name():
    df = pd.DataFrame(
        index=[
            "Specific learning disability",
            "Dystonia",
            "Cerebral hemorrhage",
            "Slurred speech",
            "This phenotype does not exist",
        ]
    )

    pt = bt_base.Phenotype(source="hp")
    inspected_df = pt.inspect(df.index, field=pt.name, return_df=True)

    inspect = inspected_df["__validated__"].reset_index(drop=True)
    expected_series = pd.Series([True, True, True, True, False])

    assert inspect.equals(expected_series)


def test_mp_phenotype_inspect_name():
    df = pd.DataFrame(
        index=[
            "decreased ovary apoptosis",
            "abnormal Ebner's gland morphology",
            "abnormal lacrimal sac morphology",
            "abnormal nictitating membrane morphology",
            "This phenotype does not exist",
        ]
    )

    pt = bt_base.Phenotype(source="mp")
    inspected_df = pt.inspect(df.index, field=pt.name, return_df=True)

    inspect = inspected_df["__validated__"].reset_index(drop=True)
    expected_series = pd.Series([True, True, True, True, False])

    assert inspect.equals(expected_series)


def test_zp_phenotype_inspect_name():
    df = pd.DataFrame(
        index=[
            "somitogenesis disrupted, abnormal",
            "somite specification disrupted, abnormal",
            "liver has extra parts of type collagen trimer liver, abnormal",
            "neuromast hair cell normal process quality apoptotic process, abnormal",
            "This phenotype does not exist",
        ]
    )

    pt = bt_base.Phenotype(source="zp")
    inspected_df = pt.inspect(df.index, field=pt.name, return_df=True)

    inspect = inspected_df["__validated__"].reset_index(drop=True)
    expected_series = pd.Series([True, True, True, True, False])

    assert inspect.equals(expected_series)


def test_phe_phenotype_inspect_name():
    df = pd.DataFrame(
        index=[
            "Intestinal infection due to C. difficile",
            "Sepsis and SIRS",
            "Systemic inflammatory response syndrome (SIRS)",
            "Septic shock",
            "This phenotype does not exist",
        ]
    )

    pt = bt_base.Phenotype(source="phe")
    inspected_df = pt.inspect(df.index, field=pt.name, return_df=True)

    inspect = inspected_df["__validated__"].reset_index(drop=True)
    expected_series = pd.Series([True, True, True, True, False])

    assert inspect.equals(expected_series)


def test_path_phenotype():
    df = pd.DataFrame(
        index=[
            "nocturnal",
            "male",
            "female",
            "mobility",
            "This phenotype does not exist",
        ]
    )

    pt = bt_base.Phenotype(source="pato")
    inspected_df = pt.inspect(df.index, field=pt.name, return_df=True)
    inspect = inspected_df["__validated__"].reset_index(drop=True)
    expected_series = pd.Series([True, True, True, True, False])

    assert inspect.equals(expected_series)
