"""Class definitions for position/variant objects."""
from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any, Dict, Type

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
from .utils import format_hgvs_position


@dataclass(eq=True, frozen=True)
class _Base:
    """Base class for all position and variant classes."""

    @classmethod
    def copy_from(cls, obj: _Base, **kwargs):
        """Initialize a new `_Base`-derived object by copying values from another `_Base`-derived object.

        Args:
            obj (_Base): Position object to copy attributes from
            **kwargs: Arguments with keys that match the attribute names of this `_Base`-derived class will override attributes from `obj`

        Returns:
            a new object of the same class as the class that calls this method
        """
        return cls(
            **{
                **{k: v for k, v in obj.asdict().items() if k in [i.name for i in fields(cls)]},
                **kwargs,
            }
        )  # type: ignore

    def __getitem__(self, item: Any) -> Any:
        return getattr(self, item)

    def __lt__(self, other: _Base) -> bool:
        return str(self) < str(other)

    def __str__(self) -> str:
        raise NotImplementedError()  # Defined by inheriting class

    @property
    def is_cdna(self) -> bool:
        """Check if this fusion is between cDNA.

        Returns:
            bool: True if the fusion is between cDNA else False
        """
        return False

    @property
    def is_deletion(self) -> bool:
        """Check if this variant is a deletion.

        Returns:
            bool: True if the position is a deletion else False
        """
        return self.variant_type == DELETION

    @property
    def is_delins(self) -> bool:
        """Check if this variant is a delins (indel).

        Returns:
            bool: True if the position is a delins else False
        """
        return self.variant_type == DELINS

    @property
    def is_dna(self) -> bool:
        """Check if this position is on DNA.

        Returns:
            bool: True if the position is on DNA else False
        """
        return False

    @property
    def is_duplication(self) -> bool:
        """Check if this variant is a duplication.

        Returns:
            bool: True if the position is a duplication else False
        """
        return self.variant_type == DUPLICATION

    @property
    def is_exon(self) -> bool:
        """Check if this fusion is between exon.

        Returns:
            bool: True if the fusion is between exon else False
        """
        return False

    @property
    def is_frameshift(self) -> bool:
        """Check if this variant is a frameshift.

        Returns:
            bool: True if the position is a frameshift else False
        """
        return self.variant_type == FRAMESHIFT

    @property
    def is_fusion(self) -> bool:
        """Check if this variant is a fusion.

        Returns:
            bool: True if the position is a fusion else False
        """
        return self.variant_type == FUSION

    @property
    def is_insertion(self) -> bool:
        """Check if this variant is an insertion.

        Returns:
            bool: True if the position is an insertion else False
        """
        return self.variant_type == INSERTION

    @property
    def is_protein(self) -> bool:
        """Check if this fusion is between protein.

        Returns:
            bool: True if the fusion is between protein else False
        """
        return False

    @property
    def is_rna(self) -> bool:
        """Check if this fusion is between RNA.

        Returns:
            bool: True if the fusion is between RNA else False
        """
        return False

    @property
    def is_small_variant(self) -> bool:
        """Check if this a small variant.

        Returns:
            bool: True if the position is a small variant else False
        """
        return False

    @property
    def is_substitution(self) -> bool:
        """Check if this variant is a substitution.

        Returns:
            bool: True if the position is a substitution else False
        """
        return self.variant_type == SUBSTITUTION

    @property
    def is_variant(self) -> bool:
        """Check if this a variant.

        Returns:
            bool: True if the position is a variant else False
        """
        return False

    @property
    def on_negative_strand(self) -> bool:
        """Check if this position originates from the negative strand of the genome.

        Returns:
            bool: True if the position originates from the negative strand of the genome else False
        """
        raise NotImplementedError()  # Defined by inheriting class

    @property
    def on_positive_strand(self) -> bool:
        """Check if this position originates from the positive strand of the genome.

        Returns:
            bool: True if the position originates from the positive strand of the genome else False
        """
        raise NotImplementedError()  # Defined by inheriting class

    @property
    def position_type(self) -> str:
        """Get the position type.

        Returns:
            str: Type of position (e.g, 'cdna')
        """
        raise NotImplementedError()  # Defined by inheriting class

    @property
    def variant_type(self) -> str:
        """Get the variant type.

        Returns:
            str: Type of variant (e.g, 'substitution')
        """
        raise NotImplementedError()  # Defined by inheriting class

    def asdict(self) -> Dict[str, Any]:
        """Convert this position's attributes to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary of attribute names and corresponding values
        """
        return {f.name: self[f.name] for f in fields(self)}


