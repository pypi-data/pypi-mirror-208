"""Regex for parsing string representations for variants."""
import re
from typing import Any, Dict

from Bio.Data import IUPACData

# -------------------------------------------------------------------------------------------------
# Match object types
# -------------------------------------------------------------------------------------------------
MISSING = None  # Default value for missing attributes
MATCH_TYPES = {
    "feature": str,
    "prefix": str,
    "start": int,
    "start_offset": int,
    "start_seq": str,
    "end": int,
    "end_offset": int,
    "end_seq": str,
    "strand": str,
    "refseq": str,
    "altseq": str,
    "suffix": str,
    "suffix2": str,
}


# -------------------------------------------------------------------------------------------------
# General purpose regex
# -------------------------------------------------------------------------------------------------
OFFSET = r"[-+]\d+"  # A number preceeded by ('-' or '+')
PREFIX = r"[cegpmr]"  # HGVS reference sequence type prefixes
POSITION = r"(?<![-+])\d+"  # A number not preceeded by ('-' or '+')
REFERENCE = r"[A-Za-z0-9_./-]+"  # Should match all reference names (chromosome, gene, etc.)
SEQ = r"[A-Za-z*?=]+"  # All non-ambiguous amino acid and nucleotides
STRAND = r"[-+]"  # One of '-' or '+'
SUFFIX = r"delins|del|dup|fs|ins|>"  # HGVS variant suffixes

# Regex used to capture all 3-letter amino acid codes
PROTEIN_LETTERS_3 = re.compile("|".join(IUPACData.protein_letters_3to1.keys()))


