"""Collection of utility methods used throughout the package."""
from itertools import product, zip_longest
from math import floor
from string import punctuation
from typing import Iterator, List, Optional, Tuple, Union

from Bio.Seq import Seq

from pyvariant.constants import DELETION, DELINS, DUPLICATION, INSERTION, SUBSTITUTION

from .tables import DNA, DNA_CODON_TABLE, PROTEIN

# Dictionary used to replace punctuation in a string
PUNCTUATION_TO_UNDERSCORE = str.maketrans(punctuation + " ", "_" * len(punctuation + " "))


def calc_cdna_to_protein(position: int) -> int:
    """Do the math to convert a cDNA position to a protein position.

    Args:
        position (int): cDNA position

    Returns:
        int: Equivalent protein position
    """
    return floor((position - 1) / 3 + 1)


def classify_seq_change(refseq: str, altseq: str) -> str:
    """Return the type of variant based on the given reference -> alternate allele change.

    Args:
        refseq (str): Reference allele
        altseq (str): Alternate allele

    Raises:
        ValueError: Could not determine the type of variant

    Returns:
        str: Variant type
    """
    if is_deletion(refseq, altseq):
        return DELETION
    elif is_delins(refseq, altseq):
        return DELINS
    elif is_duplication(refseq, altseq):
        return DUPLICATION
    elif is_insertion(refseq, altseq):
        return INSERTION
    elif is_substitution(refseq, altseq):
        return SUBSTITUTION
    else:
        raise ValueError(f"Unable to determine variant type for {refseq}/{altseq}")


def collapse_seq_change(ref: str, alt: str) -> Tuple[str, str, int, int]:
    """Collapse a sequence change to the shortest possible change, with exceptions depending on the
    type of change.

    Examples:
                  ref:  100 - GGT - 102
                  alt:  100 - GTG - 102
                               ^^
        --------------------------------
        collapsed alt:  101 -  TG - 102

    Args:
        ref (str): Reference allele
        alt (str): Alternate allele

    Returns:
        Tuple[str, str, int, int]:
            Collapsed reference allele,
            collapsed alternate allele,
            nucleotides changed in reference allele,
            nucleotides changed in alternate allele
    """
    ref_collapse = ref
    alt_collapse = alt
    start_offset = 0
    end_offset = 0

    # Special case when the ref and alt are the same
    if ref == alt:
        return ref, alt, 0, 0

    # If the event is a duplication, return the bases as is
    if is_duplication(ref, alt):
        return ref, alt, 0, 0

    # Trim bases from each end that are identical between the ref and alt
    ref_collapse, alt_collapse, same_5_prime, same_3_prime = split_common_sequence(ref, alt)
    start_offset = len(same_5_prime)
    end_offset = len(same_3_prime)

    # If the event is an insertion or deletion, preserve the 5' and 3' ref bases
    if same_5_prime and same_3_prime:
        if len(ref_collapse) < len(alt_collapse):
            ref_collapse = same_5_prime[-1] + ref_collapse + same_3_prime[0]
            alt_collapse = same_5_prime[-1] + alt_collapse + same_3_prime[0]
            start_offset -= 1
            end_offset -= 1

    # If the ref is collapsed to an empty string it generally indicates an amino acid duplication
    if not ref_collapse:
        return ref, alt, 0, 0

    return ref_collapse, alt_collapse, start_offset, end_offset


def expand_nt(seq: str) -> Iterator[str]:
    """Expand any ambiguous nucleotides (e.g. 'ARA' -> 'AAA', 'AGA').

    Args:
        seq (str): Nucleotide sequence

    Yields:
        Iterator[str]: Generator of unambiguous nucleotide sequences
    """
    yield from iter("".join(i) for i in product(*("".join(DNA[nt]) for nt in seq)))


def expand_pep(seq: str) -> Iterator[str]:
    """Expand any ambiguous amino acids (e.g. 'B' -> 'D', 'N').

    Args:
        seq (str): Amino acid sequence

    Yields:
        Iterator[str]: Generator of unambiguous amino acids
    """
    yield from iter("".join(i) for i in product(*("".join(PROTEIN[aa]) for aa in seq)))


def format_hgvs_position(position: int, offset: int, is_3_prime_utr: bool = False) -> str:
    """Format a position as a string according to HGVS standards.

    Args:
        position (int): Position
        offset (int): Position offset
        is_3_prime_utr (bool, optional): Position offset is relative to the 3' UTR. Defaults to False.

    Returns:
        str: HGVS-style representation for the position
    """
    position_str = ""

    if is_3_prime_utr:
        position_str = "*"

    if position:
        if offset and position == 1 and not is_3_prime_utr:
            position_str += f"{offset:+}"
        elif offset:
            position_str += f"{position}{offset:+}"
        else:
            position_str += f"{position}"

    return position_str