@dataclass(eq=True, frozen=True)
class _Position(_Base):
    """Base class for positions."""

    contig_id: str
    start: int
    start_offset: int
    end: int
    end_offset: int
    strand: str

    @property
    def on_negative_strand(self) -> bool:
        """Check if this position originates from the negative strand of the genome.

        Returns:
            bool: True if the position originates from the negative strand of the genome else False
        """
        return self.strand == "-"

    @property
    def on_positive_strand(self) -> bool:
        """Check if this position originates from the positive strand of the genome.

        Returns:
            bool: True if the position originates from the positive strand of the genome else False
        """
        return self.strand == "+"

    @property
    def position_type(self) -> str:
        """Get the position type.

        Returns:
            str: Type of position (e.g, 'cdna')
        """
        return ""

    @property
    def variant_type(self) -> str:
        """Get the variant type.

        Returns:
            str: Type of variant (e.g, 'substitution')
        """
        return ""


@dataclass(eq=True, frozen=True)
class CdnaPosition(_Position):
    """Base class for cDNA positions."""

    gene_id: str
    gene_name: str
    transcript_id: str
    transcript_name: str
    protein_id: str

    def __str__(self) -> str:
        start = format_hgvs_position(self.start, self.start_offset)
        end = format_hgvs_position(self.end, self.end_offset)
        if start == end:
            return f"{self.transcript_id}:c.{start}"
        else:
            return f"{self.transcript_id}:c.{start}_{end}"

    @property
    def is_cdna(self) -> bool:
        """Check if this position is on a cDNA.

        Returns:
            bool: True if the position is on a cDNA else False
        """
        return True

    @property
    def position_type(self) -> str:
        """Get the position type.

        Returns:
            str: Type of position (e.g, 'cdna')
        """
        return CDNA


@dataclass(eq=True, frozen=True)
class DnaPosition(_Position):
    """Base class for DNA positions."""

    def __str__(self) -> str:
        start = format_hgvs_position(self.start, self.start_offset)
        end = format_hgvs_position(self.end, self.end_offset)
        if start == end:
            return f"{self.contig_id}:g.{start}"
        else:
            return f"{self.contig_id}:g.{start}_{end}"

    @property
    def is_dna(self) -> bool:
        """Check if this position is on DNA.

        Returns:
            bool: True if the position is on DNA else False
        """
        return True

    @property
    def position_type(self) -> str:
        """Get the position type.

        Returns:
            str: Type of position (e.g, 'cdna')
        """
        return DNA


@dataclass(eq=True, frozen=True)
class ExonPosition(_Position):
    """Base class for exon positions."""

    gene_id: str
    gene_name: str
    transcript_id: str
    transcript_name: str
    # NOTE: If the start and end are different, the exon ID of the start is listed as the `exon_id`
    exon_id: str

    def __str__(self) -> str:
        start = format_hgvs_position(self.start, self.start_offset)
        end = format_hgvs_position(self.end, self.end_offset)
        if start == end:
            return f"{self.transcript_id}:e.{start}"
        else:
            return f"{self.transcript_id}:e.{start}_{end}"

    @property
    def is_exon(self) -> bool:
        """Check if this position is on an exon.

        Returns:
            bool: True if the position is on an exon else False
        """
        return True

    @property
    def position_type(self) -> str:
        """Get the position type.

        Returns:
            str: Type of position (e.g, 'cdna')
        """
        return EXON


@dataclass(eq=True, frozen=True)
class ProteinPosition(_Position):
    """Base class for protein positions."""

    gene_id: str
    gene_name: str
    transcript_id: str
    transcript_name: str
    protein_id: str

    def __str__(self) -> str:
        start = format_hgvs_position(self.start, self.start_offset)
        end = format_hgvs_position(self.end, self.end_offset)
        if start == end:
            return f"{self.protein_id}:p.{start}"
        else:
            return f"{self.protein_id}:p.{start}_{end}"

    @property
    def is_protein(self) -> bool:
        """Check if this position is on a protein.

        Returns:
            bool: True if the position is on a protein else False
        """
        return True

    @property
    def position_type(self) -> str:
        """Get the position type.

        Returns:
            str: Type of position (e.g, 'cdna')
        """
        return PROTEIN


