"""Definitions for the `EnsemblCache` class."""
import os.path
import sys
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
from gtfparse import read_gtf
from pyfaidx import Fasta

from .constants import CONTIG_ID
from .files import bgzip, ftp_download, get_cache_dir, is_bgzipped
from .utils import normalize_release, normalize_species, reference_by_release, strip_version

# Ensembl FTP URL
ENSEMBL_FTP_SERVER = "ftp.ensembl.org"

# FASTA directory example: pub/release-100/fasta/homo_sapiens
FASTA_SUBDIR_TEMPLATE = "pub/release-{release}/fasta/{species}/{type}"

# FASTA file name example: Homo_sapiens.GRCh38.100.dna.toplevel.fa.gz
# NOTE: The file name format changed after Ensembl release 75
FASTA_FILENAME_TEMPLATE_OLD = {
    "cdna": "{species}.{reference}.{release}.{type}.all.fa.gz",
    "dna": "{species}.{reference}.{release}.{type}.toplevel.fa.gz",
    "ncrna": "{species}.{reference}.{release}.{type}.fa.gz",
    "pep": "{species}.{reference}.{release}.{type}.all.fa.gz",
}
FASTA_FILENAME_TEMPLATE_NEW = {
    "cdna": "{species}.{reference}.{type}.all.fa.gz",
    "dna": "{species}.{reference}.{type}.toplevel.fa.gz",
    "ncrna": "{species}.{reference}.{type}.fa.gz",
    "pep": "{species}.{reference}.{type}.all.fa.gz",
}

# GTF annotation directory example: pub/release-100/gtf/homo_sapiens
GTF_SUBDIR_TEMPLATE = "pub/release-{release}/gtf/{species}"

# GTF annotation file example: Homo_sapiens.GRCh38.100.gtf.gz
GTF_FILENAME_TEMPLATE = "{species}.{reference}.{release}.gtf.gz"

# GTF column names and features
GTF_COLUMN_RENAME = {"seqname": CONTIG_ID}
GTF_KEEP_FEATURES = ["CDS", "exon", "gene", "stop_codon", "transcript"]
GTF_KEEP_COLUMNS = [
    "contig_id",
    "feature",
    "start",
    "end",
    "strand",
    "gene_id",
    "gene_name",
    "transcript_id",
    "transcript_name",
    "exon_id",
    "exon_number",
    "protein_id",
]
GTF_ADD_COLUMNS = ["transcript_start", "transcript_end", "cdna_start", "cdna_end"]