def is_deletion(refseq: str, altseq: str) -> bool:
    """Check if a sequence change should be classified as a deletion variant. A deletion is when
    one or more bases are removed (deleted).

    Args:
        refseq (str): Reference allele
        altseq (str): Alternate allele

    Returns:
        bool: True if the sequence change represents a deletion else False
    """
    return len(refseq) > 0 and len(altseq) == 0


def is_delins(refseq: str, altseq: str) -> bool:
    """Check if a sequence change should be classified as a delins variant. A 'delins' or
    'deletion-insertion' is when one or more bases are replaced by one or more other bases and is
    not a substitution, inversion, or conversion.

    Args:
        refseq (str): Reference allele
        altseq (str): Alternate allele

    Returns:
        bool: True if the sequence change represents a delins else False
    """
    if len(refseq) * len(altseq) > 1:
        if not is_duplication(refseq, altseq) and not is_insertion(refseq, altseq):
            return True

    return False


def is_duplication(refseq: str, altseq: str) -> bool:
    """Check if a sequence change should be classified as a duplication variant. An duplication
    is when one or more bases are inserted and the bases ARE a copy of the bases immediately 5'
    (if the bases are not a copy, it is an insertion).

    Args:
        refseq (str): Reference allele
        altseq (str): Alternate allele

    Returns:
        bool: True if the sequence change represents a duplication else False
    """
    return len(refseq) > 0 and altseq == refseq * 2


def is_frameshift(cdna_refseq: str, cdna_altseq: str) -> bool:
    """Check if a nucleotide change in the cDNA would result in a frameshift variant. A frame shift
    is when a number of nucleotides, that are not a multiple of 3, (i.e. the length of a codon) are
    inserted or deleted, which causes a shift in the reading frame.

    Args:
        refseq (str): cDNA reference allele
        altseq (str): cDNA alternate allele

    Returns:
        bool: True if the sequence change represents a frameshift else False
    """
    return abs(len(cdna_refseq) - len(cdna_altseq)) % 3 != 0


def is_insertion(refseq: str, altseq: str) -> bool:
    """Check if a sequence change should be classified as an insertion variant. An insertion
    is when one or more bases are inserted and the bases are NOT a copy of the bases immediately 5'
    (i.e. a duplication).

    Args:
        refseq (str): Reference allele
        altseq (str): Alternate allele

    Returns:
        bool: True if the sequence change represents an insertion else False
    """
    return not is_duplication(refseq, altseq) and bool(split_insertion(refseq, altseq))


def is_substitution(refseq: str, altseq: str) -> bool:
    """Check if a sequence change should be classified as a substitution variant. A substitution
    is when exactly one base is replaced by exactly one other base.

    Args:
        refseq (str): Reference allele
        altseq (str): Alternate allele

    Returns:
        bool: True if the sequence change represents a substitution else False
    """
    return len(refseq) == 1 and len(altseq) == 1


def normalize_release(release: Union[float, int, str]) -> int:
    """Normalize a release number.

    Args:
        release (Union[float, int, str]): Ensembl release number

    Returns:
        int: Ensembl release as an integer
    """
    return int(release)


def normalize_species(species: str) -> str:
    """Normalize a species name, e.g. 'Homo sapiens' -> 'homo_sapiens'.

    Args:
        species (str): Species name

    Returns:
        str: Normalized species name
    """
    return str(species).lower().translate(PUNCTUATION_TO_UNDERSCORE)


def reference_by_release(release: int) -> str:
    """Given the Ensembl release number, return the reference name.

    Examples:
        >>> reference_by_release(69)
        'GRCh37'
        >>> reference_by_release(100)
        'GRCh38'

    Args:
        release (int): Ensembl release number

    Raises:
        ValueError: Ensembl release does not match a known reference

    Returns:
        str: Reference name
    """
    if release == 54:
        return "GRCh36"
    elif 54 < release <= 75:
        return "GRCh37"
    elif 75 < release:
        return "GRCh38"
    else:
        raise ValueError(f"Unknown reference for release '{release}'")