@dataclass(eq=True, frozen=True)
class RnaPosition(_Position):
    """Base class for RNA positions."""

    gene_id: str
    gene_name: str
    transcript_id: str
    transcript_name: str

    def __str__(self) -> str:
        start = format_hgvs_position(self.start, self.start_offset)
        end = format_hgvs_position(self.end, self.end_offset)
        if start == end:
            return f"{self.transcript_id}:r.{start}"
        else:
            return f"{self.transcript_id}:r.{start}_{end}"

    @property
    def is_rna(self) -> bool:
        """Check if this position is on an RNA.

        Returns:
            bool: True if the position is on an RNA else False
        """
        return True

    @property
    def position_type(self) -> str:
        """Get the position type.

        Returns:
            str: Type of position (e.g, 'cdna')
        """
        return RNA


# -------------------------------------------------------------------------------------------------
# Variant classes
# -------------------------------------------------------------------------------------------------
@dataclass(eq=True, frozen=True)
class _Variant(_Base):
    """Base class for variants."""

    @property
    def is_variant(self) -> bool:
        """Check if this a variant.

        Returns:
            bool: True if the position is a variant else False
        """
        return True


# -------------------------------------------------------------------------------------------------
# SmallVariant classes
# -------------------------------------------------------------------------------------------------
@dataclass(eq=True, frozen=True)
class _SmallVariant(_Variant):
    """Base class for small variants."""

    refseq: str
    altseq: str

    @property
    def is_small_variant(self) -> bool:
        """Check if this a small variant.

        Returns:
            bool: True if the position is a small variant else False
        """
        return True


@dataclass(eq=True, frozen=True)
class _CdnaSmallVariant(CdnaPosition, _SmallVariant):
    """Base class for cDNA small variants."""


@dataclass(eq=True, frozen=True)
class _DnaSmallVariant(DnaPosition, _SmallVariant):
    """Base class for DNA small variants."""


@dataclass(eq=True, frozen=True)
class _ExonSmallVariant(ExonPosition, _SmallVariant):
    """Base class for exon small variants."""


@dataclass(eq=True, frozen=True)
class _ProteinSmallVariant(ProteinPosition, _SmallVariant):
    """Base class for protein small variants."""


@dataclass(eq=True, frozen=True)
class _RnaSmallVariant(RnaPosition, _SmallVariant):
    """Base class for RNA small variants."""


# -------------------------------------------------------------------------------------------------
# Deletion classes
# -------------------------------------------------------------------------------------------------
@dataclass(eq=True, frozen=True)
class _Deletion(_SmallVariant):
    """Base class for deletion variants."""

    @property
    def variant_type(self) -> str:
        """Get the variant type.

        Returns:
            str: Type of variant
        """
        return DELETION


@dataclass(eq=True, frozen=True)
class CdnaDeletion(_Deletion, _CdnaSmallVariant):
    """Stores information on a cDNA deletion variant and maps to other position types."""

    def __str__(self) -> str:
        start = format_hgvs_position(self.start, self.start_offset)
        end = format_hgvs_position(self.end, self.end_offset)
        if start == end:
            return f"{self.transcript_id}:c.{start}del"
        else:
            return f"{self.transcript_id}:c.{start}_{end}del"


@dataclass(eq=True, frozen=True)
class DnaDeletion(_Deletion, _DnaSmallVariant):
    """Stores information on a DNA deletion variant and maps to other position types."""

    def __str__(self) -> str:
        start = format_hgvs_position(self.start, self.start_offset)
        end = format_hgvs_position(self.end, self.end_offset)
        if start == end:
            return f"{self.contig_id}:g.{start}del"
        else:
            return f"{self.contig_id}:g.{start}_{end}del"


@dataclass(eq=True, frozen=True)
class ProteinDeletion(_Deletion, _ProteinSmallVariant):
    """Stores information on a protein deletion variant and maps to other position types."""

    def __str__(self) -> str:
        start = format_hgvs_position(self.start, self.start_offset)
        end = format_hgvs_position(self.end, self.end_offset)
        start_seq = self.refseq[0]
        end_seq = self.refseq[-1]
        if start == end:
            return f"{self.protein_id}:p.{start_seq}{start}del"
        else:
            return f"{self.protein_id}:p.{start_seq}{start}_{end_seq}{end}del"