class EnsemblCache:
    """Class for managing Ensembl files."""

    def __init__(self, species: str, release: int, cache_dir: str = ""):
        self.species = normalize_species(species)
        self.release = normalize_release(release)
        self.reference = reference_by_release(self.release)

        if cache_dir:
            self.cache_dir = os.path.abspath(cache_dir)
        else:
            self.cache_dir = get_cache_dir()

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
        # Create the cache directory structure
        self.make_release_cache_dir()

        # Download each FASTA file
        for fasta, index, downloadf in [
            (
                self.local_cdna_fasta_filepath,
                self.local_cdna_index_filepath,
                self.download_cdna_fasta,
            ),
            (self.local_dna_fasta_filepath, self.local_dna_index_filepath, self.download_dna_fasta),
            (self.local_pep_fasta_filepath, self.local_pep_index_filepath, self.download_pep_fasta),
            (
                self.local_ncrna_fasta_filepath,
                self.local_ncrna_index_filepath,
                self.download_ncrna_fasta,
            ),
        ]:
            if not os.path.exists(fasta) or redownload:
                downloadf()

        # Re-compress (if required) and index each FASTA file
        for fasta, index, indexf in [
            (self.local_cdna_fasta_filepath, self.local_cdna_index_filepath, self.index_cdna_fasta),
            (self.local_dna_fasta_filepath, self.local_dna_index_filepath, self.index_dna_fasta),
            (self.local_pep_fasta_filepath, self.local_pep_index_filepath, self.index_pep_fasta),
            (
                self.local_ncrna_fasta_filepath,
                self.local_ncrna_index_filepath,
                self.index_ncrna_fasta,
            ),
        ]:
            # NOTE: pyfaidx only supports compressed FASTA in BGZF format. Ensembl FASTA comes in
            # GZ format, so we need to compress the data with bgzip.
            if not is_bgzipped(fasta):
                bgzip(fasta)
            if not os.path.exists(index) or redownload:
                indexf()

        # Download the GTF file
        gtf_missing = not os.path.exists(self.local_gtf_filepath)
        cache_missing = not os.path.exists(self.local_gtf_cache_filepath)
        if (gtf_missing and cache_missing) or (gtf_missing and recache) or redownload:
            self.download_gtf()

        # Process and cache the GTF file
        if cache_missing or recache:
            # TODO: switch to 'polars'?
            df = read_gtf(self.local_gtf_filepath, result_type="pandas")

            restrict_genes = ["ARF5"]  # DEBUG

            if restrict_genes:
                df = df[df["gene_name"].isin(restrict_genes)]

            df = normalize_df(df)
            self.cache_df(df)
            if clean:
                self.delete_gtf()

    # ---------------------------------------------------------------------------------------------
    # Release cache directory
    # ---------------------------------------------------------------------------------------------
    @property
    def release_cache_dir(self) -> str:
        """Local path to the directory containing the release data files."""
        return os.path.join(self.cache_dir, self.species, self.reference, str(self.release))

    def make_release_cache_dir(self):
        """Create the release cache directory, if it doesn't already exist."""
        Path(self.release_cache_dir).mkdir(exist_ok=True, parents=True)

    # ---------------------------------------------------------------------------------------------
    # Remote FASTA file paths
    # ---------------------------------------------------------------------------------------------
    @property
    def remote_cdna_fasta_subdir(self) -> str:
        """Path to the directory on the FTP server that contains the cDNA FASTA file."""
        return self._remote_fasta_subdir("cdna")

    @property
    def remote_dna_fasta_subdir(self) -> str:
        """Path to the directory on the FTP server that contains the DNA FASTA file."""
        return self._remote_fasta_subdir("dna")

    @property
    def remote_ncrna_fasta_subdir(self) -> str:
        """Path to the directory on the FTP server that contains the ncRNA FASTA file."""
        return self._remote_fasta_subdir("ncrna")

    @property
    def remote_pep_fasta_subdir(self) -> str:
        """Path to the directory on the FTP server that contains the peptide FASTA file."""
        return self._remote_fasta_subdir("pep")

    def _remote_fasta_subdir(self, fasta_type: str) -> str:
        return FASTA_SUBDIR_TEMPLATE.format(
            release=self.release, species=self.species, type=fasta_type
        )

    @property
    def remote_cdna_fasta_filename(self) -> str:
        """Name of the cDNA FASTA file on the FTP server."""
        return self._remote_fasta_filename("cdna")

    @property
    def remote_dna_fasta_filename(self) -> str:
        """Name of the DNA FASTA file on the FTP server."""
        return self._remote_fasta_filename("dna")

    @property
    def remote_ncrna_fasta_filename(self) -> str:
        """Name of the ncRNA FASTA file on the FTP server."""
        return self._remote_fasta_filename("ncrna")

    @property
    def remote_pep_fasta_filename(self) -> str:
        """Name of the peptide FASTA file on the FTP server."""
        return self._remote_fasta_filename("pep")

    def _remote_fasta_filename(self, fasta_type: str) -> str:
        if self.release <= 75:
            template = FASTA_FILENAME_TEMPLATE_OLD[fasta_type]
            return template.format(
                species=self.species.capitalize(),
                reference=self.reference,
                release=self.release,
                type=fasta_type,
            )
        else:
            template = FASTA_FILENAME_TEMPLATE_NEW[fasta_type]
            return template.format(
                species=self.species.capitalize(), reference=self.reference, type=fasta_type
            )

    # ---------------------------------------------------------------------------------------------
    # Local FASTA file paths
    # ---------------------------------------------------------------------------------------------
    @property
    def local_cdna_fasta_filepath(self) -> str:
        """Local name of the cDNA FASTA file."""
        return self._local_fasta_filepath(self.remote_cdna_fasta_filename)

    @property
    def local_dna_fasta_filepath(self) -> str:
        """Local name of the DNA FASTA file."""
        return self._local_fasta_filepath(self.remote_dna_fasta_filename)

    @property
    def local_ncrna_fasta_filepath(self) -> str:
        """Local name of the ncRNA FASTA file."""
        return self._local_fasta_filepath(self.remote_ncrna_fasta_filename)

    @property
    def local_pep_fasta_filepath(self) -> str:
        """Local name of the peptide FASTA file."""
        return self._local_fasta_filepath(self.remote_pep_fasta_filename)

    def _local_fasta_filepath(self, remote_fasta_filename: str) -> str:
        return os.path.join(self.release_cache_dir, remote_fasta_filename)

    # ---------------------------------------------------------------------------------------------
    # Download FASTA files
    # ---------------------------------------------------------------------------------------------
    def download_cdna_fasta(self):
        """Download the cDNA FASTA file from the FTP server."""
        ftp_download(
            ENSEMBL_FTP_SERVER,
            self.remote_cdna_fasta_subdir,
            self.remote_cdna_fasta_filename,
            self.local_cdna_fasta_filepath,
        )

    def download_dna_fasta(self):
        """Download the DNA FASTA file from the FTP server."""
        ftp_download(
            ENSEMBL_FTP_SERVER,
            self.remote_dna_fasta_subdir,
            self.remote_dna_fasta_filename,
            self.local_dna_fasta_filepath,
        )

    def download_ncrna_fasta(self):
        """Download the ncRNA FASTA file from the FTP server."""
        ftp_download(
            ENSEMBL_FTP_SERVER,
            self.remote_ncrna_fasta_subdir,
            self.remote_ncrna_fasta_filename,
            self.local_ncrna_fasta_filepath,
        )

    def download_pep_fasta(self):
        """Download the peptide FASTA file from the FTP server."""
        ftp_download(
            ENSEMBL_FTP_SERVER,
            self.remote_pep_fasta_subdir,
            self.remote_pep_fasta_filename,
            self.local_pep_fasta_filepath,
        )

    # ---------------------------------------------------------------------------------------------
    # Local FASTA index paths
    # ---------------------------------------------------------------------------------------------
    @property
    def local_cdna_index_filepath(self) -> str:
        """Local name of the cDNA FASTA file."""
        return self._fasta_index_path(self.local_cdna_fasta_filepath)

    @property
    def local_dna_index_filepath(self) -> str:
        """Local name of the DNA FASTA file."""
        return self._fasta_index_path(self.local_dna_fasta_filepath)

    @property
    def local_ncrna_index_filepath(self) -> str:
        """Local name of the ncRNA FASTA file."""
        return self._fasta_index_path(self.local_ncrna_fasta_filepath)

    @property
    def local_pep_index_filepath(self) -> str:
        """Local name of the peptide FASTA file."""
        return self._fasta_index_path(self.local_pep_fasta_filepath)

    def _fasta_index_path(self, local_fasta_filename: str) -> str:
        """Return the path to the FASTA index file."""
        return local_fasta_filename + ".fai"

    # ---------------------------------------------------------------------------------------------
    # Index FASTA files
    # ---------------------------------------------------------------------------------------------
    def index_cdna_fasta(self):
        """(Re)build the index file for the cDNA Fasta."""
        return self._index_fasta(self.local_cdna_fasta_filepath)

    def index_dna_fasta(self):
        """(Re)build the index file for the DNA Fasta."""
        return self._index_fasta(self.local_dna_fasta_filepath)

    def index_ncrna_fasta(self):
        """(Re)build the index file for the cDNA Fasta."""
        return self._index_fasta(self.local_ncrna_fasta_filepath)

    def index_pep_fasta(self):
        """(Re)build the index file for the peptide Fasta."""
        return self._index_fasta(self.local_pep_fasta_filepath)

    def _index_fasta(self, local_fasta_filename: str):
        print(f"Indexing {local_fasta_filename}...", file=sys.stderr)
        _ = Fasta(
            local_fasta_filename,
            key_function=strip_version,
            as_raw=True,
            sequence_always_upper=True,
            build_index=True,
            rebuild=True,
        )

    # ---------------------------------------------------------------------------------------------
    # GTF files
    # ---------------------------------------------------------------------------------------------
    @property
    def remote_gtf_subdir(self) -> str:
        """Path to the directory on the FTP server that contains the GTF file."""
        return GTF_SUBDIR_TEMPLATE.format(release=self.release, species=self.species)

    @property
    def remote_gtf_filename(self) -> str:
        """Name of the GTF file on the FTP server."""
        return GTF_FILENAME_TEMPLATE.format(
            species=self.species.capitalize(), reference=self.reference, release=self.release
        )

    @property
    def local_gtf_filepath(self) -> str:
        """Local name of the GTF file."""
        return os.path.join(self.release_cache_dir, self.remote_gtf_filename)

    @property
    def local_gtf_cache_filepath(self) -> str:
        """Local name of the cache file."""
        return os.path.join(
            self.release_cache_dir, self.remote_gtf_filename.replace(".gtf.gz", ".pickle")
        )

    def download_gtf(self):
        """Download the GTF file from the FTP server."""
        ftp_download(
            ENSEMBL_FTP_SERVER,
            self.remote_gtf_subdir,
            self.remote_gtf_filename,
            self.local_gtf_filepath,
        )

    def delete_gtf(self):
        """Delete the GTF file from the local filesystem."""
        print(f"Removing {self.local_gtf_filepath}", file=sys.stderr)
        os.remove(self.local_gtf_filepath)

    # ---------------------------------------------------------------------------------------------
    # Database cache
    # ---------------------------------------------------------------------------------------------
    def cache_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert the Ensembl GTF to a pandas DataFrame and cache it."""
        print(
            f"Converting {self.local_gtf_filepath} to {self.local_gtf_cache_filepath}",
            file=sys.stderr,
        )
        df.to_pickle(self.local_gtf_cache_filepath)

    def load_df(self) -> pd.DataFrame:
        """Return the cached Ensembl GTF data."""
        return pd.read_pickle(self.local_gtf_cache_filepath)


def normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize a pandas DataFrame and infer missing data."""
    df = df.replace("", np.nan)
    df = normlize_columns(df)
    df = df.sort_values(["start", "end"])
    df = infer_transcripts(df)
    df = infer_cdna(df)
    df = infer_missing_genes(df)
    df = exon_offset_transcript(df)
    df = cds_offset_transcript(df)
    df = cds_offset_cdna(df)
    df = set_protein_id(df)
    df = df.replace("", np.nan)

    return df


