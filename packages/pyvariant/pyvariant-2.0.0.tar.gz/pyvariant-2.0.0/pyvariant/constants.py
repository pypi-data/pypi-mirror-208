"""Collection of constants used throughout the package."""
import os.path

# Default Ensembl species and release
DEFAULT_SPECIES = "homo_sapiens"
DEFAULT_ENSEMBL_RELEASE = 100

# Environmental variable used to set the cache directory
CACHE_DIR_ENV = "VARIANT_MAP_CACHE"
CACHE_DIR_NAME = "pyvariant"

# Attribute name literals
CONTIG_ID = "contig_id"
EXON_ID = "exon_id"
GENE_ID = "gene_id"
GENE_NAME = "gene_name"
PROTEIN_ID = "protein_id"
TRANSCRIPT_ID = "transcript_id"
TRANSCRIPT_NAME = "transcript_name"

# Position type literals
CDNA = "cdna"
CDS = "CDS"
DNA = "dna"
EXON = "exon"
PROTEIN = "protein"
RNA = "rna"
STOP_CODON = "stop_codon"

# Variant type literals
DELETION = "deletion"
DELINS = "delins"
DUPLICATION = "duplication"
FRAMESHIFT = "frameshift"
FUSION = "fusion"
INSERTION = "insertion"
SUBSTITUTION = "substitution"

# Fallback FASTA file used if none are provided
EMPTY_FASTA = os.path.join(os.path.dirname(__file__), "data", "empty.fa")