# -------------------------------------------------------------------------------------------------
# Variant matching regex
# -------------------------------------------------------------------------------------------------
REGEX = [
    # -------------------------------------------------------------------------------------------------
    # HGVS (and "HGVS-like") string matching
    # -------------------------------------------------------------------------------------------------
    # NOTE: Avoid accidently matching a delins as a deletion by trying the delins regex first
    # Delins, single base. Examples:
    # ENST00000078429:c.625delinsA
    # CALR:e.9delins
    re.compile(
        rf"(?P<breakpoint1_feature>{REFERENCE})"
        r":"
        rf"(?P<breakpoint1_prefix>{PREFIX})"
        r"."
        rf"(?P<breakpoint1_start_seq>{SEQ})?"
        rf"(?P<breakpoint1_start>{POSITION})?"
        rf"(?P<breakpoint1_start_offset>{OFFSET})?"
        r"(?P<breakpoint1_suffix>delins)"
        rf"(?P<breakpoint1_altseq>{SEQ})"
    ),
    # Delins, multiple bases. Examples:
    # ENST00000078429:c.625_627delinsACC
    # BRCA2:p.K1025_K1026delinsN*
    re.compile(
        rf"(?P<breakpoint1_feature>{REFERENCE})"
        r":"
        rf"(?P<breakpoint1_prefix>{PREFIX})"
        r"."
        rf"(?P<breakpoint1_start_seq>{SEQ})?"
        rf"(?P<breakpoint1_start>{POSITION})?"
        rf"(?P<breakpoint1_start_offset>{OFFSET})?"
        r"_"
        rf"(?P<breakpoint1_end_seq>{SEQ})?"
        rf"(?P<breakpoint1_end>{POSITION})?"
        rf"(?P<breakpoint1_end_offset>{OFFSET})?"
        r"(?P<breakpoint1_suffix>delins)"
        rf"(?P<breakpoint1_altseq>{SEQ})"
    ),
    # Deletion, single base. Examples:
    # ENST00000297679:c.45del
    # ENST00000297679:c.45del (not HGVS)
    # BRCA2:p.A1847del
    re.compile(
        rf"(?P<breakpoint1_feature>{REFERENCE})"
        r":"
        rf"(?P<breakpoint1_prefix>{PREFIX})"
        r"."
        rf"(?P<breakpoint1_start_seq>{SEQ})?"
        rf"(?P<breakpoint1_start>{POSITION})?"
        rf"(?P<breakpoint1_start_offset>{OFFSET})?"
        r"(?P<breakpoint1_suffix>del)"
        rf"(?P<breakpoint1_refseq>{SEQ})?"
    ),
    # Deletion, multiple bases. Examples:
    # ENST00000297679:c.45_46del
    # ENST00000297679:c.45_46delAG (not HGVS)
    # BRCA1:e.7_8del
    # BRCA2:p.A1847_M1890del
    re.compile(
        rf"(?P<breakpoint1_feature>{REFERENCE})"
        r":"
        rf"(?P<breakpoint1_prefix>{PREFIX})"
        r"."
        rf"(?P<breakpoint1_start_seq>{SEQ})?"
        rf"(?P<breakpoint1_start>{POSITION})?"
        rf"(?P<breakpoint1_start_offset>{OFFSET})?"
        r"_"
        rf"(?P<breakpoint1_end_seq>{SEQ})?"
        rf"(?P<breakpoint1_end>{POSITION})?"
        rf"(?P<breakpoint1_end_offset>{OFFSET})?"
        r"(?P<breakpoint1_suffix>del)"
        rf"(?P<breakpoint1_refseq>{SEQ})?"
    ),
    # Duplication, single base. Examples:
    # ENST00000217260:c.98dup
    re.compile(
        rf"(?P<breakpoint1_feature>{REFERENCE})"
        r":"
        rf"(?P<breakpoint1_prefix>{PREFIX})"
        r"."
        rf"(?P<breakpoint1_start_seq>{SEQ})?"
        rf"(?P<breakpoint1_start>{POSITION})?"
        rf"(?P<breakpoint1_start_offset>{OFFSET})?"
        r"(?P<breakpoint1_suffix>dup)"
        rf"(?P<breakpoint1_refseq>{SEQ})?"
    ),
    # Duplication, multiple bases. Examples:
    # ENST00000217260:c.98_99dup
    # EGFR:p.N771_H773dup
    re.compile(
        rf"(?P<breakpoint1_feature>{REFERENCE})"
        r":"
        rf"(?P<breakpoint1_prefix>{PREFIX})"
        r"."
        rf"(?P<breakpoint1_start_seq>{SEQ})?"
        rf"(?P<breakpoint1_start>{POSITION})?"
        rf"(?P<breakpoint1_start_offset>{OFFSET})?"
        r"_"
        rf"(?P<breakpoint1_end_seq>{SEQ})?"
        rf"(?P<breakpoint1_end>{POSITION})?"
        rf"(?P<breakpoint1_end_offset>{OFFSET})?"
        r"(?P<breakpoint1_suffix>dup)"
        rf"(?P<breakpoint1_refseq>{SEQ})?"
    ),
    # Frameshift, single base. Examples:
    # BRCA1:p.E1013Nfs*4
    # BRCA1:p.E1013Nfs (not HGVS, missing new termination position)
    # NP_003997.2:p.Arg97fs (not HGVS, missing altseq)
    re.compile(
        rf"(?P<breakpoint1_feature>{REFERENCE})"
        r":"
        rf"(?P<breakpoint1_prefix>{PREFIX})"
        r"."
        rf"(?P<breakpoint1_start_seq>{SEQ})?"
        rf"(?P<breakpoint1_start>{POSITION})?"
        rf"(?P<breakpoint1_start_offset>{OFFSET})?"
        rf"(?P<breakpoint1_altseq>{SEQ})?"
        r"(?P<breakpoint1_suffix>fs)"
        r"\*?"
        rf"({POSITION})?"  # TODO: Do something with new termination position?
    ),
    # Insertion. Examples:
    # chr13:g.32913032_32913033insTT
    # BRAF:p.T599_V600insEAT
    re.compile(
        rf"(?P<breakpoint1_feature>{REFERENCE})"
        r":"
        rf"(?P<breakpoint1_prefix>{PREFIX})"
        r"."
        rf"(?P<breakpoint1_start_seq>{SEQ})?"
        rf"(?P<breakpoint1_start>{POSITION})?"
        rf"(?P<breakpoint1_start_offset>{OFFSET})?"
        r"_"
        rf"(?P<breakpoint1_end_seq>{SEQ})?"
        rf"(?P<breakpoint1_end>{POSITION})?"
        rf"(?P<breakpoint1_end_offset>{OFFSET})?"
        r"(?P<breakpoint1_suffix>ins)"
        rf"(?P<breakpoint1_altseq>{SEQ})?"
    ),
    # Nucleotide substitution. Examples:
    # ENST00000078429:r.916A>G
    # CEP72:c.1-2384C>T
    # TERT:c.-124C>T
    re.compile(
        rf"(?P<breakpoint1_feature>{REFERENCE})"
        r":"
        rf"(?P<breakpoint1_prefix>{PREFIX})"
        r"."
        rf"(?P<breakpoint1_start>{POSITION})?"
        rf"(?P<breakpoint1_start_offset>{OFFSET})?"
        rf"(?P<breakpoint1_refseq>{SEQ})"
        r"(?P<breakpoint1_suffix>>)"
        rf"(?P<breakpoint1_altseq>{SEQ})"
    ),
    # Protein substitution. Examples:
    # BRAF:p.R4621I
    re.compile(
        rf"(?P<breakpoint1_feature>{REFERENCE})"
        r":"
        rf"(?P<breakpoint1_prefix>{PREFIX})"
        r"."
        rf"(?P<breakpoint1_refseq>{SEQ})"
        rf"(?P<breakpoint1_start>{POSITION})?"
        rf"(?P<breakpoint1_start_offset>{OFFSET})?"
        rf"(?P<breakpoint1_altseq>{SEQ})"
    ),
    # Fusion. Examples:
    # NM_152263.2:r.-115_775::NM_002609.3:r.1580_*1924
    re.compile(
        rf"(?P<breakpoint1_feature>{REFERENCE})"
        r":"
        rf"(?P<breakpoint1_prefix>{PREFIX})"
        r"."
        rf"(?P<breakpoint1_start>{POSITION})?"
        rf"(?P<breakpoint1_start_offset>{OFFSET})?"
        r"_?"
        rf"(?P<breakpoint1_end>{POSITION})?"
        rf"(?P<breakpoint1_end_offset>{OFFSET})?"
        r"::"
        rf"(?P<breakpoint2_feature>{REFERENCE})"
        r":"
        rf"(?P<breakpoint2_prefix>{PREFIX})"
        r"."
        rf"(?P<breakpoint2_start>{POSITION})?"
        rf"(?P<breakpoint2_start_offset>{OFFSET})?"
        r"_?"
        rf"(?P<breakpoint2_end>{POSITION})?"
        rf"(?P<breakpoint2_end_offset>{OFFSET})?"
    ),
    # Non-variant position, multiple bases. Examples:
    # 5:g.1282623_1282626
    re.compile(
        rf"(?P<breakpoint1_feature>{REFERENCE})"
        r":"
        rf"(?P<breakpoint1_prefix>{PREFIX})"
        r"."
        rf"(?P<breakpoint1_start>{POSITION})?"
        rf"(?P<breakpoint1_start_offset>{OFFSET})?"
        r"_"
        rf"(?P<breakpoint1_end>{POSITION})?"
        rf"(?P<breakpoint1_end_offset>{OFFSET})?"
    ),
    # Non-variant position, single base. Examples:
    # ENST00000078429:c.625
    re.compile(
        rf"(?P<breakpoint1_feature>{REFERENCE})"
        r":"
        rf"(?P<breakpoint1_prefix>{PREFIX})"
        r"."
        rf"(?P<breakpoint1_start>{POSITION})?"
        rf"(?P<breakpoint1_start_offset>{OFFSET})?"
    ),
    # -------------------------------------------------------------------------------------------------
    # Non-HGVS string matching
    # -------------------------------------------------------------------------------------------------
    # Delins, single base. Examples:
    # BRAF:p.V600delVinsYM (not HGVS)
    re.compile(
        rf"(?P<breakpoint1_feature>{REFERENCE})"
        r":"
        rf"(?P<breakpoint1_prefix>{PREFIX})"
        r"."
        rf"(?P<breakpoint1_start_seq>{SEQ})?"
        rf"(?P<breakpoint1_start>{POSITION})?"
        rf"(?P<breakpoint1_start_offset>{OFFSET})?"
        r"(?P<breakpoint1_suffix>del)"
        rf"(?P<breakpoint1_refseq>{SEQ})"
        r"(?P<breakpoint1_suffix2>ins)"
        rf"(?P<breakpoint1_altseq>{SEQ})"
    ),
    # Fusion. Examples:
    # (chr8,chr8):fusion(g.128070272,g.127289817)
    re.compile(
        r"\("
        rf"(?P<breakpoint1_feature>{REFERENCE})"
        r","
        rf"(?P<breakpoint2_feature>{REFERENCE})"
        r"\):fusion\("
        rf"(?P<breakpoint1_prefix>{PREFIX})"
        r"."
        rf"(?P<breakpoint1_start>{POSITION})?"
        rf"(?P<breakpoint1_start_offset>{OFFSET})?"
        r"_?"
        rf"(?P<breakpoint1_end>{POSITION})?"
        rf"(?P<breakpoint1_end_offset>{OFFSET})?"
        r","
        rf"(?P<breakpoint2_prefix>{PREFIX})"
        r"."
        rf"(?P<breakpoint2_start>{POSITION})?"
        rf"(?P<breakpoint2_start_offset>{OFFSET})?"
        r"_?"
        rf"(?P<breakpoint2_end>{POSITION})?"
        rf"(?P<breakpoint2_end_offset>{OFFSET})?"
        r"\)"
    ),
]