@dataclass(eq=True, frozen=True)
class RnaDeletion(_Deletion, _RnaSmallVariant):
    """Stores information on an RNA deletion variant and maps to other position types."""

    def __str__(self) -> str:
        start = format_hgvs_position(self.start, self.start_offset)
        end = format_hgvs_position(self.end, self.end_offset)
        if start == end:
            return f"{self.transcript_id}:r.{start}del"
        else:
            return f"{self.transcript_id}:r.{start}_{end}del"


# -------------------------------------------------------------------------------------------------
# Delins classes
# -------------------------------------------------------------------------------------------------
@dataclass(eq=True, frozen=True)
class _Delins(_SmallVariant):
    """Base class for delins variants."""

    @property
    def variant_type(self) -> str:
        """Get the variant type.

        Returns:
            str: Type of variant
        """
        return DELINS


@dataclass(eq=True, frozen=True)
class CdnaDelins(_Delins, _CdnaSmallVariant):
    """Stores information on a cDNA delins variant and maps to other position types."""

    def __str__(self) -> str:
        start = format_hgvs_position(self.start, self.start_offset)
        end = format_hgvs_position(self.end, self.end_offset)
        if start == end:
            return f"{self.transcript_id}:c.{start}delins{self.altseq}"
        else:
            return f"{self.transcript_id}:c.{start}_{end}delins{self.altseq}"


@dataclass(eq=True, frozen=True)
class DnaDelins(_Delins, _DnaSmallVariant):
    """Stores information on a DNA delins variant and maps to other position types."""

    def __str__(self) -> str:
        start = format_hgvs_position(self.start, self.start_offset)
        end = format_hgvs_position(self.end, self.end_offset)
        if start == end:
            return f"{self.contig_id}:g.{start}delins{self.altseq}"
        else:
            return f"{self.contig_id}:g.{start}_{end}delins{self.altseq}"


@dataclass(eq=True, frozen=True)
class ProteinDelins(_Delins, _ProteinSmallVariant):
    """Stores information on a protein delins variant and maps to other position types."""

    def __str__(self) -> str:
        start = format_hgvs_position(self.start, self.start_offset)
        end = format_hgvs_position(self.end, self.end_offset)
        start_seq = self.refseq[0]
        end_seq = self.refseq[-1]
        if start == end:
            return f"{self.protein_id}:p.{start_seq}{start}delins{self.altseq}"
        else:
            return f"{self.protein_id}:p.{start_seq}{start}_{end_seq}{end}delins{self.altseq}"


@dataclass(eq=True, frozen=True)
class RnaDelins(_Delins, _RnaSmallVariant):
    """Stores information on an RNA delins variant and maps to other position types."""

    def __str__(self) -> str:
        start = format_hgvs_position(self.start, self.start_offset)
        end = format_hgvs_position(self.end, self.end_offset)
        if start == end:
            return f"{self.transcript_id}:r.{start}delins{self.altseq}"
        else:
            return f"{self.transcript_id}:r.{start}_{end}delins{self.altseq}"


# -------------------------------------------------------------------------------------------------
# Duplication classes
# -------------------------------------------------------------------------------------------------
@dataclass(eq=True, frozen=True)
class _Duplication(_SmallVariant):
    """Base class for duplication variants."""

    @property
    def variant_type(self) -> str:
        """Get the variant type.

        Returns:
            str: Type of variant
        """
        return DUPLICATION


@dataclass(eq=True, frozen=True)
class CdnaDuplication(_Duplication, _CdnaSmallVariant):
    """Stores information on a cDNA duplication variant and maps to other position types."""

    def __str__(self) -> str:
        start = format_hgvs_position(self.start, self.start_offset)
        end = format_hgvs_position(self.end, self.end_offset)
        if start == end:
            return f"{self.transcript_id}:c.{start}dup"
        else:
            return f"{self.transcript_id}:c.{start}_{end}dup"


@dataclass(eq=True, frozen=True)
class DnaDuplication(_Duplication, _DnaSmallVariant):
    """Stores information on a DNA duplication variant and maps to other position types."""

    def __str__(self) -> str:
        start = format_hgvs_position(self.start, self.start_offset)
        end = format_hgvs_position(self.end, self.end_offset)
        if start == end:
            return f"{self.contig_id}:g.{start}dup"
        else:
            return f"{self.contig_id}:g.{start}_{end}dup"