def normlize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename columns, drop unused data, and set data types for each column."""
    # Rename column(s)
    df = df.rename(columns=GTF_COLUMN_RENAME)
    # Drop unused columns
    df = df.drop(df.columns.difference(GTF_KEEP_COLUMNS), axis=1)
    # Drop unused feature types
    df = df[df.feature.isin(GTF_KEEP_FEATURES)]
    # Add additional columns
    df = df.reindex(columns=GTF_KEEP_COLUMNS + GTF_ADD_COLUMNS)
    # Assert that all the expected columns exist
    missing = [i for i in GTF_KEEP_COLUMNS + GTF_ADD_COLUMNS if i not in df.columns]
    assert not missing, f"Found columns {list(df.columns)}, missing {missing}"
    # Coerce the non-null values in the 'exon_number' to float
    df["exon_number"] = df["exon_number"].astype(float, errors="raise")

    return df


def infer_transcripts(df: pd.DataFrame) -> pd.DataFrame:
    """Infer transcripts position(s) from other features, if not already defined."""
    transcript_rows = []

    print("Inferring transcripts...", file=sys.stderr)
    for transcript_id, group in df.groupby("transcript_id"):
        if group[group.feature == "transcript"].empty:
            first = group.iloc[0]
            last = group.iloc[-1]
            new_row = {
                "contig_id": first.contig_id,
                "feature": "transcript",
                "start": first.start,
                "end": last.end,
                "strand": first.strand,
                "gene_id": first.gene_id,
                "gene_name": first.gene_name,
                "transcript_id": transcript_id,
                "transcript_name": first.transcript_name,
            }
            transcript_rows.append(new_row)
            print(f"Inferred transcript {new_row}", file=sys.stderr)

    new_transcript_df = pd.DataFrame(transcript_rows)
    df = pd.concat([df, new_transcript_df], ignore_index=True)
    df = df.sort_values(["start", "end"])

    return df


def infer_cdna(df: pd.DataFrame) -> pd.DataFrame:
    """Infer cDNA position(s) from other features, if not already defined."""
    cdna_rows = []

    print("Inferring cDNA...", file=sys.stderr)
    for transcript_id, group in df.groupby("transcript_id"):
        if group[group.feature == "cdna"].empty:
            cds_df = group[group.feature == "cds"]
            if not cds_df.empty:
                first = cds_df.iloc[0]
                last = cds_df.iloc[-1]
                new_row = {
                    "contig_id": first.contig_id,
                    "feature": "cdna",
                    "start": first.start,
                    "end": last.end,
                    "strand": first.strand,
                    "gene_id": first.gene_id,
                    "gene_name": first.gene_name,
                    "transcript_id": transcript_id,
                    "transcript_name": first.transcript_name,
                }
                cdna_rows.append(new_row)
                print(f"Inferred cDNA {new_row}", file=sys.stderr)

    new_cdna_df = pd.DataFrame(cdna_rows)
    df = pd.concat([df, new_cdna_df], ignore_index=True)
    df = df.sort_values(["start", "end"])

    return df


def infer_missing_genes(df: pd.DataFrame) -> pd.DataFrame:
    """Infer gene position(s) from other features, if not already defined."""
    gene_rows = []

    print("Inferring missing genes...", file=sys.stderr)
    for _, group in df.groupby("gene_id"):
        if group[group.feature == "gene"].empty:
            first = group.iloc[0]
            last = group.iloc[-1]
            new_row = {
                "contig_id": first.contig_id,
                "feature": "gene",
                "start": first.start,
                "end": last.end,
                "strand": first.strand,
                "gene_id": first.gene_id,
                "gene_name": first.gene_name,
            }
            gene_rows.append(new_row)
            print(f"Inferred gene {new_row}", file=sys.stderr)

    new_gene_df = pd.DataFrame(gene_rows)
    df = pd.concat([df, new_gene_df], ignore_index=True)
    df = df.sort_values(["start", "end"])

    return df


def exon_offset_transcript(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate the position of each exon, relative to the start of the transcript."""
    print("Inferring exon offsets from transcripts...", file=sys.stderr)
    for _, group in df.groupby("transcript_id"):
        transcript_df = group[group.feature == "transcript"]
        if transcript_df.empty:
            continue

        offset = 0
        transcript_index = transcript_df.index[0]
        transcript = transcript_df.iloc[0]
        ascending = transcript.strand == "+"
        exon_df = group[group.feature == "exon"]
        if exon_df.empty:
            continue

        for exon in exon_df.sort_values(["start", "end"], ascending=ascending).itertuples():
            # if this is the first exon/CDS/etc start the offset relative to the RNA
            if offset == 0:
                if ascending:
                    offset = exon.start - transcript.start
                else:
                    offset = transcript.end - exon.end

            length = exon.end - exon.start + 1
            transcript_start = offset + 1
            transcript_end = length + offset
            offset += length

            # add the new offsets to the exon
            df.at[exon.Index, "transcript_start"] = transcript_start
            df.at[exon.Index, "transcript_end"] = transcript_end

        # add the new offsets to the transcript
        df.at[transcript_index, "transcript_start"] = 1
        df.at[transcript_index, "transcript_end"] = offset

    # convert the offset values to integers
    df["transcript_start"] = df["transcript_start"].astype("Int64")
    df["transcript_end"] = df["transcript_end"].astype("Int64")

    return df


