"""Core logic for handling annotations and mapping positions/variants between different types."""
from __future__ import annotations

import sys
from functools import lru_cache
from itertools import product
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union, cast

import pandas as pd
from gtfparse import read_gtf
from pyfaidx import Fasta

from .constants import (
    CDNA,
    CDS,
    CONTIG_ID,
    DELETION,
    DELINS,
    DNA,
    DUPLICATION,
    EXON,
    EXON_ID,
    FRAMESHIFT,
    FUSION,
    GENE_ID,
    GENE_NAME,
    INSERTION,
    PROTEIN,
    PROTEIN_ID,
    RNA,
    STOP_CODON,
    SUBSTITUTION,
    TRANSCRIPT_ID,
    TRANSCRIPT_NAME,
)
from .files import tsv_to_dict, txt_to_list
from .parser import parse
from .positions import (
    CdnaDeletion,
    CdnaDelins,
    CdnaDuplication,
    CdnaFusion,
    CdnaInsertion,
    CdnaPosition,
    CdnaSubstitution,
    DnaDeletion,
    DnaDelins,
    DnaDuplication,
    DnaFusion,
    DnaInsertion,
    DnaPosition,
    DnaSubstitution,
    ExonFusion,
    ExonPosition,
    ProteinDeletion,
    ProteinDelins,
    ProteinDuplication,
    ProteinFrameshift,
    ProteinFusion,
    ProteinInsertion,
    ProteinPosition,
    ProteinSubstitution,
    RnaDeletion,
    RnaDelins,
    RnaDuplication,
    RnaFusion,
    RnaInsertion,
    RnaPosition,
    RnaSubstitution,
    _CdnaSmallVariant,
    _DnaSmallVariant,
    _ExonSmallVariant,
    _Fusion,
    _Position,
    _ProteinSmallVariant,
    _RnaSmallVariant,
    _SmallVariant,
)
from .sequence import PyfaidxFasta, get_sequence, mutate_sequence
from .tables import AMINO_ACID_TABLE
from .utils import (
    calc_cdna_to_protein,
    classify_seq_change,
    collapse_seq_change,
    expand_nt,
    expand_pep,
    is_insertion,
    reverse_complement,
    reverse_translate,
    split_by_codon,
    strip_version,
)