@dataclass(eq=True, frozen=True)
class ProteinDuplication(_Duplication, _ProteinSmallVariant):
    """Stores information on a protein duplication variant and maps to other position types."""

    def __str__(self) -> str:
        start = format_hgvs_position(self.start, self.start_offset)
        end = format_hgvs_position(self.end, self.end_offset)
        start_seq = self.refseq[0]
        end_seq = self.refseq[-1]
        if start == end:
            return f"{self.protein_id}:p.{start_seq}{start}dup"
        else:
            return f"{self.protein_id}:p.{start_seq}{start}_{end_seq}{end}dup"


@dataclass(eq=True, frozen=True)
class RnaDuplication(_Duplication, _RnaSmallVariant):
    """Stores information on an RNA duplication variant and maps to other position types."""

    def __str__(self) -> str:
        start = format_hgvs_position(self.start, self.start_offset)
        end = format_hgvs_position(self.end, self.end_offset)
        if start == end:
            return f"{self.transcript_id}:r.{start}dup"
        else:
            return f"{self.transcript_id}:r.{start}_{end}dup"


# -------------------------------------------------------------------------------------------------
# Frameshift classes
# -------------------------------------------------------------------------------------------------
@dataclass(eq=True, frozen=True)
class _Frameshift(_SmallVariant):
    """Base class for insertion variants."""

    @property
    def variant_type(self) -> str:
        """Get the variant type.

        Returns:
            str: Type of variant
        """
        return FRAMESHIFT


@dataclass(eq=True, frozen=True)
class ProteinFrameshift(_Frameshift, _ProteinSmallVariant):
    """Stores information on a protein frameshift variant and maps to other position types."""

    def __str__(self) -> str:
        start = format_hgvs_position(self.start, self.start_offset)
        start_seq = self.refseq[0]
        return f"{self.protein_id}:p.{start_seq}{start}fs"


# -------------------------------------------------------------------------------------------------
# Insertion classes
# -------------------------------------------------------------------------------------------------
@dataclass(eq=True, frozen=True)
class _Insertion(_SmallVariant):
    """Base class for insertion variants."""

    @property
    def variant_type(self) -> str:
        """Get the variant type.

        Returns:
            str: Type of variant
        """
        return INSERTION


@dataclass(eq=True, frozen=True)
class CdnaInsertion(_Insertion, _CdnaSmallVariant):
    """Stores information on a cDNA insertion variant and maps to other position types."""

    def __str__(self) -> str:
        start = format_hgvs_position(self.start, self.start_offset)
        end = format_hgvs_position(self.end, self.end_offset)
        altseq = self.altseq[1:-1]
        return f"{self.transcript_id}:c.{start}_{end}ins{altseq}"


@dataclass(eq=True, frozen=True)
class DnaInsertion(_Insertion, _DnaSmallVariant):
    """Stores information on a DNA insertion variant and maps to other position types."""

    def __str__(self) -> str:
        start = format_hgvs_position(self.start, self.start_offset)
        end = format_hgvs_position(self.end, self.end_offset)
        altseq = self.altseq[1:-1]
        return f"{self.contig_id}:g.{start}_{end}ins{altseq}"


@dataclass(eq=True, frozen=True)
class ProteinInsertion(_Insertion, _ProteinSmallVariant):
    """Stores information on a protein insertion variant and maps to other position types."""

    def __str__(self) -> str:
        start = format_hgvs_position(self.start, self.start_offset)
        end = format_hgvs_position(self.end, self.end_offset)
        start_seq = self.refseq[0]
        end_seq = self.refseq[-1]
        altseq = self.altseq[1:-1]
        return f"{self.protein_id}:p.{start_seq}{start}_{end_seq}{end}ins{altseq}"


@dataclass(eq=True, frozen=True)
class RnaInsertion(_Insertion, _RnaSmallVariant):
    """Stores information on an RNA insertion variant and maps to other position types."""

    def __str__(self) -> str:
        start = format_hgvs_position(self.start, self.start_offset)
        end = format_hgvs_position(self.end, self.end_offset)
        altseq = self.altseq[1:-1]
        return f"{self.transcript_id}:r.{start}_{end}ins{altseq}"