def reverse_complement(sequence: str) -> str:
    """Return the reverse complement of a given nucleotide sequence.

    Args:
        sequence (str): Nucleotide sequence

    Returns:
        str: Reverse complement of the nucleotide sequence
    """
    return str(Seq(sequence).reverse_complement())


def reverse_translate(peptide: str) -> Iterator[str]:
    """Return all reverse translations of an amino acid sequence (e.g. 'C' -> 'TGC', 'TGC', 'TGT', 'TGT').

    Args:
        peptide (str): Amino acid sequence

    Yields:
        Iterator[str]: Generator of unambiguous, reverse complements of the amino acid sequence
    """
    for pep in expand_pep(peptide):
        yield from iter("".join(i) for i in product(*[DNA_CODON_TABLE[aa] for aa in pep]))


def split_by_codon(iterable: str) -> Iterator[str]:
    """Collect a sequence into chunks of 3 (adapted from the 'grouper' recipe found
    here: https://docs.python.org/3.8/library/itertools.html#itertools-recipes).

    Examples:
        >>> split_by_codon('ABCDEF')
        ['ABC', 'DEF']

    Args:
        iterable (str): Nucleotide sequence

    Raises:
        ValueError: Length of the nucleotide sequence is not divisible by 3

    Yields:
        Iterator[str]: Generator of codon sequences
    """
    if len(iterable) % 3 != 0:
        raise ValueError(f"Iterable ({iterable}) is not divisible by 3")

    args = [iter(iterable)] * 3
    yield from iter("".join(i) for i in zip_longest(*args))


def split_insertion(refseq: str, altseq: str) -> Optional[Tuple[str, str, str]]:
    """Find an insertion (if any). This is done by finding a substring such that if the substring
    was removed from the alt, the alt would be the same as the ref.

    Examples:
        >>> split_insertion("GT", "GAT")
        ("G", "A", "T")

    Args:
        refseq (str): Reference allele
        altseq (str): Alternate allele

    Returns:
        Optional[Tuple[str, str, str]]:
            Sequence flanking the insertion sequence on the left,
            Insertion sequence,
            Sequence flanking the insertion sequence on the right,
    """
    if refseq:
        _, alt_collapse, same_5_prime, same_3_prime = split_common_sequence(refseq, altseq)
        if same_5_prime + same_3_prime == refseq:
            return (same_5_prime, alt_collapse, same_3_prime)

    return None


def split_common_sequence(refseq: str, altseq: str) -> Tuple[str, str, str, str]:
    """Compare two strings (sequences) and split each at the point where the two are no longer the
    same at either end.

    For example, 'AATTTC' and 'AAGC' both start with 'AA' and end with 'C'

    Examples:
        >>> split_common_sequence('AATTTC', 'AAGC') == ('TTT', 'G', 'AA', 'C')

    Args:
        refseq (str): Reference allele
        altseq (str): Alternate allele

    Returns:
        Tuple[str, str, str, str]:
            Unique subsequence of the reference allele
            Unique subsequence of the alternate allele
            Sequence common at the 5' end of both reference and alternate alleles
            Sequence common at the 3' end of both reference and alternate alleles
    """
    common_left: List[str] = list()
    common_right: List[str] = list()
    refseq_ = list(refseq)
    altseq_ = list(altseq)

    def trim_one_side(idx: int, common: List):
        assert idx in (0, -1)

        while True:
            try:
                i = refseq_.pop(idx)
            except IndexError:
                i = ""

            try:
                j = altseq_.pop(idx)
            except IndexError:
                j = ""

            if i != j or not i or not j:
                # Put the 'popped' bases back then stop
                if i:
                    if idx == 0:
                        refseq_.insert(0, i)
                    elif idx == -1:
                        refseq_.append(i)
                if j:
                    if idx == 0:
                        altseq_.insert(0, j)
                    elif idx == -1:
                        altseq_.append(j)
                break
            else:
                if idx == 0:
                    common.append(i)
                elif idx == -1:
                    common.insert(0, i)

    trim_one_side(0, common_left)  # Trim 5' (left) end
    trim_one_side(-1, common_right)  # Trim 3' (right) end

    return "".join(refseq_), "".join(altseq_), "".join(common_left), "".join(common_right)


def strip_version(key: str) -> str:
    """Strip the version number from a symbol.

    Examples:
        >>> strip_version('NM_000546.5')
        'NM_000546'
        >>> strip_version('ENST00000357191.1')
        'ENST00000357191'

    Args:
        key (str): Identifier

    Returns:
        str: Identifier with the version number removed
    """
    return key.rsplit(".", 1)[0]
