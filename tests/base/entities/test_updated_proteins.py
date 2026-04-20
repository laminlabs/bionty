import lamindb as ln
import bionty as bt
from bionty.core._source import register_source_in_bionty_assets
import pandas as pd
import re
import bionty.base as bt_base
import pandas as pd

DEFAULT_VERSION = "2026_04_10"

TEST_PROTEINS = {
    "mouse-ear cress":                "A0A022RI21",
    "bovine":                         "A0A023J7X0",
    "dog":                            "A0A023SFI1",
    "chinese hamster":                "A0A061HTA4",
    "e. coli":                        "A0A023I6S3",
    "long-tailed macaque":            "A0A023JBW5",
    "saccharomyces cerevisiae s288c": "A0A023IRJ6",
    "pig":                            "A0A023I2Y2",
}

def test_uniprot_protein_inspect_uniprotkb_id():
    for organism, valid_id in TEST_PROTEINS.items():
        pr = bt_base.Protein(organism=organism, source="uniprot", version=DEFAULT_VERSION)

        inspected_df = pr.inspect([valid_id, "This does not exist"], "uniprotkb_id", return_df=True)
        inspect = inspected_df["__validated__"].reset_index(drop=True)
        expected = pd.Series([True, False])

        assert inspect.equals(expected), f"❌ Failed for {organism} ({valid_id})"
        print(f"✅ {organism}: {valid_id}")

test_uniprot_protein_inspect_uniprotkb_id()