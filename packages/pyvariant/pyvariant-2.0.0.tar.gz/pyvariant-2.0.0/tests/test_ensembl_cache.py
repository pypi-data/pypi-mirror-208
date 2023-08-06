import numpy as np
import pandas as pd

from pyvariant.ensembl_cache import exon_offset_transcript, set_protein_id


def test_exon_offset_transcript():
    columns = [
        "feature",
        "start",
        "end",
        "strand",
        "transcript_id",
        "transcript_start",
        "transcript_end",
    ]
    data = [
        ["transcript", 1, 123, "+", "ENST00000123456", np.nan, np.nan],
        ["exon", 1, 12, "+", "ENST00000123456", np.nan, np.nan],
        ["exon", 97, 123, "+", "ENST00000123456", np.nan, np.nan],
    ]
    in_df = pd.DataFrame(data, columns=columns)
    out_df = exon_offset_transcript(in_df)
    assert out_df["transcript_start"].to_list() == [1, 1, 13]
    assert out_df["transcript_end"].to_list() == [39, 12, 39]


def test_set_protein_id():
    columns = ["feature", "transcript_id", "protein_id"]
    data = [
        ["CDS", "ENST00000123456", "ENSP00000654321"],
        ["CDS", "ENST00000412167", "ENSP00000390987"],
        ["exon", "ENST00000999999", np.nan],
        ["stop_codon", "ENST00000412167", np.nan],
        ["cdna", "ENST00000412167", np.nan],
    ]
    in_df = pd.DataFrame(data, columns=columns)
    out_df = set_protein_id(in_df)
    assert out_df["protein_id"].to_list() == [
        "ENSP00000654321",
        "ENSP00000390987",
        np.nan,
        "ENSP00000390987",
        "ENSP00000390987",
    ]