class Core:
    """Core class that handles converting between position types and retrieving information on
    biological features.
    """

    def __init__(
        self,
        gtf: str,
        cds: List[str],
        dna: List[str],
        peptide: List[str],
        rna: List[str],
        canonical_transcript: Union[List[str], str] = [],
        contig_alias: Union[str, Dict] = {},
        exon_alias: Union[str, Dict] = {},
        gene_alias: Union[str, Dict] = {},
        protein_alias: Union[str, Dict] = {},
        transcript_alias: Union[str, Dict] = {},
    ):
        """_summary_

        Args:
            gtf (str): Path to a GTF files with feature annotations
            cds (List[str]): List of paths to a FASTA files of CDS sequences
            dna (List[str]): List of paths to a FASTA files of DNA sequences
            peptide (List[str]): List of paths to a FASTA files of peptide sequences
            rna (List[str]): List of paths to a FASTA files of RNA sequences
            canonical_transcript (Union[List[str], str], optional): List of canonical transcript IDs, or the path to a text file
            contig_alias (Union[str, Dict], optional): Dictionary mapping contig aliases to their normalized ID, or a path to a text file
            exon_alias (Union[str, Dict], optional): Dictionary mapping exon aliases to their normalized ID, or a path to a text file
            gene_alias (Union[str, Dict], optional): Dictionary mapping gene aliases to their normalized ID, or a path to a text file
            protein_alias (Union[str, Dict], optional): Dictionary mapping protein aliases to their normalized ID, or a path to a text file
            transcript_alias (Union[str, Dict], optional): Dictionary mapping transcript aliases to their normalized ID, or a path to a text file
        """
        self.df = read_gtf(gtf, result_type="pandas")  # TODO: switch to 'polars'?

        self.cds_fasta: List[PyfaidxFasta] = []
        self.dna_fasta: List[PyfaidxFasta] = []
        self.protein_fasta: List[PyfaidxFasta] = []
        self.rna_fasta: List[PyfaidxFasta] = []
        self.cds_fasta = [PyfaidxFasta.load(i) for i in cds]
        self.dna_fasta = [PyfaidxFasta.load(i) for i in dna]
        self.protein_fasta = [PyfaidxFasta.load(i) for i in peptide]
        self.rna_fasta = [PyfaidxFasta.load(i) for i in rna]

        if isinstance(canonical_transcript, str):
            self._canonical_transcript = txt_to_list(canonical_transcript)
        else:
            self._canonical_transcript = canonical_transcript

        if isinstance(contig_alias, str):
            self._contig_alias = tsv_to_dict(contig_alias)
        else:
            self._contig_alias = contig_alias

        if isinstance(exon_alias, str):
            self._exon_alias = tsv_to_dict(exon_alias)
        else:
            self._exon_alias = exon_alias

        if isinstance(gene_alias, str):
            self._gene_alias = tsv_to_dict(gene_alias)
        else:
            self._gene_alias = gene_alias

        if isinstance(protein_alias, str):
            self._protein_alias = tsv_to_dict(protein_alias)
        else:
            self._protein_alias = protein_alias

        if isinstance(transcript_alias, str):
            self._transcript_alias = tsv_to_dict(transcript_alias)
        else:
            self._transcript_alias = transcript_alias

    # ---------------------------------------------------------------------------------------------
    # Functions for loading variants
    # ---------------------------------------------------------------------------------------------
    def parse(self, string: str, canonical: bool = False) -> List:
        """Parse a variant string into a variant object.

        Args:
            string (str): String representing a variant, in HGVS format
            canonical (bool, optional): Only consider the canonical transcript when mapping. Defaults to False.

        Returns:
            List: One or more normalized variants
        """
        parsed = parse(string)
        result = self.variant(
            position_type=parsed["breakpoint1"]["position_type"],
            feature=parsed["breakpoint1"]["feature"],
            start=parsed["breakpoint1"]["start"],
            start_offset=parsed["breakpoint1"]["start_offset"],
            end=parsed["breakpoint1"]["end"],
            end_offset=parsed["breakpoint1"]["end_offset"],
            strand=parsed["breakpoint1"]["strand"],
            refseq=parsed["breakpoint1"]["refseq"],
            altseq=parsed["breakpoint1"]["altseq"],
            variant_type=parsed["breakpoint1"]["variant_type"],
            position_type2=parsed["breakpoint2"]["position_type"],
            feature2=parsed["breakpoint2"]["feature"],
            start2=parsed["breakpoint2"]["start"],
            start_offset2=parsed["breakpoint2"]["start_offset"],
            end2=parsed["breakpoint2"]["end"],
            end_offset2=parsed["breakpoint2"]["end_offset"],
            strand2=parsed["breakpoint2"]["strand"],
            refseq2=parsed["breakpoint2"]["refseq"],
            altseq2=parsed["breakpoint2"]["altseq"],
            canonical=canonical,
        )

        return result

    # TODO: add type hints
    def variant(
        self,
        *,
        position_type: str,
        feature: str,
        start: int,
        start_offset: Optional[int] = None,
        end: Optional[int] = None,
        end_offset: Optional[int] = None,
        strand: Optional[str] = None,
        refseq: Optional[str] = None,
        altseq: Optional[str] = None,
        variant_type: Optional[str] = None,
        position_type2: Optional[str] = None,
        feature2: Optional[str] = None,
        start2: Optional[int] = None,
        start_offset2: Optional[int] = None,
        end2: Optional[int] = None,
        end_offset2: Optional[int] = None,
        strand2: Optional[str] = None,
        refseq2: Optional[str] = None,
        altseq2: Optional[str] = None,
        canonical: bool = False,
    ) -> List:
        """Initialize one or more position or variants objects from the given arguments.

        Args:
            position_type (str): Position type for `start` and `end`. One of 'cdna', 'dna', 'exon', 'protein', or 'rna'.
            feature (str): Feature such as a transcript ID or gene name.
            start (int): Start position.
            start_offset (int, optional): Offset from `start`.
            end (int, optional): End position. Defaults to `start`.
            end_offset (int, optional): Offset from `end`.
            strand (str, optional): Strand the feature is on. One of '+' or '-'.
            refseq (str, optional): Reference allele. Required if the given position represents a variant.
            altseq (str, optional): Alternate allele. Required if the given position represents a variant.
            variant_type (str, optional): Variant type. Required if `refseq` or `altseq` is given.
            position_type2 (str, optional): For fusions. Position type for `start2` and `end2`. One of 'cdna', 'dna', 'exon', 'protein', or 'rna'.
            feature2 (str, optional): For fusions. Feature such as a transcript ID or gene name.
            start2 (int, optional): For fusions. Start position.
            start_offset2 (int, optional): For fusions. Offset from `start2`.
            end2 (int, optional): For fusions. End position. Defaults to `start2`.
            end_offset2 (int, optional): For fusions. Offset from `end2`.
            strand2 (str, optional): For fusions. Strand the feature is on. One of '+' or '-'.
            refseq2 (str, optional): For fusions. Reference allele. Required if the given position represents a variant.
            altseq2 (str, optional): For fusions. Alternate allele. Required if the given position represents a variant.
            canonical (bool, optional): Only consider the canonical transcript when mapping. Defaults to False.

        Raises:
            ValueError: Arguments are missing.

        Returns:
            List: Position or Variants objects
        """
        result: List[Any] = []

        # Set defaults for missing inputs
        start_offset = cast(int, start_offset or 0)
        end = cast(int, end or start)
        end_offset = cast(int, end_offset or 0)
        strand = cast(str, strand or "")
        refseq = cast(str, refseq or "")
        altseq = cast(str, altseq or "")
        variant_type = cast(str, variant_type or "")

        # Infer the variant type from the refseq and altseq, if not given
        if (refseq or altseq) and not variant_type:
            if position_type2:
                variant_type = FUSION
            else:
                variant_type = classify_seq_change(refseq, altseq)

        # Normalize refseq and altseq to uppercase
        if refseq:
            refseq = refseq.upper()

        if altseq:
            altseq = altseq.upper()

        # Normalize uracil (U) to thymine (T)
        if position_type != PROTEIN:
            if refseq:
                refseq = refseq.replace("U", "T")

            if altseq:
                altseq = altseq.replace("U", "T")

        # Replace 'indel' with the HGVS 'delins'
        if variant_type.lower() == "indel":
            variant_type = DELINS

        def get_refseq_altseq(position) -> Tuple[str, str]:
            refseq_ = refseq or self.sequence(position)
            if altseq:
                altseq_ = altseq
            else:
                if variant_type == DELETION:
                    altseq_ = ""
                elif variant_type == DELINS:
                    raise ValueError(f"altseq required for {DELINS}")
                elif variant_type == DUPLICATION:
                    altseq_ = refseq_ * 2
                elif variant_type == FRAMESHIFT:
                    raise ValueError(f"altseq required for {FRAMESHIFT}")
                elif variant_type == INSERTION:
                    raise ValueError(f"altseq required for {INSERTION}")
                elif variant_type == SUBSTITUTION:
                    raise ValueError(f"altseq required for {SUBSTITUTION}")
                else:
                    raise ValueError(f"Unsupported variant type '{variant_type}'")

            return refseq_, altseq_

        # Load a fusion
        if variant_type == FUSION:
            fusion: Optional[Type[_Fusion]] = None

            # TODO: default to any exon for exon fusions?

            if position_type2:
                position_type2 = cast(str, position_type2)
            else:
                raise ValueError(f"missing argument required for {FUSION}: 'position_type2'")

            if feature2:
                feature2 = cast(str, feature2)
            else:
                raise ValueError(f"missing argument required for {FUSION}: 'feature2'")

            if start2:
                start2 = cast(int, start2)
            else:
                raise ValueError(f"missing argument required for {FUSION}: 'start2'")

            # TODO: support mixed type fusions?
            if position_type == CDNA and position_type2 == CDNA:
                fusion = CdnaFusion
            elif position_type == DNA and position_type2 == DNA:
                fusion = DnaFusion
            elif position_type == EXON and position_type2 == EXON:
                fusion = ExonFusion
            elif position_type == PROTEIN and position_type2 == PROTEIN:
                fusion = ProteinFusion
            elif position_type == RNA and position_type2 == RNA:
                fusion = RnaFusion
            else:
                raise ValueError(f"Fusions are not supported for {position_type}::{position_type2}")

            if fusion:
                breakpoint1 = self.variant(
                    feature=feature,
                    start=start,
                    position_type=position_type,
                    start_offset=start_offset,
                    end=end,
                    end_offset=end_offset,
                    strand=strand,
                    refseq=refseq,
                    altseq=altseq,
                )
                breakpoint2 = self.variant(
                    feature=feature2,
                    start=start2,
                    position_type=position_type2,
                    start_offset=start_offset2,
                    end=end2,
                    end_offset=end_offset2,
                    strand=strand2,
                    refseq=refseq2,
                    altseq=altseq2,
                )

                return list(fusion(b1, b2) for b1, b2 in product(breakpoint1, breakpoint2))

        # Respect the given strand, otherwise check both strands
        if strand:
            strand_ = [strand]
        else:
            strand_ = [""]

        # Convert the given parameters to a position of the specified type
        if position_type == CDNA:
            transcript_ids = self.transcript_ids(feature)
            result = self._cdna_to_cdna(
                transcript_ids, start, start_offset, end, end_offset, strand_, canonical=canonical
            )
        elif position_type == DNA:
            contig_ids = self.contig_ids(feature)
            result = self._dna_to_dna(
                contig_ids, start, start_offset, end, end_offset, strand_, canonical=canonical
            )
        elif position_type == EXON:
            transcript_ids = self.transcript_ids(feature)
            result = self._exon_to_exon(
                transcript_ids, start, start_offset, end, end_offset, strand_, canonical=canonical
            )
        elif position_type == PROTEIN:
            transcript_ids = self.transcript_ids(feature)
            result = self._protein_to_protein(
                transcript_ids, start, start_offset, end, end_offset, strand_, canonical=canonical
            )
        elif position_type == RNA:
            transcript_ids = self.transcript_ids(feature)
            result = self._rna_to_rna(
                transcript_ids, start, start_offset, end, end_offset, strand_, canonical=canonical
            )
        else:
            raise ValueError(f"Unrecognized position type '{position_type}'")

        # Optional, convert each position and the given ref and alt sequences to variants
        if variant_type:
            result_ = []
            for position in result:
                refseq_, altseq_ = get_refseq_altseq(position)
                result_.extend(self._position_to_small_variant(position, refseq_, altseq_))

            result = result_

        # TODO: Should this always raise an error?
        if not result:
            raise ValueError("Unable to convert inputs to a variant")

        return result

    # ---------------------------------------------------------------------------------------------
    # Functions for getting variant sequences
    # ---------------------------------------------------------------------------------------------
    # TODO: add type hints
    def altseq(
        self,
        position_or_str,
        strand: Optional[str] = None,
        window: Optional[int] = -1,
        floor: Optional[int] = -1,
        ceiling: Optional[int] = -1,
    ) -> str:
        """Return the mutated sequence for the given variant, inclusive. Alias for
        `sequence(position_or_str, mutate=True)`.

        Args:
            position_or_str: Position or variant to retrieve sequence for
            strand (Optional[str]): Normalize the sequence to the given strand ('+' or '-')
            window (Optional[int]): Total length of the returned sequence
            floor (Optional[int]): Minimum start position of the returned sequence
            ceiling (Optional[int]): Maximum end position of the returned sequence

        Returns:
            str: Sequence

        Raises:
            ValueError: No method exists for getting a sequence for the given position type
        """
        return self.sequence(
            position_or_str, mutate=True, strand=strand, window=window, floor=floor, ceiling=ceiling
        )

    def refseq(
        self,
        position_or_str,
        strand: Optional[str] = None,
        window: Optional[int] = -1,
        floor: Optional[int] = -1,
        ceiling: Optional[int] = -1,
    ) -> str:
        """Return the reference sequence for the given variant, inclusive. Alias for
        `sequence(position_or_str, mutate=False)`.

        Args:
            position_or_str: Position or variant to retrieve sequence for
            strand (Optional[str]): Normalize the sequence to the given strand ('+' or '-')
            window (Optional[int]): Total length of the returned sequence
            floor (Optional[int]): Minimum start position of the returned sequence
            ceiling (Optional[int]): Maximum end position of the returned sequence

        Returns:
            str: Sequence

        Raises:
            ValueError: No method exists for getting a sequence for the given position type
        """
        return self.sequence(
            position_or_str,
            mutate=False,
            strand=strand,
            window=window,
            floor=floor,
            ceiling=ceiling,
        )

    def sequence(
        self,
        position_or_str,
        mutate: bool = True,
        strand: Optional[str] = None,
        window: Optional[int] = -1,
        floor: Optional[int] = -1,
        ceiling: Optional[int] = -1,
    ) -> str:
        """Return the sequence for the given position, inclusive.

        Args:
            position_or_str: Position or variant to retrieve sequence for
            mutate: Return the mutated sequence if the given position is a variant, otherwise return the reference sequence
            strand (Optional[str]): Normalize the sequence to the given strand ('+' or '-')
            window (Optional[int]): Total length of the returned sequence
            floor (Optional[int]): Minimum start position of the returned sequence
            ceiling (Optional[int]): Maximum end position of the returned sequence

        Returns:
            str: Sequence

        Raises:
            ValueError: No method exists for getting a sequence for the given position type
        """
        assert strand in [None, "+", "-"]
        sequence_set = set()

        if isinstance(position_or_str, str):
            position_list = self.parse(position_or_str)
        else:
            position_list = [position_or_str]

        for position in position_list:
            if position.is_fusion:
                sequence_set.add(self._fusion_sequence(position, strand, window, floor, ceiling))
            else:
                sequence_set.add(self._sequence(position, mutate, strand, window, floor, ceiling))

        if len(sequence_set) > 1:
            raise ValueError(f"Ambiguous sequences for '{position_or_str}': {sequence_set}")
        else:
            return sequence_set.pop()

    def _sequence(
        self,
        position,
        mutate: bool,
        strand: Optional[str],
        window: Optional[int],
        floor: Optional[int],
        ceiling: Optional[int],
    ) -> str:
        if isinstance(position, str):
            position_ = self.parse(position)
            assert len(position_) == 1
            position = position_[0]

        # TODO: Is this the correct behaviour for offset variants?
        if (not position.is_fusion and (position.start_offset or position.end_offset)) or (
            position.is_fusion
            and (
                position.breakpoint1.start_offset
                or position.breakpoint1.end_offset
                or position.breakpoint2.start_offset
                or position.breakpoint2.end_offset
            )
        ):
            if position.is_protein:
                raise ValueError(f"Unable to get sequence for {position}")
            else:
                position_ = self.to_dna(position)
                assert len(position_) == 1
                position = position_[0]

        # Get the correct reference
        if position.is_cdna:
            fasta = self._get_fasta(self.cds_fasta, position.transcript_id)
        elif position.is_dna:
            fasta = self._get_fasta(self.dna_fasta, position.contig_id)
        elif position.is_exon:
            raise NotImplementedError(f"No FASTA for exons ({position})")
        elif position.is_protein:
            fasta = self._get_fasta(self.protein_fasta, position.protein_id)
        elif position.is_rna:
            fasta = self._get_fasta(self.rna_fasta, position.transcript_id)
        else:
            raise ValueError(f"Unable to get sequence for {position}")

        # Retrieve the sequence at the given position
        if position.is_small_variant and mutate:
            sequence = self._altseq(position, window, floor, ceiling, fasta)
        else:
            sequence = self._refseq(position, window, floor, ceiling, fasta)

        # Reverse complement the sequence if the strand the position is on isn't the desired strand
        if strand == "+" and position.on_negative_strand:
            sequence = reverse_complement(sequence)
        elif strand == "-" and position.on_positive_strand:
            sequence = reverse_complement(sequence)
        # NOTE: Assumes the DNA FASTA represents the "+" strand of the genome
        elif position.is_dna and position.on_negative_strand and strand != "-":
            sequence = reverse_complement(sequence)

        return sequence

    def _get_fasta(self, fasta_list: List[PyfaidxFasta], ref: str) -> Fasta:
        for fasta in fasta_list:
            if ref in fasta:
                return fasta
        else:
            raise KeyError(f"Sequence '{ref}' not found")

    def _fusion_sequence(
        self,
        position,
        strand: Optional[str],
        window: Optional[int],
        floor: Optional[int],
        ceiling: Optional[int],
    ) -> str:
        sequence = ""

        breakpoint1 = position.breakpoint1
        breakpoint2 = position.breakpoint2

        # To get exon positions, we need to first map the position to DNA
        if breakpoint1.is_exon:
            breakpoint1_ = self.to_dna(breakpoint1)
            assert len(breakpoint1_) == 1
            breakpoint1 = breakpoint1_[0]

        if breakpoint2.is_exon:
            breakpoint2_ = self.to_dna(breakpoint2)
            assert len(breakpoint2_) == 1
            breakpoint2 = breakpoint2_[0]

        # We only care about the position surrounding the breakpoint
        breakpoint1 = breakpoint1.copy_from(breakpoint1, start=breakpoint1.end)
        breakpoint2 = breakpoint2.copy_from(breakpoint2, end=breakpoint2.start)

        # If a window isn't given, make it equal to the breakpoint size
        if window and window > 0:
            pad_left = window // 2
            pad_right = window - pad_left
        else:
            pad_left = breakpoint1.end - breakpoint1.start + 1
            pad_right = breakpoint2.end - breakpoint2.start + 1

        sequence += self.sequence(
            breakpoint1,
            mutate=False,
            strand=(strand or breakpoint1.strand),
            window=pad_left,
            floor=floor,
            ceiling=breakpoint1.end,
        )
        sequence += self.sequence(
            breakpoint2,
            mutate=False,
            strand=(strand or breakpoint2.strand),
            window=pad_right,
            floor=breakpoint2.start,
            ceiling=ceiling,
        )

        return sequence

    def _refseq(
        self,
        position,
        window: Optional[int],
        floor: Optional[int],
        ceiling: Optional[int],
        fasta: Fasta,
    ) -> str:
        if position.is_cdna:
            position = cast(CdnaPosition, position)
            return self._cdna_refseq(position, window, floor, ceiling, fasta)
        elif position.is_dna:
            position = cast(DnaPosition, position)
            return self._dna_refseq(position, window, floor, ceiling, fasta)
        elif position.is_exon:
            position = cast(ExonPosition, position)
            return self._exon_refseq(position, window, floor, ceiling, fasta)
        elif position.is_protein:
            position = cast(ProteinPosition, position)
            return self._protein_refseq(position, window, floor, ceiling, fasta)
        elif position.is_rna:
            position = cast(RnaPosition, position)
            return self._rna_refseq(position, window, floor, ceiling, fasta)
        else:
            raise ValueError(f"Unable to get sequence for {position}")

    def _altseq(
        self,
        variant,
        window: Optional[int],
        floor: Optional[int],
        ceiling: Optional[int],
        fasta: Fasta,
    ) -> str:
        if variant.is_cdna:
            variant = cast(_CdnaSmallVariant, variant)
            return self._cdna_altseq(variant, window, floor, ceiling, fasta)
        elif variant.is_dna:
            variant = cast(_DnaSmallVariant, variant)
            return self._dna_altseq(variant, window, floor, ceiling, fasta)
        elif variant.is_exon:
            variant = cast(_ExonSmallVariant, variant)
            return self._exon_altseq(variant, window, floor, ceiling, fasta)
        elif variant.is_protein:
            variant = cast(_ProteinSmallVariant, variant)
            return self._protein_altseq(variant, window, floor, ceiling, fasta)
        elif variant.is_rna:
            variant = cast(_RnaSmallVariant, variant)
            return self._rna_altseq(variant, window, floor, ceiling, fasta)
        else:
            raise ValueError(f"Unable to get sequence for {variant}")

    def _cdna_refseq(
        self,
        position,
        window: Optional[int],
        floor: Optional[int],
        ceiling: Optional[int],
        fasta: Fasta,
    ) -> str:
        return get_sequence(
            fasta, position.transcript_id, position.start, position.end, window, floor, ceiling
        )

    def _dna_refseq(
        self,
        position,
        window: Optional[int],
        floor: Optional[int],
        ceiling: Optional[int],
        fasta: Fasta,
    ) -> str:
        return get_sequence(
            fasta, position.contig_id, position.start, position.end, window, floor, ceiling
        )

    def _exon_refseq(
        self,
        position,
        window: Optional[int],
        floor: Optional[int],
        ceiling: Optional[int],
        fasta: Fasta,
    ) -> str:
        raise NotImplementedError(f"Unable to get sequence for {position}")

    def _protein_refseq(
        self,
        position,
        window: Optional[int],
        floor: Optional[int],
        ceiling: Optional[int],
        fasta: Fasta,
    ) -> str:
        return get_sequence(
            fasta, position.protein_id, position.start, position.end, window, floor, ceiling
        )

    def _rna_refseq(
        self,
        position,
        window: Optional[int],
        floor: Optional[int],
        ceiling: Optional[int],
        fasta: Fasta,
    ) -> str:
        return get_sequence(
            fasta, position.transcript_id, position.start, position.end, window, floor, ceiling
        )

    def _cdna_altseq(
        self,
        variant,
        window: Optional[int],
        floor: Optional[int],
        ceiling: Optional[int],
        fasta: Fasta,
    ) -> str:
        return mutate_sequence(
            fasta,
            variant.transcript_id,
            variant.start,
            variant.end,
            window,
            floor,
            ceiling,
            variant.altseq,
            insertion=variant.is_insertion,
        )

    def _dna_altseq(
        self,
        variant,
        window: Optional[int],
        floor: Optional[int],
        ceiling: Optional[int],
        fasta: Fasta,
    ) -> str:
        return mutate_sequence(
            fasta,
            variant.contig_id,
            variant.start,
            variant.end,
            window,
            floor,
            ceiling,
            variant.altseq,
            insertion=variant.is_insertion,
        )

    def _exon_altseq(
        self,
        variant,
        window: Optional[int],
        floor: Optional[int],
        ceiling: Optional[int],
        fasta: Fasta,
    ) -> str:
        raise NotImplementedError(f"Unable to get sequence for {variant}")

    def _protein_altseq(
        self,
        variant,
        window: Optional[int],
        floor: Optional[int],
        ceiling: Optional[int],
        fasta: Fasta,
    ) -> str:
        return mutate_sequence(
            fasta,
            variant.protein_id,
            variant.start,
            variant.end,
            window,
            floor,
            ceiling,
            variant.altseq,
            insertion=variant.is_insertion,
        )

    def _rna_altseq(
        self,
        variant,
        window: Optional[int],
        floor: Optional[int],
        ceiling: Optional[int],
        fasta: Fasta,
    ) -> str:
        return mutate_sequence(
            fasta,
            variant.transcript_id,
            variant.start,
            variant.end,
            window,
            floor,
            ceiling,
            variant.altseq,
            insertion=variant.is_insertion,
        )

    # ---------------------------------------------------------------------------------------------
    # Functions for mapping to other position types
    # ---------------------------------------------------------------------------------------------
    # TODO: add type hints
    def to_cdna(self, position, canonical: bool = False) -> List:
        """Map a position to zero or more cDNA positions.

        Args:
            position (Position): Position or variant object.
            canonical (bool, optional): Only consider the canonical transcript when mapping. Defaults to False.

        Returns:
            List[CdnaPosition]: If a variant was given, returns a variant, otherwise returns a position.
        """
        if isinstance(position, str):
            return self._string_to_cdna(position, canonical)
        else:
            return self._position_to_cdna(position, canonical)

    def to_dna(self, position, canonical: bool = False) -> List:
        """Map a position to zero or more DNA positions.

        Args:
            position (Position): Position or variant object.
            canonical (bool, optional): Only consider the canonical transcript when mapping. Defaults to False.

        Returns:
            List[DnaPosition]: If a variant was given, returns a variant, otherwise returns a position.
        """
        if isinstance(position, str):
            return self._string_to_dna(position, canonical)
        else:
            return self._position_to_dna(position, canonical)

    def to_exon(self, position, canonical: bool = False) -> List:
        """Map a position to zero or more exon positions.

        Args:
            position (Position): Position or variant object.
            canonical (bool, optional): Only consider the canonical transcript when mapping. Defaults to False.

        Returns:
            List[ExonPosition]: If a variant was given, returns a variant, otherwise returns a position.
        """
        if isinstance(position, str):
            return self._string_to_exon(position, canonical)
        else:
            return self._position_to_exon(position, canonical)

    def to_protein(self, position, canonical: bool = False) -> List:
        """Map a position to zero or more protein positions.

        Args:
            position (Position): Position or variant object.
            canonical (bool, optional): Only consider the canonical transcript when mapping. Defaults to False.

        Returns:
            List[ProteinPosition]: If a variant was given, returns a variant, otherwise returns a position.
        """
        if isinstance(position, str):
            return self._string_to_protein(position, canonical)
        else:
            return self._position_to_protein(position, canonical)

    def to_rna(self, position, canonical: bool = False) -> List:
        """Map a position to zero or more RNA positions.

        Args:
            position (Position): Position or variant object.
            canonical (bool, optional): Only consider the canonical transcript when mapping. Defaults to False.

        Returns:
            List[RnaPosition]: If a variant was given, returns a variant, otherwise returns a position.
        """
        if isinstance(position, str):
            return self._string_to_rna(position, canonical)
        else:
            return self._position_to_rna(position, canonical)

    def to_all(self, position, canonical: bool = False) -> Dict[str, List]:
        """Map a position to all alternate positions.

        Args:
            position (Position): Position or variant object.
            canonical (bool, optional): Only consider the canonical transcript when mapping. Defaults to False.

        Returns:
            Dict[str, List]: A dictionary of cDNA, DNA, exon, protein, and RNA positions.
        """
        result = {CDNA: [], DNA: [], EXON: [], PROTEIN: [], RNA: []}  # type: ignore

        if isinstance(position, str):
            position_list = self.parse(position)
        else:
            position_list = [position]

        for position in position_list:
            result[CDNA].extend(self._position_to_cdna(position, canonical))
            result[DNA].extend(self._position_to_dna(position, canonical))
            result[EXON].extend(self._position_to_exon(position, canonical))
            result[PROTEIN].extend(self._position_to_protein(position, canonical))
            result[RNA].extend(self._position_to_rna(position, canonical))

        return result

    def _string_to_cdna(self, string: str, canonical: bool):
        return self._string_to(string, self._position_to_cdna, canonical)

    def _string_to_dna(self, string: str, canonical: bool):
        return self._string_to(string, self._position_to_dna, canonical)

    def _string_to_exon(self, string: str, canonical: bool):
        return self._string_to(string, self._position_to_exon, canonical)

    def _string_to_protein(self, string: str, canonical: bool):
        return self._string_to(string, self._position_to_protein, canonical)

    def _string_to_rna(self, string: str, canonical: bool):
        return self._string_to(string, self._position_to_rna, canonical)

    def _string_to(self, string: str, func: Callable, canonical: bool):
        result = []

        for position in self.parse(string, canonical=canonical):
            for new_position in func(position, canonical):
                if new_position not in result:
                    result.append(new_position)

        return sorted(result)

    def _position_to_cdna(self, position, canonical: bool):
        return self._position_to(
            position,
            fusionf=self._position_to_cdna,
            fusiont=CdnaFusion,
            cdnavf=self._cdna_to_cdna_variant,
            dnavf=self._dna_to_cdna_variant,
            proteinvf=self._protein_to_cdna_variant,
            rnavf=self._rna_to_cdna_variant,
            cdnaf=self._cdna_to_cdna,
            dnaf=self._dna_to_cdna,
            exonf=self._exon_to_cdna,
            proteinf=self._protein_to_cdna,
            rnaf=self._rna_to_cdna,
            canonical=canonical,
        )

    def _position_to_dna(self, position, canonical: bool):
        return self._position_to(
            position,
            fusionf=self._position_to_dna,
            fusiont=DnaFusion,
            cdnavf=self._cdna_to_dna_variant,
            dnavf=self._dna_to_dna_variant,
            proteinvf=self._protein_to_dna_variant,
            rnavf=self._rna_to_dna_variant,
            cdnaf=self._cdna_to_dna,
            dnaf=self._dna_to_dna,
            exonf=self._exon_to_dna,
            proteinf=self._protein_to_dna,
            rnaf=self._rna_to_dna,
            canonical=canonical,
        )

    def _position_to_exon(self, position, canonical: bool):
        return self._position_to(
            position,
            fusionf=self._position_to_exon,
            fusiont=ExonFusion,
            cdnavf=self._cdna_to_exon_variant,
            dnavf=self._dna_to_exon_variant,
            proteinvf=self._protein_to_exon_variant,
            rnavf=self._rna_to_exon_variant,
            cdnaf=self._cdna_to_exon,
            dnaf=self._dna_to_exon,
            exonf=self._exon_to_exon,
            proteinf=self._protein_to_exon,
            rnaf=self._rna_to_exon,
            canonical=canonical,
        )

    def _position_to_protein(self, position, canonical: bool):
        return self._position_to(
            position,
            fusionf=self._position_to_protein,
            fusiont=ProteinFusion,
            cdnavf=self._cdna_to_protein_variant,
            dnavf=self._dna_to_protein_variant,
            proteinvf=self._protein_to_protein_variant,
            rnavf=self._rna_to_protein_variant,
            cdnaf=self._cdna_to_protein,
            dnaf=self._dna_to_protein,
            exonf=self._exon_to_protein,
            proteinf=self._protein_to_protein,
            rnaf=self._rna_to_protein,
            canonical=canonical,
        )

    def _position_to_rna(self, position, canonical: bool):
        return self._position_to(
            position,
            fusionf=self._position_to_rna,
            fusiont=RnaFusion,
            cdnavf=self._cdna_to_rna_variant,
            dnavf=self._dna_to_rna_variant,
            proteinvf=self._protein_to_rna_variant,
            rnavf=self._rna_to_rna_variant,
            cdnaf=self._cdna_to_rna,
            dnaf=self._dna_to_rna,
            exonf=self._exon_to_rna,
            proteinf=self._protein_to_rna,
            rnaf=self._rna_to_rna,
            canonical=canonical,
        )

    def _position_to(
        self,
        position,
        fusionf: Callable,
        fusiont: Type,
        cdnavf: Callable,
        dnavf: Callable,
        proteinvf: Callable,
        rnavf: Callable,
        cdnaf: Callable,
        dnaf: Callable,
        exonf: Callable,
        proteinf: Callable,
        rnaf: Callable,
        canonical: bool,
    ) -> List:
        if position.is_fusion:
            fusion = cast(_Fusion, position)
            breakpoint1 = fusionf(fusion.breakpoint1, canonical)
            breakpoint2 = fusionf(fusion.breakpoint2, canonical)
            return [fusiont(b1, b2) for b1, b2 in product(breakpoint1, breakpoint2)]
        elif position.is_small_variant:
            if position.is_cdna:
                position = cast(_CdnaSmallVariant, position)
                return cdnavf(
                    [position.transcript_id],
                    position.start,
                    position.start_offset,
                    position.end,
                    position.end_offset,
                    [position.strand],
                    position.refseq,
                    position.altseq,
                    canonical,
                )
            elif position.is_dna:
                position = cast(_DnaSmallVariant, position)
                return dnavf(
                    [position.contig_id],
                    position.start,
                    position.start_offset,
                    position.end,
                    position.end_offset,
                    [position.strand],
                    position.refseq,
                    position.altseq,
                    canonical,
                )
            elif position.is_protein:
                position = cast(_ProteinSmallVariant, position)
                return proteinvf(
                    [position.transcript_id],
                    position.start,
                    position.start_offset,
                    position.end,
                    position.end_offset,
                    [position.strand],
                    position.refseq,
                    position.altseq,
                    canonical,
                )
            elif position.is_rna:
                position = cast(_RnaSmallVariant, position)
                return rnavf(
                    [position.transcript_id],
                    position.start,
                    position.start_offset,
                    position.end,
                    position.end_offset,
                    [position.strand],
                    position.refseq,
                    position.altseq,
                    canonical,
                )
        else:
            if position.is_cdna:
                position = cast(CdnaPosition, position)
                return cdnaf(
                    [position.transcript_id],
                    position.start,
                    position.start_offset,
                    position.end,
                    position.end_offset,
                    [position.strand],
                    canonical,
                )
            elif position.is_dna:
                position = cast(DnaPosition, position)
                return dnaf(
                    [position.contig_id],
                    position.start,
                    position.start_offset,
                    position.end,
                    position.end_offset,
                    [position.strand],
                    canonical,
                )
            elif position.is_exon:
                position = cast(ExonPosition, position)
                return exonf(
                    [position.transcript_id],
                    position.start,
                    position.start_offset,
                    position.end,
                    position.end_offset,
                    [position.strand],
                    canonical,
                )
            elif position.is_protein:
                position = cast(ProteinPosition, position)
                return proteinf(
                    [position.transcript_id],
                    position.start,
                    position.start_offset,
                    position.end,
                    position.end_offset,
                    [position.strand],
                    canonical,
                )
            elif position.is_rna:
                position = cast(RnaPosition, position)
                return rnaf(
                    [position.transcript_id],
                    position.start,
                    position.start_offset,
                    position.end,
                    position.end_offset,
                    [position.strand],
                    canonical,
                )

        raise AssertionError(f"Unknown position type for {position}")

    def _cdna_to_cdna(
        self,
        transcript_id: List[str],
        start: int,
        start_offset: int,
        end: int,
        end_offset: int,
        strand: List[str],
        canonical: bool = False,
        include_stop: bool = True,
    ) -> List[CdnaPosition]:
        feature = [CDS, STOP_CODON] if include_stop else [CDS]

        if canonical:
            transcript_id = [i for i in transcript_id if self.is_canonical_transcript(i)]
            if not transcript_id:
                return []

        def convert(n: int, offset: int):
            result = []

            mask = (
                (self.df[TRANSCRIPT_ID].isin(transcript_id))
                & (self.df["cdna_start"] <= n)
                & (self.df["cdna_end"] >= n)
                & (self.df["feature"].isin(feature))
            )
            for _, cds in self.df[mask].iterrows():
                # If the offset position can be normalized to a non-offset position, do so.
                # Otherwise just return an offset position.
                n_ = n + offset
                if cds.cdna_start <= n_ <= cds.cdna_end:
                    n = n_
                    offset = 0

                result.append(
                    CdnaPosition(
                        contig_id=cds.contig_id,
                        start=n,
                        start_offset=offset,
                        end=n,
                        end_offset=offset,
                        strand=cds.strand,
                        gene_id=cds.gene_id,
                        gene_name=cds.gene_name,
                        transcript_id=cds.transcript_id,
                        transcript_name=cds.transcript_name,
                        protein_id=cds.protein_id,
                    )
                )

            return result

        result_start = convert(start, start_offset)
        if (start, start_offset) == (end, end_offset):
            return sorted(result_start)
        else:
            result_end = convert(end, end_offset)
            return join_positions(result_start, result_end, TRANSCRIPT_ID)

    def _cdna_to_cdna_variant(
        self,
        transcript_id: List[str],
        start: int,
        start_offset: int,
        end: int,
        end_offset: int,
        strand: List[str],
        refseq: str,
        altseq: str,
        canonical: bool = False,
        include_stop: bool = True,
    ) -> List[_CdnaSmallVariant]:
        result = []

        for cdna in self._cdna_to_cdna(
            transcript_id,
            start,
            start_offset,
            end,
            end_offset,
            strand,
            canonical=canonical,
            include_stop=include_stop,
        ):
            result.extend(self._position_to_small_variant(cdna, refseq, altseq))

        return result

    def _cdna_to_dna(
        self,
        transcript_id: List[str],
        start: int,
        start_offset: int,
        end: int,
        end_offset: int,
        strand: List[str],
        canonical: bool = False,
        include_stop: bool = True,
    ) -> List[DnaPosition]:
        feature = [CDS, STOP_CODON] if include_stop else [CDS]

        if canonical:
            transcript_id = [i for i in transcript_id if self.is_canonical_transcript(i)]
            if not transcript_id:
                return []

        def convert(n: int, offset: int):
            result = []

            mask = (
                (self.df[TRANSCRIPT_ID].isin(transcript_id))
                & (self.df["cdna_start"] <= n)
                & (self.df["cdna_end"] >= n)
                & (self.df["feature"].isin(feature))
            )
            for _, cds in self.df[mask].iterrows():
                if cds.strand == "-":
                    new_start = new_end = cds.end - (n - cds.cdna_start) - offset
                else:
                    new_start = new_end = cds.start + (n - cds.cdna_start) + offset

                offset = 0

                # TODO: Check that new new_start is actually on the contig
                result.append(
                    DnaPosition(
                        contig_id=cds.contig_id,
                        start=new_start,
                        start_offset=offset,
                        end=new_end,
                        end_offset=offset,
                        strand=cds.strand,
                    )
                )

            return result

        result_start = convert(start, start_offset)
        if (start, start_offset) == (end, end_offset):
            return sorted(result_start)
        else:
            result_end = convert(end, end_offset)
            return join_positions(result_start, result_end, CONTIG_ID)

    def _cdna_to_dna_variant(
        self,
        transcript_id: List[str],
        start: int,
        start_offset: int,
        end: int,
        end_offset: int,
        strand: List[str],
        refseq: str,
        altseq: str,
        canonical: bool = False,
        include_stop: bool = True,
    ) -> List[_DnaSmallVariant]:
        result = []

        for dna in self._cdna_to_dna(
            transcript_id,
            start,
            start_offset,
            end,
            end_offset,
            strand,
            canonical=canonical,
            include_stop=include_stop,
        ):
            result.extend(self._position_to_small_variant(dna, refseq, altseq))

        return result

    def _cdna_to_exon(
        self,
        transcript_id: List[str],
        start: int,
        start_offset: int,
        end: int,
        end_offset: int,
        strand: List[str],
        canonical: bool = False,
        include_stop: bool = True,
    ) -> List[ExonPosition]:
        feature = [CDS, STOP_CODON] if include_stop else [CDS]

        if canonical:
            transcript_id = [i for i in transcript_id if self.is_canonical_transcript(i)]
            if not transcript_id:
                return []

        def convert(n: int, offset: int):
            result = []

            mask_cds = (
                (self.df[TRANSCRIPT_ID].isin(transcript_id))
                & (self.df["cdna_start"] <= n)
                & (self.df["cdna_end"] >= n)
                & (self.df["feature"].isin(feature))
            )
            for _, cds in self.df[mask_cds].iterrows():
                # If the offset position can be normalized to a non-offset position, do so.
                # Otherwise skip this iteration since it means that the position is not on an exon.
                n_ = n + offset
                if cds.cdna_start <= n_ <= cds.cdna_end:
                    n = n_
                    offset = 0
                else:
                    continue

                mask_exon = (
                    (self.df[TRANSCRIPT_ID].isin(transcript_id))
                    & (self.df["exon_number"] == cds.exon_number)
                    & (self.df["feature"] == EXON)
                )
                for _, exon in self.df[mask_exon].iterrows():
                    result.append(
                        ExonPosition(
                            contig_id=exon.contig_id,
                            start=int(exon.exon_number),
                            start_offset=offset,
                            end=int(exon.exon_number),
                            end_offset=offset,
                            strand=exon.strand,
                            gene_id=exon.gene_id,
                            gene_name=exon.gene_name,
                            transcript_id=exon.transcript_id,
                            transcript_name=exon.transcript_name,
                            exon_id=exon.exon_id,
                        )
                    )

            return result

        result_start = convert(start, start_offset)
        if (start, start_offset) == (end, end_offset):
            return sorted(result_start)
        else:
            result_end = convert(end, end_offset)
            return join_positions(result_start, result_end, TRANSCRIPT_ID)

    def _cdna_to_exon_variant(
        self,
        transcript_id: List[str],
        start: int,
        start_offset: int,
        end: int,
        end_offset: int,
        strand: List[str],
        refseq: str,
        altseq: str,
        canonical: bool = False,
        include_stop: bool = True,
    ) -> List[_ExonSmallVariant]:
        result = []

        for exon in self._cdna_to_exon(
            transcript_id,
            start,
            start_offset,
            end,
            end_offset,
            strand,
            canonical=canonical,
            include_stop=include_stop,
        ):
            result.extend(self._position_to_small_variant(exon, refseq, altseq))

        return result

    def _cdna_to_protein(
        self,
        transcript_id: List[str],
        start: int,
        start_offset: int,
        end: int,
        end_offset: int,
        strand: List[str],
        canonical: bool = False,
    ) -> List[ProteinPosition]:
        result = []

        for cdna in self._cdna_to_cdna(
            transcript_id,
            start,
            start_offset,
            end,
            end_offset,
            strand,
            canonical=canonical,
            include_stop=False,
        ):
            result.extend(self._cdna_to_protein_core(cdna))

        return result

    def _cdna_to_protein_core(self, cdna: CdnaPosition) -> List[ProteinPosition]:
        # If the postion wasn't mapped to a non-offset position by `_cdna_to_cdna`, it means
        # that the position does not map to a protein.
        if cdna.start_offset or cdna.end_offset:
            return []

        # Convert the cDNA position to a protein position
        protein_start = calc_cdna_to_protein(cdna.start)
        protein_end = calc_cdna_to_protein(cdna.end)
        protein = ProteinPosition.copy_from(
            cdna, start=protein_start, start_offset=0, end=protein_end, end_offset=0
        )

        return [protein]

    def _cdna_to_protein_variant(
        self,
        transcript_id: List[str],
        start: int,
        start_offset: int,
        end: int,
        end_offset: int,
        strand: List[str],
        refseq: str,
        altseq: str,
        canonical: bool = False,
    ) -> List[_ProteinSmallVariant]:
        result = []

        for cdna in self._cdna_to_cdna(
            transcript_id,
            start,
            start_offset,
            end,
            end_offset,
            strand,
            canonical=canonical,
            include_stop=False,
        ):
            result.extend(self._cdna_to_protein_variant_core(cdna, refseq, altseq))

        return result

    def _cdna_to_protein_variant_core(
        self, cdna: CdnaPosition, refseq: str, altseq: str
    ) -> List[_ProteinSmallVariant]:
        result = []

        # If the postion wasn't mapped to a non-offset position by `_cdna_to_cdna`, it means
        # that the position does not map to a protein.
        if cdna.start_offset or cdna.end_offset:
            return []

        # Skip positions where the given refseq does not match what's annotated
        if refseq != self.sequence(cdna):
            return []

        # Convert the cDNA position to a protein position
        protein_start = calc_cdna_to_protein(cdna.start)
        protein_end = calc_cdna_to_protein(cdna.end)
        protein = ProteinPosition.copy_from(
            cdna, start=protein_start, start_offset=0, end=protein_end, end_offset=0
        )
        refaa = self.sequence(protein)
        for altaa, is_frameshift in self.translate_cdna_variant(cdna, altseq):
            # TODO: Support frameshift variants
            result.extend(
                self._position_to_small_variant(protein, refaa, altaa, is_frameshift=is_frameshift)
            )

        return result

    def _cdna_to_rna(
        self,
        transcript_id: List[str],
        start: int,
        start_offset: int,
        end: int,
        end_offset: int,
        strand: List[str],
        canonical: bool = False,
        include_stop: bool = True,
    ) -> List[RnaPosition]:
        feature = [CDS, STOP_CODON] if include_stop else [CDS]

        if canonical:
            transcript_id = [i for i in transcript_id if self.is_canonical_transcript(i)]
            if not transcript_id:
                return []

        def convert(n: int, offset: int):
            result = []

            mask = (
                (self.df[TRANSCRIPT_ID].isin(transcript_id))
                & (self.df["cdna_start"] <= n)
                & (self.df["cdna_end"] >= n)
                & (self.df["feature"].isin(feature))
            )
            for _, cds in self.df[mask].iterrows():
                # If the offset position can be normalized to a non-offset position, do so.
                # Otherwise just return an offset position.
                n_ = n + offset
                if cds.cdna_start <= n_ <= cds.cdna_end:
                    n = n_
                    offset = 0

                new_start = new_end = cds.transcript_start + (n - cds.cdna_start)
                result.append(
                    RnaPosition(
                        contig_id=cds.contig_id,
                        start=new_start,
                        start_offset=offset,
                        end=new_end,
                        end_offset=offset,
                        strand=cds.strand,
                        gene_id=cds.gene_id,
                        gene_name=cds.gene_name,
                        transcript_id=cds.transcript_id,
                        transcript_name=cds.transcript_name,
                    )
                )

            return result

        result_start = convert(start, start_offset)
        if (start, start_offset) == (end, end_offset):
            return sorted(result_start)
        else:
            result_end = convert(end, end_offset)
            return join_positions(result_start, result_end, TRANSCRIPT_ID)

    def _cdna_to_rna_variant(
        self,
        transcript_id: List[str],
        start: int,
        start_offset: int,
        end: int,
        end_offset: int,
        strand: List[str],
        refseq: str,
        altseq: str,
        canonical: bool = False,
        include_stop: bool = True,
    ) -> List[_RnaSmallVariant]:
        result = []

        for rna in self._cdna_to_rna(
            transcript_id,
            start,
            start_offset,
            end,
            end_offset,
            strand,
            canonical=canonical,
            include_stop=include_stop,
        ):
            result.extend(self._position_to_small_variant(rna, refseq, altseq))

        return result

    def _dna_to_cdna(
        self,
        contig_id: List[str],
        start: int,
        start_offset: int,
        end: int,
        end_offset: int,
        strand: List[str],
        canonical: bool = False,
        include_stop: bool = True,
    ) -> List[CdnaPosition]:
        feature = [CDS, STOP_CODON] if include_stop else [CDS]

        def convert(n: int, offset: int):
            result = []

            for strand_ in strand:
                n_ = (n - offset) if strand_ == "-" else (n + offset)
                offset = 0

                mask = (
                    (self.df[CONTIG_ID].isin(contig_id))
                    & (self.df["start"] <= n_)
                    & (self.df["end"] >= n_)
                    & (self.df["feature"].isin(feature))
                )
                if strand_:
                    mask = mask & (self.df["strand"] == strand_)

                for _, cds in self.df[mask].iterrows():
                    if cds.strand == "-":
                        new_start = new_end = cds.end - n_ + cds.cdna_start
                    else:
                        new_start = new_end = n_ - cds.start + cds.cdna_start

                    if canonical and not self.is_canonical_transcript(cds.transcript_id):
                        continue

                    result.append(
                        CdnaPosition(
                            contig_id=cds.contig_id,
                            start=new_start,
                            start_offset=offset,
                            end=new_end,
                            end_offset=offset,
                            strand=cds.strand,
                            gene_id=cds.gene_id,
                            gene_name=cds.gene_name,
                            transcript_id=cds.transcript_id,
                            transcript_name=cds.transcript_name,
                            protein_id=cds.protein_id,
                        )
                    )

            return result

        result_start = convert(start, start_offset)
        if (start, start_offset) == (end, end_offset):
            return sorted(result_start)
        else:
            result_end = convert(end, end_offset)
            return join_positions(result_start, result_end, TRANSCRIPT_ID)

    def _dna_to_cdna_variant(
        self,
        contig_id: List[str],
        start: int,
        start_offset: int,
        end: int,
        end_offset: int,
        strand: List[str],
        refseq: str,
        altseq: str,
        canonical: bool = False,
        include_stop: bool = True,
    ) -> List[_CdnaSmallVariant]:
        result = []

        for cdna in self._dna_to_cdna(
            contig_id,
            start,
            start_offset,
            end,
            end_offset,
            strand,
            canonical=canonical,
            include_stop=include_stop,
        ):
            result.extend(self._position_to_small_variant(cdna, refseq, altseq))

        return result

    def _dna_to_dna(
        self,
        contig_id: List[str],
        start: int,
        start_offset: int,
        end: int,
        end_offset: int,
        strand: List[str],
        canonical: bool = False,
    ) -> List[DnaPosition]:
        result = []

        # TODO: Check that new new_start is actually on the contig
        for contig_id_, strand_ in product(contig_id, strand):
            if strand_ == "-":
                new_start = start - start_offset
                new_end = end - end_offset
            else:
                new_start = start + start_offset
                new_end = end + end_offset

            start_offset = 0
            end_offset = 0

            # Sort the start and end positions after adjusting by offsets
            new_start, new_end = sorted([new_start, new_end])

            result.append(
                DnaPosition(
                    contig_id=contig_id_,
                    start=new_start,
                    start_offset=start_offset,
                    end=new_end,
                    end_offset=end_offset,
                    strand=strand_,
                )
            )

        return result

    def _dna_to_dna_variant(
        self,
        contig_id: List[str],
        start: int,
        start_offset: int,
        end: int,
        end_offset: int,
        strand: List[str],
        refseq: str,
        altseq: str,
        canonical: bool = False,
    ) -> List[_DnaSmallVariant]:
        result = []

        for dna in self._dna_to_dna(
            contig_id, start, start_offset, end, end_offset, strand, canonical=canonical
        ):
            result.extend(self._position_to_small_variant(dna, refseq, altseq))

        return result

    def _dna_to_exon(
        self,
        contig_id: List[str],
        start: int,
        start_offset: int,
        end: int,
        end_offset: int,
        strand: List[str],
        canonical: bool = False,
    ) -> List[ExonPosition]:
        def convert(n: int, offset: int):
            result = []

            for strand_ in strand:
                n_ = (n - offset) if strand_ == "-" else (n + offset)
                offset = 0

                mask = (
                    (self.df[CONTIG_ID].isin(contig_id))
                    & (self.df["start"] <= n_)
                    & (self.df["end"] >= n_)
                    & (self.df["feature"] == EXON)
                )
                if strand_:
                    mask = mask & (self.df["strand"] == strand_)

                for _, exon in self.df[mask].iterrows():
                    if canonical and not self.is_canonical_transcript(exon.transcript_id):
                        continue

                    result.append(
                        ExonPosition(
                            contig_id=exon.contig_id,
                            start=int(exon.exon_number),
                            start_offset=offset,
                            end=int(exon.exon_number),
                            end_offset=offset,
                            strand=exon.strand,
                            gene_id=exon.gene_id,
                            gene_name=exon.gene_name,
                            transcript_id=exon.transcript_id,
                            transcript_name=exon.transcript_name,
                            exon_id=exon.exon_id,
                        )
                    )

            return result

        result_start = convert(start, start_offset)
        if (start, start_offset) == (end, end_offset):
            return sorted(result_start)
        else:
            result_end = convert(end, end_offset)
            return join_positions(result_start, result_end, TRANSCRIPT_ID)

    def _dna_to_exon_variant(
        self,
        contig_id: List[str],
        start: int,
        start_offset: int,
        end: int,
        end_offset: int,
        strand: List[str],
        refseq: str,
        altseq: str,
        canonical: bool = False,
    ) -> List[_ExonSmallVariant]:
        result = []

        for exon in self._dna_to_exon(
            contig_id, start, start_offset, end, end_offset, strand, canonical=canonical
        ):
            result.extend(self._position_to_small_variant(exon, refseq, altseq))

        return result

    def _dna_to_protein(
        self,
        contig_id: List[str],
        start: int,
        start_offset: int,
        end: int,
        end_offset: int,
        strand: List[str],
        canonical: bool = False,
    ) -> List[ProteinPosition]:
        result = []

        for cdna in self._dna_to_cdna(
            contig_id,
            start,
            start_offset,
            end,
            end_offset,
            strand,
            canonical=canonical,
            include_stop=False,
        ):
            result.extend(self._cdna_to_protein_core(cdna))

        return result

    def _dna_to_protein_variant(
        self,
        contig_id: List[str],
        start: int,
        start_offset: int,
        end: int,
        end_offset: int,
        strand: List[str],
        refseq: str,
        altseq: str,
        canonical: bool = False,
    ) -> List[_ProteinSmallVariant]:
        result = []

        for cdna in self._dna_to_cdna(
            contig_id,
            start,
            start_offset,
            end,
            end_offset,
            strand,
            canonical=canonical,
            include_stop=False,
        ):
            result.extend(self._cdna_to_protein_variant_core(cdna, refseq, altseq))

        return result

    def _dna_to_rna(
        self,
        contig_id: List[str],
        start: int,
        start_offset: int,
        end: int,
        end_offset: int,
        strand: List[str],
        canonical: bool = False,
    ) -> List[RnaPosition]:
        def convert(n: int, offset: int):
            result = []

            for strand_ in strand:
                n_ = (n - offset) if strand_ == "-" else (n + offset)
                offset = 0

                mask = (
                    (self.df[CONTIG_ID].isin(contig_id))
                    & (self.df["start"] <= n_)
                    & (self.df["end"] >= n_)
                    & (self.df["feature"] == EXON)
                )
                if strand_:
                    mask = mask & (self.df["strand"] == strand_)

                for _, exon in self.df[mask].iterrows():
                    if exon.strand == "-":
                        new_start = new_end = exon.end - n_ + exon.transcript_start
                    else:
                        new_start = new_end = n_ - exon.start + exon.transcript_start

                    if canonical and not self.is_canonical_transcript(exon.transcript_id):
                        continue

                    result.append(
                        RnaPosition(
                            contig_id=exon.contig_id,
                            start=new_start,
                            start_offset=offset,
                            end=new_end,
                            end_offset=offset,
                            strand=exon.strand,
                            gene_id=exon.gene_id,
                            gene_name=exon.gene_name,
                            transcript_id=exon.transcript_id,
                            transcript_name=exon.transcript_name,
                        )
                    )

            return result

        result_start = convert(start, start_offset)
        if (start, start_offset) == (end, end_offset):
            return sorted(result_start)
        else:
            result_end = convert(end, end_offset)
            return join_positions(result_start, result_end, TRANSCRIPT_ID)

    def _dna_to_rna_variant(
        self,
        contig_id: List[str],
        start: int,
        start_offset: int,
        end: int,
        end_offset: int,
        strand: List[str],
        refseq: str,
        altseq: str,
        canonical: bool = False,
    ) -> List[_RnaSmallVariant]:
        result = []

        for rna in self._dna_to_rna(
            contig_id, start, start_offset, end, end_offset, strand, canonical=canonical
        ):
            result.extend(self._position_to_small_variant(rna, refseq, altseq))

        return result

    def _exon_to_cdna(
        self,
        transcript_id: List[str],
        start: int,
        start_offset: int,
        end: int,
        end_offset: int,
        strand: List[str],
        canonical: bool = False,
        include_stop: bool = True,
    ) -> List[CdnaPosition]:
        feature = [CDS, STOP_CODON] if include_stop else [CDS]

        if canonical:
            transcript_id = [i for i in transcript_id if self.is_canonical_transcript(i)]
            if not transcript_id:
                return []

        def convert(n: int, offset: int):
            result = []

            # TODO: Is there a reasonable case where an exon position would have an offset?
            assert not offset, offset

            mask = (
                (self.df[TRANSCRIPT_ID].isin(transcript_id))
                & (self.df["exon_number"] == float(n))
                & (self.df["feature"].isin(feature))
            )
            for _, cds in self.df[mask].iterrows():
                result.append(
                    CdnaPosition(
                        contig_id=cds.contig_id,
                        start=cds.cdna_start,
                        start_offset=offset,
                        end=cds.cdna_end,
                        end_offset=offset,
                        strand=cds.strand,
                        gene_id=cds.gene_id,
                        gene_name=cds.gene_name,
                        transcript_id=cds.transcript_id,
                        transcript_name=cds.transcript_name,
                        protein_id=cds.protein_id,
                    )
                )

            return result

        result_start = convert(start, start_offset)
        if (start, start_offset) == (end, end_offset):
            return sorted(result_start)
        else:
            result_end = convert(end, end_offset)
            return join_positions(result_start, result_end, TRANSCRIPT_ID)

    def _exon_to_dna(
        self,
        transcript_id: List[str],
        start: int,
        start_offset: int,
        end: int,
        end_offset: int,
        strand: List[str],
        canonical: bool = False,
    ) -> List[DnaPosition]:
        if canonical:
            transcript_id = [i for i in transcript_id if self.is_canonical_transcript(i)]
            if not transcript_id:
                return []

        def convert(n: int, offset: int):
            result = []

            # TODO: Is there a reasonable case where an exon position would have an offset?
            assert not offset, offset

            mask = (
                (self.df[TRANSCRIPT_ID].isin(transcript_id))
                & (self.df["exon_number"] == float(n))
                & (self.df["feature"] == EXON)
            )
            for _, exon in self.df[mask].iterrows():
                result.append(
                    DnaPosition(
                        contig_id=exon.contig_id,
                        start=exon.start,
                        start_offset=offset,
                        end=exon.end,
                        end_offset=offset,
                        strand=exon.strand,
                    )
                )

            return result

        result_start = convert(start, start_offset)
        if (start, start_offset) == (end, end_offset):
            return sorted(result_start)
        else:
            result_end = convert(end, end_offset)
            return join_positions(result_start, result_end, CONTIG_ID)

    def _exon_to_exon(
        self,
        transcript_id: List[str],
        start: int,
        start_offset: int,
        end: int,
        end_offset: int,
        strand: List[str],
        canonical: bool = False,
    ) -> List[ExonPosition]:
        if canonical:
            transcript_id = [i for i in transcript_id if self.is_canonical_transcript(i)]
            if not transcript_id:
                return []

        def convert(n: int, offset):
            result = []

            # TODO: Is there a reasonable case where an exon position would have an offset?
            assert not offset, offset

            mask = (
                (self.df[TRANSCRIPT_ID].isin(transcript_id))
                & (self.df["exon_number"] == float(n))
                & (self.df["feature"] == EXON)
            )
            for _, exon in self.df[mask].iterrows():
                result.append(
                    ExonPosition(
                        contig_id=exon.contig_id,
                        start=int(exon.exon_number),
                        start_offset=offset,
                        end=int(exon.exon_number),
                        end_offset=offset,
                        strand=exon.strand,
                        gene_id=exon.gene_id,
                        gene_name=exon.gene_name,
                        transcript_id=exon.transcript_id,
                        transcript_name=exon.transcript_name,
                        exon_id=exon.exon_id,
                    )
                )

            return result

        result_start = convert(start, start_offset)
        if (start, start_offset) == (end, end_offset):
            return sorted(result_start)
        else:
            result_end = convert(end, end_offset)
            return join_positions(result_start, result_end, TRANSCRIPT_ID)

    def _exon_to_protein(
        self,
        transcript_id: List[str],
        start: int,
        start_offset: int,
        end: int,
        end_offset: int,
        strand: List[str],
        canonical: bool = False,
    ) -> List[ProteinPosition]:
        result = []

        for cdna in self._exon_to_cdna(
            transcript_id,
            start,
            start_offset,
            end,
            end_offset,
            strand,
            canonical=canonical,
            include_stop=False,
        ):
            result.extend(
                self._cdna_to_protein(
                    [cdna.transcript_id],
                    cdna.start,
                    cdna.start_offset,
                    cdna.end,
                    cdna.end_offset,
                    [cdna.strand],
                    canonical=canonical,
                )
            )

        return result

    def _exon_to_rna(
        self,
        transcript_id: List[str],
        start: int,
        start_offset: int,
        end: int,
        end_offset: int,
        strand: List[str],
        canonical: bool = False,
    ) -> List[RnaPosition]:
        if canonical:
            transcript_id = [i for i in transcript_id if self.is_canonical_transcript(i)]
            if not transcript_id:
                return []

        def convert(n: int, offset: int):
            result = []

            # TODO: Is there a reasonable case where an exon position would have an offset?
            assert not offset, offset

            mask = (
                (self.df[TRANSCRIPT_ID].isin(transcript_id))
                & (self.df["exon_number"] == float(n))
                & (self.df["feature"] == EXON)
            )
            for _, exon in self.df[mask].iterrows():
                result.append(
                    RnaPosition(
                        contig_id=exon.contig_id,
                        start=exon.transcript_start,
                        start_offset=offset,
                        end=exon.transcript_end,
                        end_offset=offset,
                        strand=exon.strand,
                        gene_id=exon.gene_id,
                        gene_name=exon.gene_name,
                        transcript_id=exon.transcript_id,
                        transcript_name=exon.transcript_name,
                    )
                )

            return result

        result_start = convert(start, start_offset)
        if (start, start_offset) == (end, end_offset):
            return sorted(result_start)
        else:
            result_end = convert(end, end_offset)
            return join_positions(result_start, result_end, TRANSCRIPT_ID)

    def _protein_to_cdna(
        self,
        transcript_id: List[str],
        start: int,
        start_offset: int,
        end: int,
        end_offset: int,
        strand: List[str],
        canonical: bool = False,
    ) -> List[CdnaPosition]:
        def convert(n: int):
            return ((n - 1) * 3) + 1

        # TODO: Is there a reasonable case where an protein position would have an offset?
        assert not start_offset, start_offset
        assert not end_offset, end_offset

        cdna_start = convert(start)
        cdna_end = convert(end) + 2

        return self._cdna_to_cdna(
            transcript_id,
            cdna_start,
            start_offset,
            cdna_end,
            end_offset,
            strand,
            canonical=canonical,
        )

    def _protein_to_cdna_variant(
        self,
        transcript_id: List[str],
        start: int,
        start_offset: int,
        end: int,
        end_offset: int,
        strand: List[str],
        refseq: str,
        altseq: str,
        canonical: bool = False,
    ) -> List[_CdnaSmallVariant]:
        result = []

        for cdna in self._protein_to_cdna(
            transcript_id, start, start_offset, end, end_offset, strand, canonical=canonical
        ):
            for ref, alt in product(reverse_translate(refseq), reverse_translate(altseq)):
                # For insertions, check that the sequence flanking the inserted sequence matches the ref
                if is_insertion(refseq, altseq) and not is_insertion(ref, alt):
                    continue

                result.extend(self._position_to_small_variant(cdna, ref, alt, validate=True))

        return result

    def _protein_to_dna(
        self,
        transcript_id: List[str],
        start: int,
        start_offset: int,
        end: int,
        end_offset: int,
        strand: List[str],
        canonical: bool = False,
    ) -> List[DnaPosition]:
        result = []

        for cdna in self._protein_to_cdna(
            transcript_id, start, start_offset, end, end_offset, strand, canonical=canonical
        ):
            result.extend(
                self._cdna_to_dna(
                    [cdna.transcript_id],
                    cdna.start,
                    cdna.start_offset,
                    cdna.end,
                    cdna.end_offset,
                    [cdna.strand],
                    canonical=canonical,
                )
            )

        return sorted(set(result))

    def _protein_to_dna_variant(
        self,
        transcript_id: List[str],
        start: int,
        start_offset: int,
        end: int,
        end_offset: int,
        strand: List[str],
        refseq: str,
        altseq: str,
        canonical: bool = False,
    ) -> List[_DnaSmallVariant]:
        result = []

        for cdna in self._protein_to_cdna_variant(
            transcript_id,
            start,
            start_offset,
            end,
            end_offset,
            strand,
            refseq,
            altseq,
            canonical=canonical,
        ):
            result.extend(
                self._cdna_to_dna_variant(
                    [cdna.transcript_id],
                    cdna.start,
                    cdna.start_offset,
                    cdna.end,
                    cdna.end_offset,
                    [cdna.strand],
                    cdna.refseq,
                    cdna.altseq,
                    canonical=canonical,
                    include_stop=True,
                )
            )

        return sorted(set(result))

    def _protein_to_exon(
        self,
        transcript_id: List[str],
        start: int,
        start_offset: int,
        end: int,
        end_offset: int,
        strand: List[str],
        canonical: bool = False,
    ) -> List[ExonPosition]:
        result = []

        for cdna in self._protein_to_cdna(
            transcript_id, start, start_offset, end, end_offset, strand, canonical=canonical
        ):
            result.extend(
                self._cdna_to_exon(
                    [cdna.transcript_id],
                    cdna.start,
                    cdna.start_offset,
                    cdna.end,
                    cdna.end_offset,
                    [cdna.strand],
                    canonical=canonical,
                )
            )

        return sorted(set(result))

    def _protein_to_exon_variant(
        self,
        transcript_id: List[str],
        start: int,
        start_offset: int,
        end: int,
        end_offset: int,
        strand: List[str],
        refseq: str,
        altseq: str,
        canonical: bool = False,
    ) -> List[_ExonSmallVariant]:
        result = []

        for cdna in self._protein_to_cdna_variant(
            transcript_id,
            start,
            start_offset,
            end,
            end_offset,
            strand,
            refseq,
            altseq,
            canonical=canonical,
        ):
            result.extend(
                self._cdna_to_exon_variant(
                    [cdna.transcript_id],
                    cdna.start,
                    cdna.start_offset,
                    cdna.end,
                    cdna.end_offset,
                    [cdna.strand],
                    cdna.refseq,
                    cdna.altseq,
                    canonical=canonical,
                    include_stop=True,
                )
            )

        return sorted(set(result))

    def _protein_to_protein(
        self,
        transcript_id: List[str],
        start: int,
        start_offset: int,
        end: int,
        end_offset: int,
        strand: List[str],
        canonical: bool = False,
    ) -> List[ProteinPosition]:
        result = []

        for cdna in self._protein_to_cdna(
            transcript_id, start, start_offset, end, end_offset, strand, canonical=canonical
        ):
            result.extend(
                self._cdna_to_protein(
                    [cdna.transcript_id],
                    cdna.start,
                    cdna.start_offset,
                    cdna.end,
                    cdna.end_offset,
                    [cdna.strand],
                    canonical=canonical,
                )
            )

        return sorted(set(result))

    def _protein_to_protein_variant(
        self,
        transcript_id: List[str],
        start: int,
        start_offset: int,
        end: int,
        end_offset: int,
        strand: List[str],
        refseq: str,
        altseq: str,
        canonical: bool = False,
    ) -> List[_ProteinSmallVariant]:
        result = []

        for cdna in self._protein_to_cdna_variant(
            transcript_id,
            start,
            start_offset,
            end,
            end_offset,
            strand,
            refseq,
            altseq,
            canonical=canonical,
        ):
            result.extend(
                self._cdna_to_protein_variant(
                    [cdna.transcript_id],
                    cdna.start,
                    cdna.start_offset,
                    cdna.end,
                    cdna.end_offset,
                    [cdna.strand],
                    cdna.refseq,
                    cdna.altseq,
                    canonical=canonical,
                )
            )

        return sorted(set(result))

    def _protein_to_rna(
        self,
        transcript_id: List[str],
        start: int,
        start_offset: int,
        end: int,
        end_offset: int,
        strand: List[str],
        canonical: bool = False,
    ) -> List[RnaPosition]:
        result = []

        for cdna in self._protein_to_cdna(
            transcript_id, start, start_offset, end, end_offset, strand, canonical=canonical
        ):
            result.extend(
                self._cdna_to_rna(
                    [cdna.transcript_id],
                    cdna.start,
                    cdna.start_offset,
                    cdna.end,
                    cdna.end_offset,
                    [cdna.strand],
                    canonical=canonical,
                )
            )

        return sorted(set(result))

    def _protein_to_rna_variant(
        self,
        transcript_id: List[str],
        start: int,
        start_offset: int,
        end: int,
        end_offset: int,
        strand: List[str],
        refseq: str,
        altseq: str,
        canonical: bool = False,
    ) -> List[_RnaSmallVariant]:
        result = []

        for cdna in self._protein_to_cdna_variant(
            transcript_id,
            start,
            start_offset,
            end,
            end_offset,
            strand,
            refseq,
            altseq,
            canonical=canonical,
        ):
            result.extend(
                self._cdna_to_rna_variant(
                    [cdna.transcript_id],
                    cdna.start,
                    cdna.start_offset,
                    cdna.end,
                    cdna.end_offset,
                    [cdna.strand],
                    cdna.refseq,
                    cdna.altseq,
                    canonical=canonical,
                )
            )

        return sorted(set(result))

    def _rna_to_cdna(
        self,
        transcript_id: List[str],
        start: int,
        start_offset: int,
        end: int,
        end_offset: int,
        strand: List[str],
        canonical: bool = False,
        include_stop: bool = True,
    ) -> List[CdnaPosition]:
        feature = [CDS, STOP_CODON] if include_stop else [CDS]

        if canonical:
            transcript_id = [i for i in transcript_id if self.is_canonical_transcript(i)]
            if not transcript_id:
                return []

        def convert(n: int, offset: int):
            result = []

            mask = (
                (self.df[TRANSCRIPT_ID].isin(transcript_id))
                & (self.df["transcript_start"] <= n)
                & (self.df["transcript_end"] >= n)
                & (self.df["feature"].isin(feature))
            )
            for _, cds in self.df[mask].iterrows():
                # If the offset position can be normalized to a non-offset position, do so.
                # Otherwise just return an offset position.
                n_ = n + offset
                if cds.cdna_start <= n_ <= cds.cdna_end:
                    n = n_
                    offset = 0

                new_start = new_end = cds.cdna_start + (n - cds.transcript_start)
                result.append(
                    CdnaPosition(
                        contig_id=cds.contig_id,
                        start=new_start,
                        start_offset=offset,
                        end=new_end,
                        end_offset=offset,
                        strand=cds.strand,
                        gene_id=cds.gene_id,
                        gene_name=cds.gene_name,
                        transcript_id=cds.transcript_id,
                        transcript_name=cds.transcript_name,
                        protein_id=cds.protein_id,
                    )
                )

            return result

        result_start = convert(start, start_offset)
        if (start, start_offset) == (end, end_offset):
            return sorted(result_start)
        else:
            result_end = convert(end, end_offset)
            return join_positions(result_start, result_end, TRANSCRIPT_ID)

    def _rna_to_cdna_variant(
        self,
        transcript_id: List[str],
        start: int,
        start_offset: int,
        end: int,
        end_offset: int,
        strand: List[str],
        refseq: str,
        altseq: str,
        canonical: bool = False,
        include_stop: bool = True,
    ) -> List[_CdnaSmallVariant]:
        result = []

        for cdna in self._rna_to_cdna(
            transcript_id,
            start,
            start_offset,
            end,
            end_offset,
            strand,
            canonical=canonical,
            include_stop=include_stop,
        ):
            result.extend(self._position_to_small_variant(cdna, refseq, altseq))

        return result

    def _rna_to_dna(
        self,
        transcript_id: List[str],
        start: int,
        start_offset: int,
        end: int,
        end_offset: int,
        strand: List[str],
        canonical: bool = False,
    ) -> List[DnaPosition]:
        if canonical:
            transcript_id = [i for i in transcript_id if self.is_canonical_transcript(i)]
            if not transcript_id:
                return []

        def convert(n: int, offset: int):
            result = []

            mask = (
                (self.df[TRANSCRIPT_ID].isin(transcript_id))
                & (self.df["transcript_start"] <= n)
                & (self.df["transcript_end"] >= n)
                & (self.df["feature"] == EXON)
            )
            exon_df = self.df[mask]
            for _, exon in exon_df.iterrows():
                if exon.strand == "-":
                    new_start = new_end = exon.end - (n - exon.transcript_start) - offset
                else:
                    new_start = new_end = exon.start + (n - exon.transcript_start) + offset

                offset = 0

                # TODO: Check that new new_start is actually on the contig
                result.append(
                    DnaPosition(
                        contig_id=exon.contig_id,
                        start=new_start,
                        start_offset=offset,
                        end=new_end,
                        end_offset=offset,
                        strand=exon.strand,
                    )
                )

            return result

        result_start = convert(start, start_offset)
        if (start, start_offset) == (end, end_offset):
            return sorted(result_start)
        else:
            result_end = convert(end, end_offset)
            return join_positions(result_start, result_end, CONTIG_ID)

    def _rna_to_dna_variant(
        self,
        transcript_id: List[str],
        start: int,
        start_offset: int,
        end: int,
        end_offset: int,
        strand: List[str],
        refseq: str,
        altseq: str,
        canonical: bool = False,
    ) -> List[_DnaSmallVariant]:
        result = []

        for dna in self._rna_to_dna(
            transcript_id, start, start_offset, end, end_offset, strand, canonical=canonical
        ):
            result.extend(self._position_to_small_variant(dna, refseq, altseq))

        return result

    def _rna_to_exon(
        self,
        transcript_id: List[str],
        start: int,
        start_offset: int,
        end: int,
        end_offset: int,
        strand: List[str],
        canonical: bool = False,
    ) -> List[ExonPosition]:
        if canonical:
            transcript_id = [i for i in transcript_id if self.is_canonical_transcript(i)]
            if not transcript_id:
                return []

        def convert(n: int, offset: int):
            result = []

            mask = (
                (self.df[TRANSCRIPT_ID].isin(transcript_id))
                & (self.df["transcript_start"] <= n)
                & (self.df["transcript_end"] >= n)
                & (self.df["feature"] == EXON)
            )
            for _, exon in self.df[mask].iterrows():
                # If the offset position can be normalized to a non-offset position, do so.
                # Otherwise skip this iteration since it means that the position is not on an exon.
                n_ = n + offset
                if exon.transcript_start <= n_ <= exon.transcript_end:
                    n = n_
                    offset = 0
                else:
                    continue

                result.append(
                    ExonPosition(
                        contig_id=exon.contig_id,
                        start=int(exon.exon_number),
                        start_offset=offset,
                        end=int(exon.exon_number),
                        end_offset=offset,
                        strand=exon.strand,
                        gene_id=exon.gene_id,
                        gene_name=exon.gene_name,
                        transcript_id=exon.transcript_id,
                        transcript_name=exon.transcript_name,
                        exon_id=exon.exon_id,
                    )
                )

            return result

        result_start = convert(start, start_offset)
        if (start, start_offset) == (end, end_offset):
            return sorted(result_start)
        else:
            result_end = convert(end, end_offset)
            return join_positions(result_start, result_end, TRANSCRIPT_ID)

    def _rna_to_exon_variant(
        self,
        transcript_id: List[str],
        start: int,
        start_offset: int,
        end: int,
        end_offset: int,
        strand: List[str],
        refseq: str,
        altseq: str,
        canonical: bool = False,
    ) -> List[_ExonSmallVariant]:
        result = []

        for exon in self._rna_to_exon(
            transcript_id, start, start_offset, end, end_offset, strand, canonical=canonical
        ):
            result.extend(self._position_to_small_variant(exon, refseq, altseq))

        return result

    def _rna_to_protein(
        self,
        transcript_id: List[str],
        start: int,
        start_offset: int,
        end: int,
        end_offset: int,
        strand: List[str],
        canonical: bool = False,
    ) -> List[ProteinPosition]:
        result = []

        for cdna in self._rna_to_cdna(
            transcript_id,
            start,
            start_offset,
            end,
            end_offset,
            strand,
            canonical=canonical,
            include_stop=False,
        ):
            result.extend(
                self._cdna_to_protein(
                    [cdna.transcript_id],
                    cdna.start,
                    cdna.start_offset,
                    cdna.end,
                    cdna.end_offset,
                    [cdna.strand],
                    canonical=canonical,
                )
            )

        return sorted(set(result))

    def _rna_to_protein_variant(
        self,
        transcript_id: List[str],
        start: int,
        start_offset: int,
        end: int,
        end_offset: int,
        strand: List[str],
        refseq: str,
        altseq: str,
        canonical: bool = False,
    ) -> List[_ProteinSmallVariant]:
        result = []

        for cdna in self._rna_to_cdna_variant(
            transcript_id,
            start,
            start_offset,
            end,
            end_offset,
            strand,
            refseq,
            altseq,
            canonical=canonical,
            include_stop=False,
        ):
            result.extend(
                self._cdna_to_protein_variant(
                    [cdna.transcript_id],
                    cdna.start,
                    cdna.start_offset,
                    cdna.end,
                    cdna.end_offset,
                    [cdna.strand],
                    cdna.refseq,
                    cdna.altseq,
                    canonical=canonical,
                )
            )

        return sorted(set(result))

    def _rna_to_rna(
        self,
        transcript_id: List[str],
        start: int,
        start_offset: int,
        end: int,
        end_offset: int,
        strand: List[str],
        canonical: bool = False,
    ) -> List[RnaPosition]:
        if canonical:
            transcript_id = [i for i in transcript_id if self.is_canonical_transcript(i)]
            if not transcript_id:
                return []

        def convert(n: int, offset: int):
            result = []

            mask = (
                (self.df[TRANSCRIPT_ID].isin(transcript_id))
                & (self.df["transcript_start"] <= n)
                & (self.df["transcript_end"] >= n)
                & (self.df["feature"] == EXON)
            )
            for _, exon in self.df[mask].iterrows():
                # If the offset position can be normalized to a non-offset position, do so.
                # Otherwise just return an offset position.
                n_ = n + offset
                if exon.transcript_start <= n_ <= exon.transcript_end:
                    n = n_
                    offset = 0

                result.append(
                    RnaPosition(
                        contig_id=exon.contig_id,
                        start=n,
                        start_offset=offset,
                        end=n,
                        end_offset=offset,
                        strand=exon.strand,
                        gene_id=exon.gene_id,
                        gene_name=exon.gene_name,
                        transcript_id=exon.transcript_id,
                        transcript_name=exon.transcript_name,
                    )
                )

            return result

        result_start = convert(start, start_offset)
        if (start, start_offset) == (end, end_offset):
            return sorted(result_start)
        else:
            result_end = convert(end, end_offset)
            return join_positions(result_start, result_end, TRANSCRIPT_ID)

    def _rna_to_rna_variant(
        self,
        transcript_id: List[str],
        start: int,
        start_offset: int,
        end: int,
        end_offset: int,
        strand: List[str],
        refseq: str,
        altseq: str,
        canonical: bool = False,
    ) -> List[_RnaSmallVariant]:
        result = []

        for rna in self._rna_to_rna(
            transcript_id, start, start_offset, end, end_offset, strand, canonical=canonical
        ):
            result.extend(self._position_to_small_variant(rna, refseq, altseq))

        return result

    def _position_to_small_variant(
        self,
        position: _Position,
        refseq: str,
        altseq: str,
        is_frameshift: bool = False,
        validate: bool = False,
    ) -> List:
        """Convert an position plus reference and alternate alleles into a variant.

        Args:
            position (_Position): Position
            refseq (str): Reference allele, amino acids if the position is protein otherwise nucleotides
            altseq (str): Alternate allele, amino acids if the position is protein otherwise nucleotides
            is_frameshift (str): Sequence change results in a frameshift
            validate (bool): Check that the given refseq matches the annotated sequence

        Raises:
            NotImplementedError: An unsupported combination of feature/alternate alleles was given
            ValueError: The given feature allele does not match the annotated feature allele

        Returns:
            List: One or more variants
        """
        variant_list = []

        variant_class: Optional[Type[_SmallVariant]] = None
        variant_class_map: Dict[Tuple, Type[_SmallVariant]] = {
            (CDNA, DELETION): CdnaDeletion,
            (CDNA, DELINS): CdnaDelins,
            (CDNA, DUPLICATION): CdnaDuplication,
            (CDNA, INSERTION): CdnaInsertion,
            (CDNA, SUBSTITUTION): CdnaSubstitution,
            (DNA, DELETION): DnaDeletion,
            (DNA, DELINS): DnaDelins,
            (DNA, DUPLICATION): DnaDuplication,
            (DNA, INSERTION): DnaInsertion,
            (DNA, SUBSTITUTION): DnaSubstitution,
            (PROTEIN, DELETION): ProteinDeletion,
            (PROTEIN, DELINS): ProteinDelins,
            (PROTEIN, DUPLICATION): ProteinDuplication,
            (PROTEIN, FRAMESHIFT): ProteinFrameshift,
            (PROTEIN, INSERTION): ProteinInsertion,
            (PROTEIN, SUBSTITUTION): ProteinSubstitution,
            (RNA, DELETION): RnaDeletion,
            (RNA, DELINS): RnaDelins,
            (RNA, DUPLICATION): RnaDuplication,
            (RNA, INSERTION): RnaInsertion,
            (RNA, SUBSTITUTION): RnaSubstitution,
        }

        # Select the function to use to expand ambiguous sequences
        if position.is_protein:
            expand = expand_pep
        else:
            expand = expand_nt

        for ref, alt in product(expand(refseq), expand(altseq)):
            # Optionally, assert that the given ref matches the annotated one
            if validate:
                try:
                    if ref != self.sequence(position):
                        continue
                except KeyError as exc:
                    print(exc, file=sys.stderr)

            # Trim bases that are unchanged between the ref and alt alleles
            new_ref, new_alt, start_adjust, end_adjust = collapse_seq_change(ref, alt)

            # Determine the type of variant
            variant_type = classify_seq_change(new_ref, new_alt)

            # Adjust the start position to the collapsed ref and alt. Example:
            # (start=1, start_offset=-3) + start_adjust=2 == (start=1, start_offset=-1)
            # (start=1, start_offset=-1) + start_adjust=2 == (start=2, start_offset=0)
            if position.start_offset:
                if position.start_offset < 0:
                    start_offset = min(position.start_offset + start_adjust, 0)
                    start = position.start + (start_adjust - (start_offset - position.start_offset))
                else:
                    start_offset = position.start_offset + start_adjust
                    start = position.start
            else:
                start_offset = position.start_offset
                start = position.start + start_adjust

            # Adjust the end position to the collapsed ref and alt. Example:
            # (end=3, end_offset=3) + end_adjust=2 == (end=3, end_offset=1)
            # (end=3, end_offset=1) + end_adjust=2 == (end=2, end_offset=0)
            if position.end_offset:
                if position.end_offset > 0:
                    end_offset = max(position.end_offset - end_adjust, 0)
                    end = position.end - (end_adjust + (end_offset - position.end_offset))
                else:
                    end_offset = position.end_offset - end_adjust
                    end = position.end
            else:
                end_offset = position.end_offset
                end = position.end - end_adjust

            # Special case: Insertions
            if variant_type == INSERTION:
                if len(ref) == 1:
                    # Adjust the position so it includes both bases flanking the insertion site
                    end = start + 1
                    position = position.copy_from(
                        position,
                        start=start,
                        start_offset=start_offset,
                        end=end,
                        end_offset=start_offset,
                    )
                    new_ref = self.sequence(position)
                    new_alt = new_alt + new_ref[-1]

            # Special case: Frameshifts
            if position.position_type == PROTEIN and is_frameshift:
                # NOTE: Only the first amino acid change is preserved.
                # See https://varnomen.hgvs.org/recommendations/protein/variant/frameshift/
                variant_class = ProteinFrameshift
                end = start
                new_ref = new_ref[0] if new_ref else new_ref
                new_alt = new_alt[0] if new_alt else new_alt
            else:
                variant_class = variant_class_map.get((position.position_type, variant_type))

            # Initialize a new variant object from the given position object
            if variant_class:
                variant = variant_class.copy_from(
                    position,
                    start=start,
                    start_offset=start_offset,
                    end=end,
                    end_offset=end_offset,
                    refseq=new_ref,
                    altseq=new_alt,
                )
                variant_list.append(variant)
            elif position.is_exon:
                # TODO: Is there a way to map a small variant to an exon?
                pass
            else:
                raise ValueError(
                    f"Unrecognized variant type for {position.position_type}/{variant_type} ({new_ref}/{new_alt})"
                )

        return variant_list

    # ---------------------------------------------------------------------------------------------
    # Functions for checking if positions/variants are equivalent
    # ---------------------------------------------------------------------------------------------
    def diff(self, query, reference) -> Dict[str, Tuple[List, List]]:
        """Return any positions that are shared between two positions

        Args:
            query (Position): Query position
            reference (Position): Reference position

        Returns:
            Dict[str, List]: Positions different between `query` and `reference`
        """
        return {
            CDNA: self.diff_cdna(query, reference),
            DNA: self.diff_dna(query, reference),
            EXON: self.diff_exon(query, reference),
            PROTEIN: self.diff_protein(query, reference),
            RNA: self.diff_rna(query, reference),
        }

    def diff_cdna(self, query, reference) -> Tuple[List, List]:
        """Return cDNA positions that are different between two positions

        Args:
            query (Position): Query position
            reference (Position): Reference position

        Returns:
            Tuple[List, List]: A list of cDNA positions unique to `query` and a list of cDNA
                positions unique to `reference`
        """
        return self._diff(query, reference, self.to_cdna)

    def diff_dna(self, query, reference) -> Tuple[List, List]:
        """Return DNA positions that are different between two positions

        Args:
            query (Position): Query position
            reference (Position): Reference position

        Returns:
            Tuple[List, List]: A list of DNA positions unique to `query` and a list of DNA positions
                unique to `reference`
        """
        return self._diff(query, reference, self.to_dna)

    def diff_exon(self, query, reference) -> Tuple[List, List]:
        """Return exon positions that are different between two positions

        Args:
            query (Position): Query position
            reference (Position): Reference position

        Returns:
            Tuple[List, List]: A list of exon positions unique to `query` and a list of exon positions
                unique to `reference`
        """
        return self._diff(query, reference, self.to_exon)

    def diff_protein(self, query, reference) -> Tuple[List, List]:
        """Return protein positions that are different between two positions

        Args:
            query (Position): Query position
            reference (Position): Reference position

        Returns:
            Tuple[List, List]: A list of protein positions unique to `query` and a list of protein
                positions unique to `reference`
        """
        return self._diff(query, reference, self.to_protein)

    def diff_rna(self, query, reference) -> Tuple[List, List]:
        """Return RNA positions that are different between two positions

        Args:
            query (Position): Query position
            reference (Position): Reference position

        Returns:
            Tuple[List, List]: A list of RNA positions unique to `query` and a list of RNA positions
                unique to `reference`
        """
        return self._diff(query, reference, self.to_rna)

    def _diff(self, query, reference, func: Callable) -> Tuple[List, List]:
        query_result = []
        reference_result = []

        query_pos = func(query)
        reference_pos = func(reference)
        for i in query_pos:
            if i not in reference_pos:
                query_result.append(i)

        for i in reference_pos:
            if i not in query_pos:
                reference_result.append(i)

        return query_result, reference_result

    def same(self, query, reference) -> Dict[str, List]:
        """Return any positions that are shared between two positions

        Args:
            query (Position): Query position
            reference (Position): Reference position

        Returns:
            Dict[str, List]: Positions shared between `query` and `reference`
        """
        return {
            CDNA: self.same_cdna(query, reference),
            DNA: self.same_dna(query, reference),
            EXON: self.same_exon(query, reference),
            PROTEIN: self.same_protein(query, reference),
            RNA: self.same_rna(query, reference),
        }

    def same_cdna(self, query, reference) -> List:
        """Return cDNA positions that are shared between two positions

        Args:
            query (Position): Query position
            reference (Position): Reference position

        Returns:
            List: cDNA positions shared between `query` and `reference`
        """
        return self._same(query, reference, self.to_cdna)

    def same_dna(self, query, reference) -> List:
        """Return DNA positions that are shared between two positions

        Args:
            query (Position): Query position
            reference (Position): Reference position

        Returns:
            List: DNA positions shared between `query` and `reference`
        """
        return self._same(query, reference, self.to_dna)

    def same_exon(self, query, reference) -> List:
        """Return exon positions that are shared between two positions

        Args:
            query (Position): Query position
            reference (Position): Reference position

        Returns:
            List: Exon positions shared between `query` and `reference`
        """
        return self._same(query, reference, self.to_exon)

    def same_protein(self, query, reference) -> List:
        """Return protein positions that are shared between two positions

        Args:
            query (Position): Query position
            reference (Position): Reference position

        Returns:
            List: Protein positions shared between `query` and `reference`
        """
        return self._same(query, reference, self.to_protein)

    def same_rna(self, query, reference) -> List:
        """Return RNA positions that are shared between two positions

        Args:
            query (Position): Query position
            reference (Position): Reference position

        Returns:
            List: RNA positions shared between `query` and `reference`
        """
        return self._same(query, reference, self.to_rna)

    def _same(self, query, reference, func: Callable) -> List:
        result = []

        query_pos = func(query)
        reference_pos = func(reference)
        for i in query_pos:
            if i in reference_pos:
                result.append(i)

        return result

    # ---------------------------------------------------------------------------------------------
    # Functions for getting feature ID/names
    # ---------------------------------------------------------------------------------------------
    def contig_ids(self, feature: str = "") -> List[str]:
        """Return the contig IDs that map to the given feature. If no feature is given, return
        all contig IDs.

        Examples:
            >>> ensembl100.contig_ids("BRCA2")
            ['13']

        Args:
            feature (str, optional): Feature ID or name

        Returns:
            List[str]: Contig IDs
        """
        return self._query_feature(CONTIG_ID, feature, alias=self.contig_alias)

    def exon_ids(self, feature: str = "") -> List[str]:
        """Return the exon IDs that map to the given feature. If no feature is given, return
        all exon IDs.

        Examples:
            >>> ensembl100.exon_ids("BRCA2")[:3]
            ['ENSE00000939167', 'ENSE00000939168', 'ENSE00000939169']

        Args:
            feature (str, optional): Feature ID or name

        Returns:
            List[str]: Exon IDs
        """
        return self._query_feature(EXON_ID, feature, alias=self.exon_alias)

    def gene_ids(self, feature: str = "") -> List[str]:
        """Return the gene IDs that map to the given feature. If no feature is given, return
        all gene IDs.

        Examples:
            >>> ensembl100.gene_ids("BRCA2")
            ['ENSG00000139618']

        Args:
            feature (str, optional): Feature ID or name

        Returns:
            List[str]: Gene IDs
        """
        return self._query_feature(GENE_ID, feature, alias=self.gene_alias)

    def gene_names(self, feature: str = "") -> List[str]:
        """Return the gene names that map to the given feature. If no feature is given, return
        all gene names.

        Examples:
            >>> ensembl100.gene_names("ENSG00000139618")
            ['BRCA2']

        Args:
            feature (str, optional): Feature ID or name

        Returns:
            List[str]: Gene names
        """
        return self._query_feature(GENE_NAME, feature, alias=self.gene_alias)

    def protein_ids(self, feature: str = "") -> List[str]:
        """Return the protein IDs that map to the given feature. If no feature is given, return
        all protein IDs.

        Examples:
            >>> ensembl100.protein_ids("BRCA2")[:3]
            ['ENSP00000369497', 'ENSP00000433168', 'ENSP00000434898']

        Args:
            feature (str, optional): Feature ID or name

        Returns:
            List[str]: Protein IDs
        """
        return self._query_feature(PROTEIN_ID, feature, alias=self.protein_alias)

    def transcript_ids(self, feature: str = "") -> List[str]:
        """Return the transcript IDs that map to the given feature. If no feature is given, return
        all transcript IDs.

        Examples:
            >>> ensembl100.transcript_ids("BRCA2")[:3]
            ['ENST00000380152', 'ENST00000470094', 'ENST00000528762']

        Args:
            feature (str, optional): Feature ID or name

        Returns:
            List[str]: Transcript IDs
        """
        return self._query_feature(TRANSCRIPT_ID, feature, alias=self.transcript_alias)

    def transcript_names(self, feature: str = "") -> List[str]:
        """Return the transcript names that map to the given feature. If no feature is given, return
        all transcript names.

        Examples:
            >>> ensembl100.transcript_names("BRCA2")[:3]
            ['BRCA2-201', 'BRCA2-202', 'BRCA2-203']

        Args:
            feature (str, optional): Feature ID or name

        Returns:
            List[str]: Transcript names
        """
        return self._query_feature(TRANSCRIPT_NAME, feature, alias=self.transcript_alias)

    @lru_cache
    def _query_feature(
        self, key: str, feature: str = "", alias: Optional[Callable] = None
    ) -> List[str]:
        if feature:
            parts = []

            for feature, feature_type in self.normalize_id(feature):
                if feature_type == CONTIG_ID:
                    func = self._query_contig_id
                elif feature_type == EXON_ID:
                    func = self._query_exon_id
                elif feature_type == GENE_ID:
                    func = self._query_gene_id
                elif feature_type == GENE_NAME:
                    func = self._query_gene_name
                elif feature_type == PROTEIN_ID:
                    func = self._query_protein_id
                elif feature_type == TRANSCRIPT_ID:
                    func = self._query_transcript_id
                elif feature_type == TRANSCRIPT_NAME:
                    func = self._query_transcript_name
                else:
                    raise ValueError(f"Unable to get {key} for {feature} ({feature_type})")

                # Try different aliases to see which have a match to the annotations
                feature_ = [feature]
                if alias:
                    feature_ += alias(feature)

                parts.append(func(feature_)[key])

            if parts:
                result = pd.concat(parts)
            else:
                result = pd.Series(dtype="object")
        else:
            result = self.df[key]

        return self._uniquify_series(result)

    def _query_contig_id(self, feature: Union[List[str], str]) -> pd.DataFrame:
        return self._query(feature, CONTIG_ID)

    def _query_exon_id(self, feature: Union[List[str], str]) -> pd.DataFrame:
        return self._query(feature, EXON_ID)

    def _query_gene_id(self, feature: Union[List[str], str]) -> pd.DataFrame:
        return self._query(feature, GENE_ID)

    def _query_gene_name(self, feature: Union[List[str], str]) -> pd.DataFrame:
        return self._query(feature, GENE_NAME)

    def _query_protein_id(self, feature: Union[List[str], str]) -> pd.DataFrame:
        return self._query(feature, PROTEIN_ID)

    def _query_transcript_id(self, feature: Union[List[str], str]) -> pd.DataFrame:
        return self._query(feature, TRANSCRIPT_ID)

    def _query_transcript_name(self, feature: Union[List[str], str]) -> pd.DataFrame:
        return self._query(feature, TRANSCRIPT_NAME)

    def _query(self, feature: Union[List[str], str], col: str) -> pd.DataFrame:
        feature = [feature] if isinstance(feature, str) else feature
        sudbf = self.df.loc[self.df[col].isin(feature)]

        return sudbf

    def _uniquify_series(self, series: pd.Series) -> List:
        return sorted(series.dropna().unique().tolist())

    # ---------------------------------------------------------------------------------------------
    # Functions for getting feature aliases
    # ---------------------------------------------------------------------------------------------
    @lru_cache
    def contig_alias(self, contig_id: str) -> List[str]:
        """List all aliases of the given contig ID.

        Args:
            contig_id (str): contig ID

        Returns:
            List[str]: All aliases of the given contig ID
        """
        alias = self._alias(contig_id, self._contig_alias)

        # TODO: Better way to handle chromosome naming?
        if contig_id.startswith("chr"):
            contig_id_alt = contig_id[3:]
            if contig_id_alt not in alias:
                alias.append(contig_id_alt)

        if not contig_id.startswith("chr"):
            contig_id_alt = "chr" + contig_id
            if contig_id_alt not in alias:
                alias.append(contig_id_alt)

        return alias

    @lru_cache
    def exon_alias(self, exon_id: str) -> List[str]:
        """List all aliases of the given exon ID.

        Args:
            exon_id (str): exon ID

        Returns:
            List[str]: All aliases of the given exon ID
        """
        return self._alias(exon_id, self._exon_alias)

    @lru_cache
    def gene_alias(self, gene_id: str) -> List[str]:
        """List all aliases of the given gene ID.

        Args:
            gene_id (str): gene ID

        Returns:
            List[str]: All aliases of the given gene ID
        """
        return self._alias(gene_id, self._gene_alias)

    @lru_cache
    def protein_alias(self, protein_id: str) -> List[str]:
        """List all aliases of the given protein ID.

        Args:
            protein_id (str): protein ID

        Returns:
            List[str]: All aliases of the given protein ID
        """
        return self._alias(protein_id, self._protein_alias)

    @lru_cache
    def transcript_alias(self, transcript_id: str) -> List[str]:
        """List all aliases of the given transcript ID.

        Args:
            transcript_id (str): transcript ID

        Returns:
            List[str]: All aliases of the given transcript ID
        """
        return self._alias(transcript_id, self._transcript_alias)

    def _alias(self, feature: str, alias_dict: Dict[str, List[str]]) -> List[str]:
        feature = str(feature)

        # Try different variations on the feature ID until one is found
        alias_list = [
            feature,
            strip_version(feature),
            feature.lower(),
            strip_version(feature).lower(),
            feature.upper(),
            strip_version(feature).upper(),
        ]
        for key in alias_list:
            if alias := alias_dict.get(key, []):
                # Coerce the alias to a list
                if isinstance(alias, str):
                    alias_list.append(alias)
                else:
                    alias_list.extend(alias)

        return sorted(set(alias_list))

    # ---------------------------------------------------------------------------------------------
    # Functions for normalizing feature ID/names
    # ---------------------------------------------------------------------------------------------
    def normalize_id(self, feature: str) -> List[Tuple[str, str]]:
        """Normalize an ID or name to the annotated equivalent(s).

        Examples:
            >>> ensembl100.normalize_id("BRCA2-201")
            [('BRCA2-201', 'transcript_name')]

        Args:
            feature (str): Feature ID or name

        Returns:
            List[Tuple[str, str]]: List of (normalized ID/name, normalized type (e.g. 'gene',
                'transcript', etc.))
        """
        normalized = []

        feature_type, result = self._normalize_id(feature)
        if feature_type:
            normalized = self._uniquify_series(result[feature_type])

        return [(i, feature_type) for i in normalized]

    @lru_cache
    def _normalize_id(self, feature: str) -> Tuple[str, pd.DataFrame]:
        feature_type = ""
        result = pd.DataFrame()

        for key, func in [
            (CONTIG_ID, self._normalize_contig_id),
            (EXON_ID, self._normalize_exon_id),
            (GENE_ID, self._normalize_gene_id),
            (GENE_NAME, self._normalize_gene_name),
            (PROTEIN_ID, self._normalize_protein_id),
            (TRANSCRIPT_ID, self._normalize_transcript_id),
            (TRANSCRIPT_NAME, self._normalize_transcript_name),
        ]:
            result = func(feature)
            if not result.empty:
                feature_type = key
                break

        return feature_type, result

    def _normalize_contig_id(self, feature: str) -> pd.DataFrame:
        featurel = [feature] + self.contig_alias(feature)

        return self._query_contig_id(featurel)

    def _normalize_exon_id(self, feature: str) -> pd.DataFrame:
        featurel = [feature] + self.exon_alias(feature)

        return self._query_exon_id(featurel)

    def _normalize_gene_id(self, feature: str) -> pd.DataFrame:
        featurel = [feature] + self.gene_alias(feature)

        return self._query_gene_id(featurel)

    def _normalize_gene_name(self, feature: str) -> pd.DataFrame:
        featurel = [feature] + self.gene_alias(feature)

        return self._query_gene_name(featurel)

    def _normalize_protein_id(self, feature: str) -> pd.DataFrame:
        featurel = [feature] + self.protein_alias(feature)

        return self._query_protein_id(featurel)

    def _normalize_transcript_id(self, feature: str) -> pd.DataFrame:
        featurel = [feature] + self.transcript_alias(feature)

        return self._query_transcript_id(featurel)

    def _normalize_transcript_name(self, feature: str) -> pd.DataFrame:
        featurel = [feature] + self.transcript_alias(feature)

        return self._query_transcript_name(featurel)

    # ---------------------------------------------------------------------------------------------
    # Functions for checking feature type
    # ---------------------------------------------------------------------------------------------
    def is_contig(self, feature: str) -> bool:
        """Check if the given ID or name is a contig.

        Args:
            feature (str): Feature ID or name

        Returns:
            bool: True if is a contig else False
        """
        return any((i[1] == CONTIG_ID for i in self.normalize_id(feature)))

    def is_exon(self, feature: str) -> bool:
        """Check if the given ID or name is an exon.

        Args:
            feature (str): Feature ID or name

        Returns:
            bool: True if is an exon else False
        """
        return any((i[1] == EXON_ID for i in self.normalize_id(feature)))

    def is_gene(self, feature: str) -> bool:
        """Check if the given ID or name is a gene.

        Args:
            feature (str): Feature ID or name

        Returns:
            bool: True if is an gene else False
        """
        return any((i[1] in (GENE_ID, GENE_NAME) for i in self.normalize_id(feature)))

    def is_protein(self, feature: str) -> bool:
        """Check if the given ID or name is a protein.

        Args:
            feature (str): Feature ID or name

        Returns:
            bool: True if is an protein else False
        """
        return any((i[1] == PROTEIN_ID for i in self.normalize_id(feature)))

    def is_transcript(self, feature: str) -> bool:
        """Check if the given ID or name is a transcript.

        Args:
            feature (str): Feature ID or name

        Returns:
            bool: True if is an transcript else False
        """
        return any((i[1] in (TRANSCRIPT_ID, TRANSCRIPT_NAME) for i in self.normalize_id(feature)))

    # ---------------------------------------------------------------------------------------------
    # Functions for checking if a transcript is a canonical transcript
    # ---------------------------------------------------------------------------------------------
    @lru_cache
    def is_canonical_transcript(self, transcript_id: str) -> bool:
        """Check if the given transcript ID is the canonical transcript for its gene.

        Args:
            transcript_id (str): transcript ID

        Returns:
            bool: True if the transcript is the canonical transcript else False
        """
        return transcript_id in self._canonical_transcript

    # ---------------------------------------------------------------------------------------------
    # <feature>
    # ---------------------------------------------------------------------------------------------
    def cdna(self, feature: str, canonical: bool = False) -> List[CdnaPosition]:
        """Return the cDNA position(s) matching the given feature ID or name.

        Args:
            feature (str): Feature ID or name
            canonical (bool, optional): Only consider the canonical transcript when mapping. Defaults to False.

        Returns:
            List[CdnaPosition]: One or more cDNA positions.
        """
        result = []

        transcript_ids = self.transcript_ids(feature)
        mask = (self.df[TRANSCRIPT_ID].isin(transcript_ids)) & (self.df["feature"] == CDNA)
        for _, cdna in self.df[mask].iterrows():
            if canonical and not self.is_canonical_transcript(cdna.transcript_id):
                continue

            result.append(
                CdnaPosition(
                    contig_id=cdna.contig_id,
                    start=cdna.cdna_start,
                    start_offset=0,
                    end=cdna.cdna_end,
                    end_offset=0,
                    strand=cdna.strand,
                    gene_id=cdna.gene_id,
                    gene_name=cdna.gene_name,
                    transcript_id=cdna.transcript_id,
                    transcript_name=cdna.transcript_name,
                    protein_id=cdna.protein_id,
                )
            )

        return sorted(set(result))

    def dna(self, feature: str) -> List[DnaPosition]:
        """Return the DNA position(s) matching the given feature ID or name.

        Args:
            feature (str): Feature ID or name
            canonical (bool, optional): Only consider the canonical transcript when mapping. Defaults to False.

        Returns:
            List[DnaPosition]: One or more DNA positions.
        """
        result = []

        # get the strand of the original feature
        _, df = self._normalize_id(feature)
        strand_list = self._uniquify_series(df["strand"])

        for contig_id in self.contig_ids(feature):
            for fasta in self.dna_fasta:
                try:
                    contig_seq = fasta[contig_id]
                    break
                except KeyError:
                    continue
            else:
                raise KeyError(f"Sequence '{contig_id}' not found")

            start = 1
            end = len(contig_seq)
            for strand in strand_list:
                result.append(
                    DnaPosition(
                        contig_id=contig_id,
                        start=start,
                        start_offset=0,
                        end=end,
                        end_offset=0,
                        strand=strand,
                    )
                )

        return sorted(set(result))

    def exon(self, feature: str, canonical: bool = False) -> List[ExonPosition]:
        """Return the exon position(s) matching the given feature ID or name.

        Args:
            feature (str): Feature ID or name
            canonical (bool, optional): Only consider the canonical transcript when mapping. Defaults to False.

        Returns:
            List[ExonPosition]: One or more exon positions.
        """
        result = []

        exon_ids = self.exon_ids(feature)
        mask = (self.df[EXON_ID].isin(exon_ids)) & (self.df["feature"] == EXON)
        for _, exon in self.df[mask].iterrows():
            if canonical and not self.is_canonical_transcript(exon.transcript_id):
                continue

            result.append(
                ExonPosition(
                    contig_id=exon.contig_id,
                    start=int(exon.exon_number),
                    start_offset=0,
                    end=int(exon.exon_number),
                    end_offset=0,
                    strand=exon.strand,
                    gene_id=exon.gene_id,
                    gene_name=exon.gene_name,
                    transcript_id=exon.transcript_id,
                    transcript_name=exon.transcript_name,
                    exon_id=exon.exon_id,
                )
            )

        return sorted(set(result))

    def gene(self, feature: str) -> List[DnaPosition]:
        """Return the gene position(s) matching the given feature ID or name.

        Args:
            feature (str): Feature ID or name
            canonical (bool, optional): Only consider the canonical transcript when mapping. Defaults to False.

        Returns:
            List[DnaPosition]: One or more DNA positions.
        """
        result = []

        gene_ids = self.gene_ids(feature)
        mask = (self.df[GENE_ID].isin(gene_ids)) & (self.df["feature"] == "gene")
        for _, gene in self.df[mask].iterrows():
            result.append(
                DnaPosition(
                    contig_id=gene.contig_id,
                    start=gene.start,
                    start_offset=0,
                    end=gene.end,
                    end_offset=0,
                    strand=gene.strand,
                )
            )

        return sorted(set(result))

    def protein(self, feature: str, canonical: bool = False) -> List[ProteinPosition]:
        """Return the protein position(s) matching the given feature ID or name.

        Args:
            feature (str): Feature ID or name
            canonical (bool, optional): Only consider the canonical transcript when mapping. Defaults to False.

        Returns:
            List[ProteinPosition]: One or more protein positions.
        """
        result = []
        for cdna in self.cdna(feature, canonical=canonical):
            # Convert the cDNA position to a protein position
            protein_start = calc_cdna_to_protein(cdna.start)
            protein_end = calc_cdna_to_protein(cdna.end)
            result.append(
                ProteinPosition.copy_from(
                    cdna, start=protein_start, start_offset=0, end=protein_end, end_offset=0
                )
            )

        return sorted(set(result))

    def rna(self, feature: str, canonical: bool = False) -> List[RnaPosition]:
        """Return the RNA position(s) matching the given feature ID or name.

        Args:
            feature (str): Feature ID or name
            canonical (bool, optional): Only consider the canonical transcript when mapping. Defaults to False.

        Returns:
            List[RnaPosition]: One or more RNA positions.
        """
        result = []

        transcript_ids = self.transcript_ids(feature)
        mask = (self.df[TRANSCRIPT_ID].isin(transcript_ids)) & (self.df["feature"] == "transcript")
        for _, transcript in self.df[mask].iterrows():
            if canonical and not self.is_canonical_transcript(transcript.transcript_id):
                continue

            result.append(
                RnaPosition(
                    contig_id=transcript.contig_id,
                    start=transcript.transcript_start,
                    start_offset=0,
                    end=transcript.transcript_end,
                    end_offset=0,
                    strand=transcript.strand,
                    gene_id=transcript.gene_id,
                    gene_name=transcript.gene_name,
                    transcript_id=transcript.transcript_id,
                    transcript_name=transcript.transcript_name,
                )
            )

        return sorted(set(result))

    # ---------------------------------------------------------------------------------------------
    # Utility functions
    # ---------------------------------------------------------------------------------------------
    def translate_cdna_variant(
        self, cdna: CdnaPosition, cdna_altseq: str
    ) -> List[Tuple[str, bool]]:
        """Return the mutated protein sequence, given a cDNA position and alt allele.

        Args:
            cdna (CdnaPosition): cDNA position object
            cdna_altseq (str): cDNA alternate allele

        Returns:
            List[str]: protein alternate allele(s)
        """
        pep_altseq_set = set()

        # Get the codon sequence
        codon_start_offset = (cdna.start - 1) % 3
        codon_start = cdna.start - codon_start_offset
        codon_end_offset = 2 - ((cdna.end - 1) % 3)
        codon_end = cdna.end + codon_end_offset
        # Create a new CdnaPosition encompassing the entire codon(s)
        codon = CdnaPosition.copy_from(cdna, start=codon_start, end=codon_end)
        codon_refseq = self.sequence(codon)
        # Assert that the codon sequence is divisible by 3
        assert len(codon_refseq) % 3 == 0

        # Mutate the codon sequence
        codon_refseq_left = codon_refseq[:codon_start_offset]
        codon_refseq_right = codon_refseq[-codon_end_offset:] if codon_end_offset else ""
        for i in expand_nt(cdna_altseq):
            codon_altseq = codon_refseq_left + i + codon_refseq_right
            # A frameshift results when the length of the alternate sequence is not divisible by 3
            remainder = len(codon_altseq) % 3
            if remainder != 0:
                # TODO: A way to preserve information about the downstream nucleotide change?
                codon_altseq = codon_altseq[:-remainder]
                is_frameshift = True
            else:
                is_frameshift = False

            pep_altseq = "".join(AMINO_ACID_TABLE[codon] for codon in split_by_codon(codon_altseq))
            pep_altseq_set.add((pep_altseq, is_frameshift))

        return sorted(pep_altseq_set)


def join_positions(start: List, end: List, merge_on: str) -> List:
    """Return the combination of two list of position or variant objects - one of start positions
    and one of end positions - into one list by the given key (e.g. 'transcript_id').

    All positions must be of the same class.

    Args:
        start (List[position or small variant]): Start positions
        end (List[position or small variant]): End positions
        merge_on (str): Attribute to merge on (e.g. 'transcript_id')

    Returns:
        List[position or small variant]: New position or variant objects
    """
    result = set()

    for start_pos, end_pos in product(start, end):
        # Make sure that the positions are sorted by position
        if start_pos.start > end_pos.start:
            start_pos, end_pos = end_pos, start_pos
        # Make a new position from the start of the 1st position and end of the 2nd
        start_key = getattr(start_pos, merge_on)
        end_key = getattr(end_pos, merge_on)
        if start_key == end_key:
            assert start_pos.__class__ == end_pos.__class__
            new = start_pos.copy_from(start_pos, end=end_pos.end, end_offset=end_pos.end_offset)
            result.add(new)

    return sorted(result)  # type: ignore