# -------------------------------------------------------------------------------------------------
# Substitution classes
# -------------------------------------------------------------------------------------------------
@dataclass(eq=True, frozen=True)
class _Substitution(_SmallVariant):
    """Base class for substitution variants."""

    @property
    def variant_type(self) -> str:
        """Get the variant type.

        Returns:
            str: Type of variant
        """
        return SUBSTITUTION


@dataclass(eq=True, frozen=True)
class CdnaSubstitution(_Substitution, _CdnaSmallVariant):
    """Stores information on a cDNA substitution variant and maps to other position types."""

    def __str__(self) -> str:
        start = format_hgvs_position(self.start, self.start_offset)
        return f"{self.transcript_id}:c.{start}{self.refseq}>{self.altseq}"


@dataclass(eq=True, frozen=True)
class DnaSubstitution(_Substitution, _DnaSmallVariant):
    """Stores information on a DNA substitution variant and maps to other position types."""

    def __str__(self) -> str:
        start = format_hgvs_position(self.start, self.start_offset)
        return f"{self.contig_id}:g.{start}{self.refseq}>{self.altseq}"


@dataclass(eq=True, frozen=True)
class ProteinSubstitution(_Substitution, _ProteinSmallVariant):
    """Stores information on a protein substitution variant and maps to other position types."""

    def __str__(self) -> str:
        start = format_hgvs_position(self.start, self.start_offset)
        return f"{self.protein_id}:p.{self.refseq}{start}{self.altseq}"


@dataclass(eq=True, frozen=True)
class RnaSubstitution(_Substitution, _RnaSmallVariant):
    """Stores information on an RNA substitution variant and maps to other position types."""

    def __str__(self) -> str:
        start = format_hgvs_position(self.start, self.start_offset)
        return f"{self.transcript_id}:r.{start}{self.refseq}>{self.altseq}"


# -------------------------------------------------------------------------------------------------
# Fusion classes
# -------------------------------------------------------------------------------------------------
@dataclass(eq=True, frozen=True)
class _Fusion(_Variant):
    """Base class for fusion variants."""

    breakpoint1: Type[_Position]
    breakpoint2: Type[_Position]

    def __str__(self) -> str:
        return f"{self.breakpoint1}::{self.breakpoint2}"

    @property
    def on_negative_strand(self) -> bool:
        """Check if one or both breakpoints originate from the negative strand of the genome.

        Returns:
            bool: True if if one or both breakpoints are on the negative strand else False
        """
        return "-" in (self.breakpoint1.strand, self.breakpoint2.strand)

    @property
    def on_positive_strand(self) -> bool:
        """Check if one or both breakpoints originate from the positive strand of the genome.

        Returns:
            bool: True if if one or both breakpoints are on the positive strand else False
        """
        return "+" in (self.breakpoint1.strand, self.breakpoint2.strand)

    @property
    def variant_type(self) -> str:
        """Get the variant type.

        Returns:
            str: Type of variant
        """
        return FUSION


@dataclass(eq=True, frozen=True)
class CdnaFusion(_Fusion):
    """Stores information on a cDNA fusion variant and maps to other position types."""

    @property
    def is_cdna(self) -> bool:
        """Check if this fusion is between cDNA.

        Returns:
            bool: True if the fusion is between cDNA else False
        """
        return True


@dataclass(eq=True, frozen=True)
class DnaFusion(_Fusion):
    """Stores information on a DNA fusion variant and maps to other position types."""

    @property
    def is_dna(self) -> bool:
        """Check if this position is on DNA.

        Returns:
            bool: True if the position is on DNA else False
        """
        return True


@dataclass(eq=True, frozen=True)
class ExonFusion(_Fusion):
    """Stores information on an exon fusion variant and maps to other position types."""

    @property
    def is_exon(self) -> bool:
        """Check if this fusion is between exon.

        Returns:
            bool: True if the fusion is between exon else False
        """
        return True


@dataclass(eq=True, frozen=True)
class ProteinFusion(_Fusion):
    """Stores information on a protein fusion variant and maps to other position types."""

    @property
    def is_protein(self) -> bool:
        """Check if this fusion is between protein.

        Returns:
            bool: True if the fusion is between protein else False
        """
        return True


@dataclass(eq=True, frozen=True)
class RnaFusion(_Fusion):
    """Stores information on a RNA fusion variant and maps to other position types."""

    @property
    def is_rna(self) -> bool:
        """Check if this fusion is between RNA.

        Returns:
            bool: True if the fusion is between RNA else False
        """
        return True
