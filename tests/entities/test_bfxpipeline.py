import bionty.base as bt_base
import pandas as pd


def test_lamin_bfxpipeline_inspect_name():
    df = pd.DataFrame(
        index=[
            "nf-core methylseq v2.6.0",
            "Cell Ranger v8.0.0",
            "This bfx pipeline does not exist",
        ]
    )

    bfxp = bt_base.BFXPipeline(source="lamin")
    inspected_df = bfxp.inspect(df.index, field=bfxp.name, return_df=True)

    inspect = inspected_df["__validated__"].reset_index(drop=True)
    expected_series = pd.Series([True, True, False])

    assert inspect.equals(expected_series)
