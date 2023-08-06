"""Definitions for the `EnsemblRelease` class."""
from __future__ import annotations

from typing import Dict, List, Optional, Union, cast

from .core import Core
from .ensembl_cache import EnsemblCache
from .files import tsv_to_dict, txt_to_list
from .positions import CdnaPosition
from .sequence import PyfaidxFasta
from .utils import reverse_complement


class EnsemblRelease(Core):
    """Handles converting between position types and retrieving information on biological features
    based on an Ensembl release.
    """

    def __init__(
        self,
        species: str,
        release: int,
        cache_dir: str = "",
        canonical_transcript: Union[List[str], str] = [],
        contig_alias: Union[str, Dict] = {},
        exon_alias: Union[str, Dict] = {},
        gene_alias: Union[str, Dict] = {},
        protein_alias: Union[str, Dict] = {},
        transcript_alias: Union[str, Dict] = {},
    ):
        """
        Args:
            species (str): Species name
            release (int): Ensembl release number
            canonical_transcript (Union[List[str], str], optional): List of canonical transcript IDs, or the path to a text file
            contig_alias (Union[str, Dict], optional): Dictionary mapping contig aliases to their normalized ID, or a path to a text file
            exon_alias (Union[str, Dict], optional): Dictionary mapping exon aliases to their normalized ID, or a path to a text file
            gene_alias (Union[str, Dict], optional): Dictionary mapping gene aliases to their normalized ID, or a path to a text file
            protein_alias (Union[str, Dict], optional): Dictionary mapping protein aliases to their normalized ID, or a path to a text file
            transcript_alias (Union[str, Dict], optional): Dictionary mapping transcript aliases to their normalized ID, or a path to a text file
        """
        self.ensembl_cache = EnsemblCache(species, release, cache_dir=cache_dir)
        self.cache_dir = self.ensembl_cache.release_cache_dir
        self.reference = self.ensembl_cache.reference
        self.release = self.ensembl_cache.release
        self.species = self.ensembl_cache.species
        self.df = self.ensembl_cache.load_df()

        self.cds_fasta: List[PyfaidxFasta] = []
        self.dna_fasta: List[PyfaidxFasta] = []
        self.protein_fasta: List[PyfaidxFasta] = []
        self.rna_fasta: List[PyfaidxFasta] = []
        self.cds_fasta = []
        self.dna_fasta = [PyfaidxFasta.load(self.ensembl_cache.local_dna_fasta_filepath)]
        self.protein_fasta = [PyfaidxFasta.load(self.ensembl_cache.local_pep_fasta_filepath)]
        self.rna_fasta = [
            PyfaidxFasta.load(self.ensembl_cache.local_cdna_fasta_filepath),
            PyfaidxFasta.load(self.ensembl_cache.local_ncrna_fasta_filepath),
        ]

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

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(species={self.species}, release={self.release})"

    def install(
        self,
        clean: bool = True,
        recache: bool = False,
        redownload: bool = False,
        restrict_genes: List[str] = [],
    ):
        """Download missing data, process, and cache.

        Args:
            clean (bool, optional): Delete temporary files. Defaults to True.
            recache (bool, optional): Overwrite any existing cache. Defaults to False.
            redownload (bool, optional): Redownload files from Ensembl. Defaults to False.
            restrict_genes (List[str], optional): Restrict cache to the specified genes. Defaults to [].
        """
        self.ensembl_cache.install(
            clean=clean, recache=recache, redownload=redownload, restrict_genes=restrict_genes
        )

    def _sequence(
        self,
        position,
        mutate: bool,
        strand: Optional[str],
        window: Optional[int],
        floor: Optional[int],
        ceiling: Optional[int],
    ) -> str:
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

        # Ensembl does not provide a CDS FASTA so we need to get the sequence from the RNA FASTA
        if position.is_cdna and not self.cds_fasta:
            position = cast(CdnaPosition, position)
            if rna := self.to_rna(position):
                position = rna[0]

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
