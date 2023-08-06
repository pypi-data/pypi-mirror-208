"""Module for parsing string representations of variants."""
from typing import Any, Dict, Optional

from Bio.Data import IUPACData

from .constants import (
    CDNA,
    DELETION,
    DELINS,
    DNA,
    DUPLICATION,
    EXON,
    FRAMESHIFT,
    FUSION,
    INSERTION,
    PROTEIN,
    RNA,
    SUBSTITUTION,
)
from .regex import MISSING, PROTEIN_LETTERS_3, match

# Map an HGVS variant prefix to a position type
PREFIX_TO_POSITION_TYPE = {"c": CDNA, "e": EXON, "g": DNA, "p": PROTEIN, "r": RNA}

# Map a HGVS variant string to a variant type
SUFFIX_TO_VARIANT_TYPE = {
    "del": DELETION,
    "delins": DELINS,
    "dup": DUPLICATION,
    "fs": FRAMESHIFT,
    "ins": INSERTION,
    ">": SUBSTITUTION,
}


def parse(string: str) -> Dict[str, Dict[str, Any]]:
    """Parse a position or variant, represented as a string, into a normalized set of values.

    Args:
        string (str): String representation

    Returns:
        Dict[str, Dict[str, Any]]: Normalized values parsed from the string
    """
    # Parse the given string
    parsed = match(string)

    # Infer the type of variant
    if any(parsed["breakpoint1"].values()) and any(parsed["breakpoint2"].values()):
        # If more than breakpoint is found, it's a fusion
        parsed["breakpoint1"]["variant_type"] = FUSION
        parsed["breakpoint2"]["variant_type"] = FUSION
    else:
        # Otherwise, the type of variant depends on the suffix in the variant string
        parsed["breakpoint1"]["variant_type"] = translate_suffix(parsed["breakpoint1"]["suffix"])
        parsed["breakpoint2"]["variant_type"] = MISSING

    # Normalize values in each breakpoint
    for breakpoint in parsed.values():
        breakpoint["position_type"] = translate_prefix(breakpoint["prefix"])

        if breakpoint["start"] is None and breakpoint["start_offset"]:
            breakpoint["start"] = 1

        if breakpoint["end"] is None:
            breakpoint["end"] = breakpoint["start"]
            if breakpoint["end_offset"] is None:
                breakpoint["end_offset"] = breakpoint["start_offset"]

        # Extra parsing of proteins
        if breakpoint["position_type"] == PROTEIN:
            # Protein substitutions don't have the '>' to explicitly say it's a substitution
            if not breakpoint["variant_type"] and (breakpoint["refseq"] or breakpoint["altseq"]):
                breakpoint["variant_type"] = SUBSTITUTION

            # Convert 3-letter amino acid codes to 1-letter codes
            for key in ["refseq", "altseq", "start_seq", "end_seq"]:
                if breakpoint[key]:
                    breakpoint[key] = protein_letters_3to1(breakpoint[key])

        else:
            # Convert sequences to uppercase
            for key in ["refseq", "altseq"]:
                if breakpoint[key]:
                    breakpoint[key] = breakpoint[key].upper()

        # Drop 'refseq_end'
        breakpoint.pop("refseq_end", "")

    return parsed


def protein_letters_3to1(sequence: str) -> str:
    """Convert a sequence of 3-letter amino acids into 1-letter amino acids.

    Args:
        sequence (str): Amino acid sequence

    Returns:
        str: Amino acid sequence with 1-letter amino acids
    """
    return PROTEIN_LETTERS_3.sub(
        lambda match: IUPACData.protein_letters_3to1[match.group(0)], sequence
    )


def translate_prefix(prefix: Optional[str]) -> Optional[str]:
    """Convert an HGVS variant prefix to a position type.

    Args:
        prefix (str): Prefix (e.g. 'r')

    Returns:
        str: Position type (e.g. 'rna')
    """
    prefix = prefix.strip().rstrip(".").lower() if prefix else ""
    return PREFIX_TO_POSITION_TYPE.get(prefix)


def translate_suffix(suffix: Optional[str]) -> Optional[str]:
    """Convert an HGVS variant suffix to a normalized variant type.

    Args:
        variant_type (str): Variant suffix (e.g. 'del')

    Returns:
        str: Variant type (e.g. 'deletion')
    """
    suffix = suffix.strip().lower() if suffix else ""
    return SUFFIX_TO_VARIANT_TYPE.get(suffix)