def cds_offset_transcript(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate the position of each CDS, relative to the start of the transcript."""
    print("Inferring CDS offsets from transcripts...", file=sys.stderr)
    for _, group in df.groupby("transcript_id"):
        cds_df = group[group.feature.isin(["cds", "stop_codon"])]
        if cds_df.empty:
            continue

        ascending = cds_df.iloc[0].strand == "+"
        for cds in cds_df.sort_values(["start", "end"], ascending=ascending).itertuples():
            exon_mask = (
                (group.start <= cds.start) & (group.end >= cds.end) & (group.feature == "exon")
            )
            exon_df = group[exon_mask]
            if exon_df.empty:
                continue

            exon = exon_df.iloc[0]
            if ascending:
                offset = cds.start - exon.start + exon.transcript_start
            else:
                offset = exon.end - cds.end + exon.transcript_start

            length = cds.end - cds.start
            transcript_start = offset
            transcript_end = length + offset
            offset += length

            # add the new offsets and exon ID to the CDS
            df.at[cds.Index, "exon_id"] = exon.exon_id
            df.at[cds.Index, "transcript_start"] = transcript_start
            df.at[cds.Index, "transcript_end"] = transcript_end

    # convert the offset values to integers
    df["transcript_start"] = df["transcript_start"].astype("Int64")
    df["transcript_end"] = df["transcript_end"].astype("Int64")

    return df


def cds_offset_cdna(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate the position of each CDS, relative to the start of the cDNA."""
    print("Inferring CDS offsets from cDNA...", file=sys.stderr)
    for _, group in df.groupby("transcript_id"):
        cdna_df = group[group.feature == "cdna"]
        if cdna_df.empty:
            continue

        cdna_index = cdna_df.index[0]
        cdna = cdna_df.iloc[0]
        ascending = cdna.strand == "+"

        cds_df = group[group.feature.isin(["cds", "stop_codon"])]
        if cds_df.empty:
            continue

        offset = 0
        cds_df = cds_df.sort_values(["start", "end"], ascending=ascending)
        for cds in cds_df.itertuples():
            # if this is the first exon/CDS/etc start the offset relative to the RNA
            if offset == 0:
                if ascending:
                    offset = cds.start - cdna.start
                else:
                    offset = cdna.end - cds.end

            length = cds.end - cds.start + 1
            start_offset = offset + 1
            end_offset = length + offset
            offset += length

            # add the new offsets to the CDS
            df.at[cds.Index, "cdna_start"] = start_offset
            df.at[cds.Index, "cdna_end"] = end_offset

        # add the new offsets to the cDNA
        df.at[cdna_index, "cdna_start"] = 1
        df.at[cdna_index, "cdna_end"] = offset

    # convert the offset values to integers
    df["cdna_start"] = df["cdna_start"].astype("Int64")
    df["cdna_end"] = df["cdna_end"].astype("Int64")

    return df


def set_protein_id(df: pd.DataFrame) -> pd.DataFrame:
    """Add the protein ID as info for each cDNA and stop codon, if not already defined."""
    print("Inferring protein IDs...", file=sys.stderr)
    for _, group in df.groupby("transcript_id"):
        # Get the first non-NA protein ID matching the transcript ID
        # A protein coding transcript should only have 1 matching protein ID
        if pidx := group["protein_id"].first_valid_index():
            protein_id = group["protein_id"].loc[pidx]
        else:
            continue

        subdf = group[group.feature.isin(["cdna", "stop_codon"])]
        for index, _ in subdf.iterrows():
            if pd.isna(df.loc[index, "protein_id"]):
                print(f"Adding protein ID '{protein_id}' to row {index}", file=sys.stderr)
                df.loc[index, "protein_id"] = protein_id

    return df