# -------------------------------------------------------------------------------------------------
# Regex matching logic
# -------------------------------------------------------------------------------------------------
def match(string: str) -> Dict:
    """Try and parse a given variant statement.

    Args:
        string (str): Position or variant represented as a string

    Raises:
        ValueError: Unable to parse position/variant

    Returns:
        Dict: Position/variant attributes
    """

    def count_missing(breakpoint_groups: Dict[str, Dict]) -> int:
        count = 0

        if breakpoint_groups:
            for bp in breakpoint_groups.values():
                for value in bp.values():
                    if value is MISSING:
                        count += 1

        return count

    best_match_nones = 99
    best_match = {}

    # Remove whitespace
    string = string.replace(" ", "")

    # TODO: Support positions offset from stop codon
    if not re.search(r"\*\d", string):
        # Iteratively try each regex until the string matches one
        for regex in REGEX:
            if parsed := regex.fullmatch(string):
                breakpoint_groups: Dict[str, Dict] = {"breakpoint1": {}, "breakpoint2": {}}
                groups: Dict[str, Any] = parsed.groupdict()
                for key, value in groups.items():
                    bp, bpkey = key.split("_", 1)
                    breakpoint_groups[bp][bpkey] = value

                for bp in breakpoint_groups:
                    for key, to_type in MATCH_TYPES.items():
                        if breakpoint_groups[bp].get(key):
                            # Coerce found values to the expected type
                            breakpoint_groups[bp][key] = to_type(breakpoint_groups[bp][key])
                        else:
                            # Add in null values for any missing keys
                            breakpoint_groups[bp][key] = MISSING

                    # Special case, join split suffixes (e.g. 'delVins' -> 'delins')
                    if suffix2 := breakpoint_groups[bp].get("suffix2", ""):
                        breakpoint_groups[bp]["suffix"] += suffix2

                    breakpoint_groups[bp].pop("suffix2")

                # If the string matches multiple regexes, return the match with more values filled out.
                # Presumably this is a better match.
                count = count_missing(breakpoint_groups)
                if count < best_match_nones:
                    best_match = breakpoint_groups
                    best_match_nones = count

    if best_match:
        return best_match
    else:
        raise ValueError(f"Unable to parse '{string}'")
