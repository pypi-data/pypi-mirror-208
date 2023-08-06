import pandas as pd
import pytest
from constants import (
    CANONICAL_TRANSCRIPT,
    CONTIG_ALIAS,
    EXON_ALIAS,
    GENE_ALIAS,
    PROTEIN_ALIAS,
    TEST_ENS100_CDNA_FASTA,
    TEST_ENS100_DNA_FASTA,
    TEST_ENS100_GTF,
    TEST_ENS100_NCRNA_FASTA,
    TEST_ENS100_PEP_FASTA,
    TRANSCRIPT_ALIAS,
)

from pyvariant.constants import (
    CONTIG_ID,
    EXON_ID,
    GENE_ID,
    GENE_NAME,
    PROTEIN_ID,
    TRANSCRIPT_ID,
    TRANSCRIPT_NAME,
)
from pyvariant.core import Core
from pyvariant.positions import (
    CdnaDeletion,
    CdnaDelins,
    CdnaDuplication,
    CdnaPosition,
    CdnaSubstitution,
    DnaDelins,
    DnaInsertion,
    DnaPosition,
    DnaSubstitution,
    ExonFusion,
    ExonPosition,
    ProteinFrameshift,
    ProteinPosition,
    ProteinSubstitution,
    RnaDelins,
    RnaPosition,
    RnaSubstitution,
)
from pyvariant.sequence import PyfaidxFasta


# -------------------------------------------------------------------------------------------------
# init
# -------------------------------------------------------------------------------------------------
def test_init():
    obj = Core(
        gtf=TEST_ENS100_GTF,
        cds=[TEST_ENS100_CDNA_FASTA],
        dna=[TEST_ENS100_DNA_FASTA],
        peptide=[TEST_ENS100_PEP_FASTA],
        rna=[TEST_ENS100_NCRNA_FASTA],
        canonical_transcript=CANONICAL_TRANSCRIPT,
        contig_alias=CONTIG_ALIAS,
        exon_alias=EXON_ALIAS,
        gene_alias=GENE_ALIAS,
        protein_alias=PROTEIN_ALIAS,
        transcript_alias=TRANSCRIPT_ALIAS,
    )
    assert isinstance(obj.df, pd.DataFrame)
    assert isinstance(obj.cds_fasta, list)
    assert isinstance(obj.cds_fasta[0], PyfaidxFasta)
    assert isinstance(obj.dna_fasta, list)
    assert isinstance(obj.dna_fasta[0], PyfaidxFasta)
    assert isinstance(obj.protein_fasta, list)
    assert isinstance(obj.protein_fasta[0], PyfaidxFasta)
    assert isinstance(obj.rna_fasta, list)
    assert isinstance(obj.rna_fasta[0], PyfaidxFasta)
    assert isinstance(obj._canonical_transcript, list)
    assert isinstance(obj._contig_alias, dict)
    assert isinstance(obj._exon_alias, dict)
    assert isinstance(obj._gene_alias, dict)
    assert isinstance(obj._protein_alias, dict)
    assert isinstance(obj._transcript_alias, dict)


# -------------------------------------------------------------------------------------------------
# to_cdna
# -------------------------------------------------------------------------------------------------
def test_to_cdna_canonical(ensembl100):
    assert ensembl100.to_cdna("7:g.127589084", canonical=False) == [
        CdnaPosition(
            contig_id="7",
            start=69,
            start_offset=0,
            end=69,
            end_offset=0,
            strand="+",
            gene_id="ENSG00000004059",
            gene_name="ARF5",
            transcript_id="ENST00000000233",
            transcript_name="ARF5-201",
            protein_id="ENSP00000000233",
        ),
        CdnaPosition(
            contig_id="7",
            start=69,
            start_offset=0,
            end=69,
            end_offset=0,
            strand="+",
            gene_id="ENSG00000004059",
            gene_name="ARF5",
            transcript_id="ENST00000415666",
            transcript_name="ARF5-202",
            protein_id="ENSP00000412701",
        ),
    ]
    assert ensembl100.to_cdna("7:g.127589084", canonical=True) == [
        CdnaPosition(
            contig_id="7",
            start=69,
            start_offset=0,
            end=69,
            end_offset=0,
            strand="+",
            gene_id="ENSG00000004059",
            gene_name="ARF5",
            transcript_id="ENST00000000233",
            transcript_name="ARF5-201",
            protein_id="ENSP00000000233",
        )
    ]


# -------------------------------------------------------------------------------------------------
# to_protein
# -------------------------------------------------------------------------------------------------
def test_to_protein_from_dna(ensembl100):
    assert ensembl100.to_protein("17:g.7674252G>A") == [
        ProteinSubstitution(
            refseq="M",
            altseq="I",
            contig_id="17",
            start=237,
            start_offset=0,
            end=237,
            end_offset=0,
            strand="-",
            gene_id="ENSG00000141510",
            gene_name="TP53",
            transcript_id="ENST00000269305",
            transcript_name="TP53-201",
            protein_id="ENSP00000269305",
        ),
        ProteinSubstitution(
            refseq="M",
            altseq="I",
            contig_id="17",
            start=237,
            start_offset=0,
            end=237,
            end_offset=0,
            strand="-",
            gene_id="ENSG00000141510",
            gene_name="TP53",
            transcript_id="ENST00000359597",
            transcript_name="TP53-202",
            protein_id="ENSP00000352610",
        ),
        ProteinSubstitution(
            refseq="M",
            altseq="I",
            contig_id="17",
            start=237,
            start_offset=0,
            end=237,
            end_offset=0,
            strand="-",
            gene_id="ENSG00000141510",
            gene_name="TP53",
            transcript_id="ENST00000420246",
            transcript_name="TP53-204",
            protein_id="ENSP00000391127",
        ),
        ProteinSubstitution(
            refseq="M",
            altseq="I",
            contig_id="17",
            start=237,
            start_offset=0,
            end=237,
            end_offset=0,
            strand="-",
            gene_id="ENSG00000141510",
            gene_name="TP53",
            transcript_id="ENST00000445888",
            transcript_name="TP53-205",
            protein_id="ENSP00000391478",
        ),
        ProteinSubstitution(
            refseq="M",
            altseq="I",
            contig_id="17",
            start=237,
            start_offset=0,
            end=237,
            end_offset=0,
            strand="-",
            gene_id="ENSG00000141510",
            gene_name="TP53",
            transcript_id="ENST00000455263",
            transcript_name="TP53-206",
            protein_id="ENSP00000398846",
        ),
        ProteinSubstitution(
            refseq="M",
            altseq="I",
            contig_id="17",
            start=237,
            start_offset=0,
            end=237,
            end_offset=0,
            strand="-",
            gene_id="ENSG00000141510",
            gene_name="TP53",
            transcript_id="ENST00000413465",
            transcript_name="TP53-203",
            protein_id="ENSP00000410739",
        ),
        ProteinSubstitution(
            refseq="M",
            altseq="I",
            contig_id="17",
            start=144,
            start_offset=0,
            end=144,
            end_offset=0,
            strand="-",
            gene_id="ENSG00000141510",
            gene_name="TP53",
            transcript_id="ENST00000514944",
            transcript_name="TP53-214",
            protein_id="ENSP00000423862",
        ),
        ProteinSubstitution(
            refseq="M",
            altseq="I",
            contig_id="17",
            start=105,
            start_offset=0,
            end=105,
            end_offset=0,
            strand="-",
            gene_id="ENSG00000141510",
            gene_name="TP53",
            transcript_id="ENST00000509690",
            transcript_name="TP53-212",
            protein_id="ENSP00000425104",
        ),
        ProteinSubstitution(
            refseq="M",
            altseq="I",
            contig_id="17",
            start=78,
            start_offset=0,
            end=78,
            end_offset=0,
            strand="-",
            gene_id="ENSG00000141510",
            gene_name="TP53",
            transcript_id="ENST00000610623",
            transcript_name="TP53-221",
            protein_id="ENSP00000477531",
        ),
        ProteinSubstitution(
            refseq="M",
            altseq="I",
            contig_id="17",
            start=198,
            start_offset=0,
            end=198,
            end_offset=0,
            strand="-",
            gene_id="ENSG00000141510",
            gene_name="TP53",
            transcript_id="ENST00000610292",
            transcript_name="TP53-219",
            protein_id="ENSP00000478219",
        ),
        ProteinSubstitution(
            refseq="M",
            altseq="I",
            contig_id="17",
            start=105,
            start_offset=0,
            end=105,
            end_offset=0,
            strand="-",
            gene_id="ENSG00000141510",
            gene_name="TP53",
            transcript_id="ENST00000510385",
            transcript_name="TP53-213",
            protein_id="ENSP00000478499",
        ),
        ProteinSubstitution(
            refseq="M",
            altseq="I",
            contig_id="17",
            start=198,
            start_offset=0,
            end=198,
            end_offset=0,
            strand="-",
            gene_id="ENSG00000141510",
            gene_name="TP53",
            transcript_id="ENST00000610538",
            transcript_name="TP53-220",
            protein_id="ENSP00000480868",
        ),
        ProteinSubstitution(
            refseq="M",
            altseq="I",
            contig_id="17",
            start=105,
            start_offset=0,
            end=105,
            end_offset=0,
            strand="-",
            gene_id="ENSG00000141510",
            gene_name="TP53",
            transcript_id="ENST00000504937",
            transcript_name="TP53-209",
            protein_id="ENSP00000481179",
        ),
        ProteinSubstitution(
            refseq="M",
            altseq="I",
            contig_id="17",
            start=78,
            start_offset=0,
            end=78,
            end_offset=0,
            strand="-",
            gene_id="ENSG00000141510",
            gene_name="TP53",
            transcript_id="ENST00000618944",
            transcript_name="TP53-224",
            protein_id="ENSP00000481401",
        ),
        ProteinSubstitution(
            refseq="M",
            altseq="I",
            contig_id="17",
            start=198,
            start_offset=0,
            end=198,
            end_offset=0,
            strand="-",
            gene_id="ENSG00000141510",
            gene_name="TP53",
            transcript_id="ENST00000620739",
            transcript_name="TP53-227",
            protein_id="ENSP00000481638",
        ),
        ProteinSubstitution(
            refseq="M",
            altseq="I",
            contig_id="17",
            start=198,
            start_offset=0,
            end=198,
            end_offset=0,
            strand="-",
            gene_id="ENSG00000141510",
            gene_name="TP53",
            transcript_id="ENST00000622645",
            transcript_name="TP53-228",
            protein_id="ENSP00000482222",
        ),
        ProteinSubstitution(
            refseq="M",
            altseq="I",
            contig_id="17",
            start=237,
            start_offset=0,
            end=237,
            end_offset=0,
            strand="-",
            gene_id="ENSG00000141510",
            gene_name="TP53",
            transcript_id="ENST00000617185",
            transcript_name="TP53-223",
            protein_id="ENSP00000482258",
        ),
        ProteinSubstitution(
            refseq="M",
            altseq="I",
            contig_id="17",
            start=198,
            start_offset=0,
            end=198,
            end_offset=0,
            strand="-",
            gene_id="ENSG00000141510",
            gene_name="TP53",
            transcript_id="ENST00000619485",
            transcript_name="TP53-226",
            protein_id="ENSP00000482537",
        ),
        ProteinSubstitution(
            refseq="M",
            altseq="I",
            contig_id="17",
            start=226,
            start_offset=0,
            end=226,
            end_offset=0,
            strand="-",
            gene_id="ENSG00000141510",
            gene_name="TP53",
            transcript_id="ENST00000615910",
            transcript_name="TP53-222",
            protein_id="ENSP00000482903",
        ),
        ProteinSubstitution(
            refseq="M",
            altseq="I",
            contig_id="17",
            start=78,
            start_offset=0,
            end=78,
            end_offset=0,
            strand="-",
            gene_id="ENSG00000141510",
            gene_name="TP53",
            transcript_id="ENST00000619186",
            transcript_name="TP53-225",
            protein_id="ENSP00000484375",
        ),
        ProteinSubstitution(
            refseq="M",
            altseq="I",
            contig_id="17",
            start=105,
            start_offset=0,
            end=105,
            end_offset=0,
            strand="-",
            gene_id="ENSG00000141510",
            gene_name="TP53",
            transcript_id="ENST00000504290",
            transcript_name="TP53-208",
            protein_id="ENSP00000484409",
        ),
        ProteinSubstitution(
            refseq="M",
            altseq="I",
            contig_id="17",
            start=198,
            start_offset=0,
            end=198,
            end_offset=0,
            strand="-",
            gene_id="ENSG00000141510",
            gene_name="TP53",
            transcript_id="ENST00000635293",
            transcript_name="TP53-229",
            protein_id="ENSP00000488924",
        ),
    ]


# -------------------------------------------------------------------------------------------------
# contig_ids
# -------------------------------------------------------------------------------------------------
def test_contig_ids_from_contig_id(ensembl100):
    result = ensembl100.contig_ids("16")
    assert isinstance(result, list)
    assert "16" in result


def test_contig_ids_from_contig_with_chr(ensembl100):
    ret_by_id = ensembl100.contig_ids("chr4")
    assert "4" in ret_by_id


def test_contig_ids_from_exon_id(ensembl100):
    result = ensembl100.contig_ids("ENSE00003826864")
    assert isinstance(result, list)
    assert "16" in result


def test_contig_ids_from_gene(ensembl100):
    ret_by_id = ensembl100.contig_ids("ENSG00000149925")
    ret_by_name = ensembl100.contig_ids("ALDOA")
    assert "16" in ret_by_id
    assert "16" in ret_by_name
    assert ret_by_id == ret_by_name


def test_contig_ids_from_protein_id(ensembl100):
    result = ensembl100.contig_ids("ENSP00000494188")
    assert isinstance(result, list)
    assert "16" in result


def test_contig_ids_from_transcript(ensembl100):
    ret_by_id = ensembl100.contig_ids("ENST00000643777")
    ret_by_name = ensembl100.contig_ids("ALDOA-219")
    assert "16" in ret_by_id
    assert "16" in ret_by_name
    assert ret_by_id == ret_by_name


def test_contig_ids_all(ensembl100):
    result = ensembl100.contig_ids()
    assert isinstance(result, list)
    assert "16" in result


# -------------------------------------------------------------------------------------------------
# exon_ids
# -------------------------------------------------------------------------------------------------
def test_exon_ids_from_contig_id(ensembl100):
    result = ensembl100.exon_ids("16")
    assert isinstance(result, list)
    assert "ENSE00003826864" in result


def test_exon_ids_from_exon_id(ensembl100):
    result = ensembl100.exon_ids("ENSE00003826864")
    assert isinstance(result, list)
    assert "ENSE00003826864" in result


def test_exon_ids_from_gene(ensembl100):
    ret_by_id = ensembl100.exon_ids("ENSG00000149925")
    ret_by_name = ensembl100.exon_ids("ALDOA")
    assert "ENSE00003826864" in ret_by_id
    assert "ENSE00003826864" in ret_by_name
    assert ret_by_id == ret_by_name


def test_exon_ids_from_protein_id(ensembl100):
    result = ensembl100.exon_ids("ENSP00000494188")
    assert isinstance(result, list)
    assert "ENSE00003826864" in result


def test_exon_ids_from_transcript(ensembl100):
    ret_by_id = ensembl100.exon_ids("ENST00000643777")
    ret_by_name = ensembl100.exon_ids("ALDOA-219")
    assert "ENSE00003826864" in ret_by_id
    assert "ENSE00003826864" in ret_by_name
    assert ret_by_id == ret_by_name


def test_exon_ids_all(ensembl100):
    result = ensembl100.exon_ids()
    assert isinstance(result, list)
    assert "ENSE00003826864" in result


# -------------------------------------------------------------------------------------------------
# gene_ids
# -------------------------------------------------------------------------------------------------
def test_gene_ids_different_gene_ids(ensembl69, ensembl100):
    # Gene ID changed bewteen 69 and 100
    # ENSG00000166748 AGBL1
    # ENSG00000273540 AGBL1
    assert ensembl69.gene_ids("AGBL1") == ["ENSG00000166748"]
    assert ensembl100.gene_ids("AGBL1") == ["ENSG00000273540"]


def test_gene_ids_different_gene_names(ensembl69, ensembl100):
    # Gene name changed bewteen 69 and 100
    # ENSG00000118058 MLL
    # ENSG00000118058 KMT2A
    assert ensembl69.gene_ids("MLL") == ["ENSG00000118058"]
    assert ensembl100.gene_ids("KMT2A") == ["ENSG00000118058"]


def test_gene_ids_from_contig_id(ensembl100):
    result = ensembl100.gene_ids("16")
    assert isinstance(result, list)
    assert "ENSG00000149925" in result


def test_gene_ids_from_exon_id(ensembl100):
    result = ensembl100.gene_ids("ENSE00003826864")
    assert isinstance(result, list)
    assert "ENSG00000149925" in result


def test_gene_ids_from_gene(ensembl100):
    ret_by_id = ensembl100.gene_ids("ENSG00000149925")
    ret_by_name = ensembl100.gene_ids("ALDOA")
    assert "ENSG00000149925" in ret_by_id
    assert "ENSG00000149925" in ret_by_name
    assert ret_by_id == ret_by_name


def test_gene_ids_from_protein_id(ensembl100):
    result = ensembl100.gene_ids("ENSP00000494188")
    assert isinstance(result, list)
    assert "ENSG00000149925" in result


def test_gene_ids_from_transcript(ensembl100):
    ret_by_id = ensembl100.gene_ids("ENST00000643777")
    ret_by_name = ensembl100.gene_ids("ALDOA-219")
    assert "ENSG00000149925" in ret_by_id
    assert "ENSG00000149925" in ret_by_name
    assert ret_by_id == ret_by_name


def test_gene_ids_all(ensembl100):
    result = ensembl100.gene_ids()
    assert isinstance(result, list)
    assert "ENSG00000149925" in result


# -------------------------------------------------------------------------------------------------
# gene_names
# -------------------------------------------------------------------------------------------------
def test_gene_names_different_gene_ids(ensembl69, ensembl100):
    # Gene ID changed bewteen 69 and 100
    # ENSG00000204645 SSX4
    # ENSG00000268009 SSX4
    assert ensembl69.gene_names("ENSG00000204645") == ["SSX4"]
    assert ensembl100.gene_names("ENSG00000268009") == ["SSX4"]


def test_gene_names_different_gene_names(ensembl69, ensembl100):
    # Gene name changed bewteen 69 and 100
    # ENSG00000118058 MLL
    # ENSG00000118058 KMT2A
    assert ensembl69.gene_names("ENSG00000118058") == ["MLL"]
    assert ensembl100.gene_names("ENSG00000118058") == ["KMT2A"]


def test_gene_names_from_contig_id(ensembl100):
    result = ensembl100.gene_names("16")
    assert isinstance(result, list)
    assert "ALDOA" in result


def test_gene_names_from_exon_id(ensembl100):
    result = ensembl100.gene_names("ENSE00003826864")
    assert isinstance(result, list)
    assert "ALDOA" in result


def test_gene_names_from_gene(ensembl100):
    ret_by_id = ensembl100.gene_names("ENSG00000149925")
    ret_by_name = ensembl100.gene_names("ALDOA")
    assert "ALDOA" in ret_by_id
    assert "ALDOA" in ret_by_name
    assert ret_by_id == ret_by_name


def test_gene_names_from_protein_id(ensembl100):
    result = ensembl100.gene_names("ENSP00000494188")
    assert isinstance(result, list)
    assert "ALDOA" in result


def test_gene_names_from_refseq_transcript(ensembl100):
    ret_by_id = ensembl100.gene_names("NM_001370259")
    assert "MEN1" in ret_by_id
    ret_by_id = ensembl100.gene_names("NM_007194")
    assert "CHEK2" in ret_by_id
    ret_by_id = ensembl100.gene_names("NM_003072")
    assert "SMARCA4" in ret_by_id
    ret_by_id = ensembl100.gene_names("NM_000314")
    assert "PTEN" in ret_by_id


def test_gene_names_from_transcript(ensembl100):
    ret_by_id = ensembl100.gene_names("ENST00000643777")
    ret_by_name = ensembl100.gene_names("ALDOA-219")
    assert "ALDOA" in ret_by_id
    assert "ALDOA" in ret_by_name
    assert ret_by_id == ret_by_name


def test_gene_names_all(ensembl100):
    result = ensembl100.gene_names()
    assert isinstance(result, list)
    assert "ALDOA" in result


# -------------------------------------------------------------------------------------------------
# protein_ids
# -------------------------------------------------------------------------------------------------
def test_protein_ids_from_contig_id(ensembl100):
    result = ensembl100.protein_ids("16")
    assert isinstance(result, list)
    assert "ENSP00000494188" in result


def test_protein_ids_from_exon_id(ensembl100):
    result = ensembl100.protein_ids("ENSE00003826864")
    assert isinstance(result, list)
    assert "ENSP00000494188" in result


def test_protein_ids_from_gene(ensembl100):
    ret_by_id = ensembl100.protein_ids("ENSG00000149925")
    ret_by_name = ensembl100.protein_ids("ALDOA")
    assert "ENSP00000494188" in ret_by_id
    assert "ENSP00000494188" in ret_by_name
    assert ret_by_id == ret_by_name


def test_protein_ids_from_protein_id(ensembl100):
    result = ensembl100.protein_ids("ENSP00000494188")
    assert isinstance(result, list)
    assert "ENSP00000494188" in result


def test_protein_ids_from_transcript(ensembl100):
    ret_by_id = ensembl100.protein_ids("ENST00000643777")
    ret_by_name = ensembl100.protein_ids("ALDOA-219")
    assert "ENSP00000494188" in ret_by_id
    assert "ENSP00000494188" in ret_by_name
    assert ret_by_id == ret_by_name


def test_protein_ids_all(ensembl100):
    result = ensembl100.protein_ids()
    assert isinstance(result, list)
    assert "ENSP00000494188" in result


# -------------------------------------------------------------------------------------------------
# transcript_ids
# -------------------------------------------------------------------------------------------------
def test_transcript_ids_from_contig_id(ensembl100):
    result = ensembl100.transcript_ids("16")
    assert isinstance(result, list)
    assert "ENST00000643777" in result


def test_transcript_ids_from_exon_id(ensembl100):
    result = ensembl100.transcript_ids("ENSE00003826864")
    assert isinstance(result, list)
    assert "ENST00000643777" in result


def test_transcript_ids_from_gene(ensembl100):
    ret_by_id = ensembl100.transcript_ids("ENSG00000149925")
    ret_by_name = ensembl100.transcript_ids("ALDOA")
    assert "ENST00000643777" in ret_by_id
    assert "ENST00000643777" in ret_by_name
    assert ret_by_id == ret_by_name


def test_transcript_ids_from_protein_id(ensembl100):
    result = ensembl100.transcript_ids("ENSP00000494188")
    assert isinstance(result, list)
    assert "ENST00000643777" in result


def test_transcript_ids_from_transcript(ensembl100):
    ret_by_id = ensembl100.transcript_ids("ENST00000643777")
    ret_by_name = ensembl100.transcript_ids("ALDOA-219")
    assert "ENST00000643777" in ret_by_id
    assert "ENST00000643777" in ret_by_name
    assert ret_by_id == ret_by_name


def test_transcript_ids_all(ensembl100):
    result = ensembl100.transcript_ids()
    assert isinstance(result, list)
    assert "ENST00000643777" in result


# -------------------------------------------------------------------------------------------------
# transcript_names
# -------------------------------------------------------------------------------------------------
def test_transcript_names_from_contig_id(ensembl100):
    result = ensembl100.transcript_names("16")
    assert isinstance(result, list)
    assert "ALDOA-219" in result


def test_transcript_names_from_exon_id(ensembl100):
    result = ensembl100.transcript_names("ENSE00003826864")
    assert isinstance(result, list)
    assert "ALDOA-219" in result


def test_transcript_names_from_gene(ensembl100):
    ret_by_id = ensembl100.transcript_names("ENSG00000149925")
    ret_by_name = ensembl100.transcript_names("ALDOA")
    assert "ALDOA-219" in ret_by_id
    assert "ALDOA-219" in ret_by_name
    assert ret_by_id == ret_by_name


def test_transcript_names_from_protein_id(ensembl100):
    result = ensembl100.transcript_names("ENSP00000494188")
    assert isinstance(result, list)
    assert "ALDOA-219" in result


def test_transcript_names_from_transcript(ensembl100):
    ret_by_id = ensembl100.transcript_names("ENST00000643777")
    ret_by_name = ensembl100.transcript_names("ALDOA-219")
    assert "ALDOA-219" in ret_by_id
    assert "ALDOA-219" in ret_by_name
    assert ret_by_id == ret_by_name


def test_transcript_names_all(ensembl100):
    result = ensembl100.transcript_names()
    assert isinstance(result, list)
    assert "ALDOA-219" in result


# -------------------------------------------------------------------------------------------------
# is_canonical_transcript
# -------------------------------------------------------------------------------------------------
def test_is_canonical_transcript_true(ensembl100):
    assert ensembl100.is_canonical_transcript("ENST00000000233") is True


def test_is_canonical_transcript_false(ensembl100):
    assert ensembl100.is_canonical_transcript("spam") is False


# -------------------------------------------------------------------------------------------------
# is_contig
# -------------------------------------------------------------------------------------------------
def test_is_contig_false(ensembl100):
    assert ensembl100.is_contig("spam") is False


def test_is_contig_true(ensembl100):
    assert ensembl100.is_contig("4") is True


def test_is_contig_true_alias(ensembl100):
    assert ensembl100.is_contig("chr4") is True


# -------------------------------------------------------------------------------------------------
# is_exon
# -------------------------------------------------------------------------------------------------
def test_is_exon_false(ensembl100):
    assert ensembl100.is_exon("spam") is False


def test_is_exon_true(ensembl100):
    assert ensembl100.is_exon("ENSE00003826864") is True


# -------------------------------------------------------------------------------------------------
# is_gene
# -------------------------------------------------------------------------------------------------
def test_is_gene_false(ensembl100):
    assert ensembl100.is_gene("spam") is False


def test_is_gene_true_from_id(ensembl100):
    assert ensembl100.is_gene("ENSG00000149925") is True


def test_is_gene_true_from_name(ensembl100):
    assert ensembl100.is_gene("ALDOA") is True


# -------------------------------------------------------------------------------------------------
# is_protein
# -------------------------------------------------------------------------------------------------
def test_is_protein_false(ensembl100):
    assert ensembl100.is_protein("spam") is False


def test_is_protein_true(ensembl100):
    assert ensembl100.is_protein("ENSP00000494188") is True


# -------------------------------------------------------------------------------------------------
# is_transcript
# -------------------------------------------------------------------------------------------------
def test_is_transcript_false(ensembl100):
    assert ensembl100.is_transcript("spam") is False


def test_is_transcript_true_from_id(ensembl100):
    assert ensembl100.is_transcript("ENST00000643777") is True


def test_is_transcript_true_from_name(ensembl100):
    assert ensembl100.is_transcript("ALDOA-219") is True


# -------------------------------------------------------------------------------------------------
# sequence
# -------------------------------------------------------------------------------------------------
@pytest.fixture
def test_sequence_cdna_pos():
    return CdnaPosition(
        "4",
        7,
        0,
        9,
        0,
        "+",
        "ENSG00000157404",
        "KIT",
        "ENST00000288135",
        "KIT-201",
        "ENSP00000288135",
    )


def test_sequence_cdna(ensembl100, test_sequence_cdna_pos):
    assert ensembl100.sequence(test_sequence_cdna_pos) == "GGC"


@pytest.fixture
def test_sequence_dna_pos_plus():
    return DnaPosition("4", 54695512, 0, 54695514, 0, "+")


@pytest.fixture
def test_sequence_dna_pos_minus():
    return DnaPosition("4", 54695512, 0, 54695514, 0, "-")


def test_sequence_dna(ensembl100, test_sequence_dna_pos_plus, test_sequence_dna_pos_minus):
    assert ensembl100.sequence(test_sequence_dna_pos_plus) == "GCT"
    assert ensembl100.sequence(test_sequence_dna_pos_minus) == "AGC"


@pytest.fixture
def test_sequence_protein_pos():
    return ProteinPosition(
        "4",
        3,
        0,
        4,
        0,
        "+",
        "ENSG00000157404",
        "KIT",
        "ENST00000288135",
        "KIT-201",
        "ENSP00000288135",
    )


def test_sequence_protein(ensembl100, test_sequence_protein_pos):
    assert ensembl100.sequence(test_sequence_protein_pos) == "GA"


@pytest.fixture
def test_sequence_rna_pos():
    return RnaPosition(
        "4", 126, 0, 128, 0, "+", "ENSG00000157404", "KIT", "ENST00000288135", "KIT-201"
    )


def test_sequence_rna(ensembl100, test_sequence_rna_pos):
    assert ensembl100.sequence(test_sequence_rna_pos) == "GCT"


def test_sequence_from_string(ensembl100):
    assert ensembl100.sequence("ENST00000288135:c.126_128delinsGT") == "GT"


def test_sequence_from_string_strand(ensembl100):
    assert ensembl100.sequence("ENST00000288135:c.126_128delinsGT", strand="-") == "AC"


def test_sequence_from_string_window(ensembl100):
    assert (
        ensembl100.sequence("ENST00000288135:c.126_128delinsGT", window=20)
        == "CCATCCAGGGTATCAGACTT"
    )


def test_sequence_from_string_ambiguous(ensembl100):
    with pytest.raises(ValueError):
        ensembl100.sequence("KRAS:c.126_128delinsGT", window=20)


def test_sequence_fusion_plus_plus_read_through(ensembl69):
    # (BCR,JAK2):fusion(e.1,e.15)
    # BCR exon 1: TTCCAGGACTGCAGAACTGGCCCAG...GAGGGCGCCTTCCATGGAGACGCAG
    # JAK2 exon 15: ATATTCTGGTTCAGGAGTTTGTAAA...GTTGGCATGGGCCATGCATTTTCTA
    assert (
        ensembl69.sequence("ENST00000305877:r.1_2030::ENST00000381652:r.2359_2486", window=50)
        == "GAGGGCGCCTTCCATGGAGACGCAGATATTCTGGTTCAGGAGTTTGTAAA"
    )


def test_sequence_fusion_minus_minus_read_through(ensembl69):
    # (ABCA5,PPP4R1L):fusion(e.3,e.4)
    # ABCA5 exon 3: GAAATTCTTTTTCCACTATTTTTTT...GTGTCTACTGATCATCTACCTGATG
    # PPP4R1L exon 4: GATGTAATACCTCAGCCGCTGCTAG...TGAAACACTGGCTTCTGATGTACAG
    assert (
        ensembl69.sequence("ENST00000392676:r.168_372::ENST00000497138:r.753_938", window=50)
        == "GTGTCTACTGATCATCTACCTGATGGATGTAATACCTCAGCCGCTGCTAG"
    )


def test_sequence_fusion_plus_minus_read_through(ensembl69):
    # (CTNNA1,GLRA1):fusion(e.7,e.4)
    # CTNNA1 exon 7: AAACAAATCATTGTGGACCCCTTGA...CCTGCTTTCGGAGTACATGGGCAAT
    # GLRA1 exon 4: GACTATAGGGTCAACATCTTCCTGC...ATGGGAATGTCCTCTACAGCATCAG
    assert (
        ensembl69.sequence("ENST00000302763:r.949_1152::ENST00000455880:r.540_763", window=50)
        == "CCTGCTTTCGGAGTACATGGGCAATGACTATAGGGTCAACATCTTCCTGC"
    )


def test_sequence_fusion_minus_plus_read_through(ensembl69):
    # (LYRM5,JAK2):fusion(e.3,e.15)
    # LYRM5 exon 3: CTGCTGTATCTTGGACGAGACTATC...GGAAATAAATAAATAATGTTATCCT
    # JAK2 exon 15: ATATTCTGGTTCAGGAGTTTGTAAA...GTTGGCATGGGCCATGCATTTTCTA
    assert (
        ensembl69.sequence("ENST00000381356:r.211_1134::ENST00000381652:r.2359_2486", window=50)
        == "GGAAATAAATAAATAATGTTATCCTATATTCTGGTTCAGGAGTTTGTAAA"
    )


# -------------------------------------------------------------------------------------------------
# normalize_id
# -------------------------------------------------------------------------------------------------
def test_normalize_id_contig_id(ensembl100):
    assert ensembl100.normalize_id("4") == [("4", CONTIG_ID)]


def test_normalize_id_exon_id(ensembl100):
    assert ensembl100.normalize_id("ENSE00003826864") == [("ENSE00003826864", EXON_ID)]


def test_normalize_id_gene_id(ensembl100):
    assert ensembl100.normalize_id("ENSG00000149925") == [("ENSG00000149925", GENE_ID)]


def test_normalize_id_gene_name(ensembl100):
    assert ensembl100.normalize_id("ALDOA") == [("ALDOA", GENE_NAME)]


def test_normalize_id_protein_id(ensembl100):
    assert ensembl100.normalize_id("ENSP00000494188") == [("ENSP00000494188", PROTEIN_ID)]


def test_normalize_id_refseq_transcript_id(ensembl100):
    assert ensembl100.normalize_id("NM_000314.4") == [("ENST00000371953", TRANSCRIPT_ID)]


def test_normalize_id_transcript_id(ensembl100):
    assert ensembl100.normalize_id("ENST00000643777") == [("ENST00000643777", TRANSCRIPT_ID)]


def test_normalize_id_transcript_name(ensembl100):
    assert ensembl100.normalize_id("ALDOA-219") == [("ALDOA-219", TRANSCRIPT_NAME)]


# -------------------------------------------------------------------------------------------------
# cdna
# -------------------------------------------------------------------------------------------------
@pytest.fixture
def test_cdna_pos():
    return CdnaPosition(
        contig_id="5",
        start=1,
        start_offset=0,
        end=3399,
        end_offset=0,
        strand="-",
        gene_id="ENSG00000164362",
        gene_name="TERT",
        transcript_id="ENST00000310581",
        transcript_name="TERT-201",
        protein_id="ENSP00000309572",
    )


@pytest.mark.parametrize(
    "feature,num_results",
    [
        ("5", 4289),
        ("ENSE00003896691", 1),
        ("ENSG00000164362", 4),
        ("ENSP00000309572", 1),
        ("ENST00000310581", 1),
        ("TERT", 4),
        ("TERT-201", 1),
    ],
)
def test_cdna(ensembl100, test_cdna_pos, feature, num_results):
    results = ensembl100.cdna(feature)
    assert len(results) == num_results
    assert test_cdna_pos in results


def test_cdna_canonical(ensembl100):
    results = ensembl100.cdna("ARF5", canonical=True)
    assert len(results) == 1
    assert results[0].transcript_id == "ENST00000000233"


# -------------------------------------------------------------------------------------------------
# dna
# -------------------------------------------------------------------------------------------------
@pytest.fixture
def expected_dna():
    return DnaPosition(
        contig_id="5", start=1253147, start_offset=0, end=1295068, end_offset=0, strand="-"
    )


@pytest.mark.parametrize(
    "feature,num_results",
    [
        ("5", 2987),
        ("ENSE00003896691", 1),
        ("ENSG00000164362", 1),
        ("ENSP00000309572", 1),
        ("ENST00000310581", 1),
        ("TERT", 1),
        ("TERT-201", 1),
    ],
)
def test_gene(ensembl100, expected_dna, feature, num_results):
    results = ensembl100.gene(feature)
    assert len(results) == num_results
    assert expected_dna in results


@pytest.fixture
def test_dna_pos_whole_contig():
    return DnaPosition(
        contig_id="5", start=1, start_offset=0, end=181538259, end_offset=0, strand="-"
    )


@pytest.mark.parametrize(
    "feature,num_results",
    [
        ("5", 2),
        ("ENSE00003896691", 1),
        ("ENSG00000164362", 1),
        ("ENSP00000309572", 1),
        ("ENST00000310581", 1),
        ("TERT", 1),
        ("TERT-201", 1),
    ],
)
def test_dna(ensembl100, test_dna_pos_whole_contig, feature, num_results):
    results = ensembl100.dna(feature)
    assert len(results) == num_results
    assert test_dna_pos_whole_contig in results


# -------------------------------------------------------------------------------------------------
# exon
# -------------------------------------------------------------------------------------------------
@pytest.fixture
def test_exon_pos():
    return ExonPosition(
        contig_id="5",
        start=1,
        start_offset=0,
        end=1,
        end_offset=0,
        strand="-",
        gene_id="ENSG00000164362",
        gene_name="TERT",
        transcript_id="ENST00000310581",
        transcript_name="TERT-201",
        exon_id="ENSE00003896691",
    )


@pytest.mark.parametrize(
    "feature,num_results",
    [
        ("5", 62673),
        ("ENSE00003896691", 1),
        ("ENSG00000164362", 79),
        ("ENSP00000309572", 33),
        ("ENST00000310581", 33),
        ("TERT", 79),
        ("TERT-201", 33),
    ],
)
def test_exon(ensembl100, test_exon_pos, feature, num_results):
    results = ensembl100.exon(feature)
    assert len(results) == num_results
    assert test_exon_pos in results


def test_exon_canonical(ensembl100):
    results = ensembl100.exon("ARF5", canonical=True)
    assert len(results) == 6
    for exon in results:
        assert exon.transcript_id == "ENST00000000233"


# -------------------------------------------------------------------------------------------------
# protein
# -------------------------------------------------------------------------------------------------
@pytest.fixture
def test_protein_pos():
    return ProteinPosition(
        contig_id="5",
        start=1,
        start_offset=0,
        end=1133,
        end_offset=0,
        strand="-",
        gene_id="ENSG00000164362",
        gene_name="TERT",
        transcript_id="ENST00000310581",
        transcript_name="TERT-201",
        protein_id="ENSP00000309572",
    )


@pytest.mark.parametrize(
    "feature,num_results",
    [
        ("5", 4289),
        ("ENSE00003896691", 1),
        ("ENSG00000164362", 4),
        ("ENSP00000309572", 1),
        ("ENST00000310581", 1),
        ("TERT", 4),
        ("TERT-201", 1),
    ],
)
def test_protein(ensembl100, test_protein_pos, feature, num_results):
    results = ensembl100.protein(feature)
    assert len(results) == num_results
    assert test_protein_pos in results


def test_protein_canonical(ensembl100):
    results = ensembl100.protein("ARF5", canonical=True)
    assert len(results) == 1
    assert results[0].transcript_id == "ENST00000000233"


# -------------------------------------------------------------------------------------------------
# rna
# -------------------------------------------------------------------------------------------------
@pytest.fixture
def test_rna_pos():
    return RnaPosition(
        contig_id="5",
        start=1,
        start_offset=0,
        end=4039,
        end_offset=0,
        strand="-",
        gene_id="ENSG00000164362",
        gene_name="TERT",
        transcript_id="ENST00000310581",
        transcript_name="TERT-201",
    )


@pytest.mark.parametrize(
    "feature,num_results",
    [
        ("5", 10806),
        ("ENSE00003896691", 1),
        ("ENSG00000164362", 7),
        ("ENSP00000309572", 1),
        ("ENST00000310581", 1),
        ("TERT", 7),
        ("TERT-201", 1),
    ],
)
def test_transcript(ensembl100, test_rna_pos, feature, num_results):
    results = ensembl100.rna(feature)
    assert len(results) == num_results
    assert test_rna_pos in results


def test_rna_canonical(ensembl100):
    results = ensembl100.rna("ARF5", canonical=True)
    assert len(results) == 1
    assert results[0].transcript_id == "ENST00000000233"


# -------------------------------------------------------------------------------------------------
# translate_cdna_variant
# -------------------------------------------------------------------------------------------------
@pytest.fixture
def test_translate_cdna_variant_pos_1():
    return CdnaPosition(
        "4",
        38,
        0,
        38,
        0,
        "+",
        "ENSG00000157404",
        "KIT",
        "ENST00000288135",
        "KIT-201",
        "ENSP00000288135",
    )


def test_translate_cdna_variant_1(ensembl100, test_translate_cdna_variant_pos_1):
    # A simple T>A substitution
    # GTT -> GAT
    assert ensembl100.translate_cdna_variant(test_translate_cdna_variant_pos_1, "A") == [
        ("D", False)
    ]


def test_translate_cdna_variant_2(ensembl100, test_translate_cdna_variant_pos_1):
    # An ambiguous substitution of either T>A or T>C
    # GTT -> GAT or GCT
    assert ensembl100.translate_cdna_variant(test_translate_cdna_variant_pos_1, "M") == [
        ("A", False),
        ("D", False),
    ]


def test_translate_cdna_variant_3(ensembl100, test_translate_cdna_variant_pos_1):
    # A frameshifting deletion of T
    # GTT -> GT
    assert ensembl100.translate_cdna_variant(test_translate_cdna_variant_pos_1, "") == [("", True)]


@pytest.fixture
def test_translate_cdna_variant_pos_2():
    return CdnaPosition(
        "4",
        38,
        0,
        40,
        0,
        "+",
        "ENSG00000157404",
        "KIT",
        "ENST00000288135",
        "KIT-201",
        "ENSP00000288135",
    )


def test_translate_cdna_variant_4(ensembl100, test_translate_cdna_variant_pos_2):
    # A delins of TTC>AAA
    # GTTCTG -> GAAATG
    assert ensembl100.translate_cdna_variant(test_translate_cdna_variant_pos_2, "AAA") == [
        ("EM", False)
    ]


def test_translate_cdna_variant_5(ensembl100, test_translate_cdna_variant_pos_2):
    # A non-frameshifting deletion of TTC
    # GTTCTG -> GTG
    assert ensembl100.translate_cdna_variant(test_translate_cdna_variant_pos_2, "") == [
        ("V", False)
    ]


@pytest.fixture
def test_translate_cdna_variant_pos_3():
    return CdnaPosition(
        "4",
        1674,
        0,
        1675,
        0,
        "+",
        "ENSG00000157404",
        "KIT",
        "ENST00000288135",
        "KIT-201",
        "ENSP00000288135",
    )


def test_translate_cdna_variant_6(ensembl100, test_translate_cdna_variant_pos_3):
    # A non-frameshift insertion of TTC
    # GG -> AAGTTCG
    assert ensembl100.translate_cdna_variant(test_translate_cdna_variant_pos_3, "GTTCG") == [
        ("KFV", False)
    ]


def test_translate_cdna_variant_7(ensembl100, test_translate_cdna_variant_pos_3):
    # A frameshifting insertion of TTCA
    # GG -> GTTCAG frameshift
    assert ensembl100.translate_cdna_variant(test_translate_cdna_variant_pos_3, "GTTCAG") == [
        ("KFS", True)
    ]


# -------------------------------------------------------------------------------------------------
# parse
# -------------------------------------------------------------------------------------------------
def test_parse_cdna_position(ensembl100):
    result = ensembl100.parse("ENST00000288135:c.68-1")
    assert result == [
        CdnaPosition(
            contig_id="4",
            start=68,
            start_offset=-1,
            end=68,
            end_offset=-1,
            strand="+",
            gene_id="ENSG00000157404",
            gene_name="KIT",
            transcript_id="ENST00000288135",
            transcript_name="KIT-201",
            protein_id="ENSP00000288135",
        )
    ]


def test_parse_cdna_intron_deletion(ensembl100):
    result = ensembl100.parse("ENST00000372348:c.136+596_136+650del")
    assert result == [
        CdnaDeletion(
            contig_id="9",
            start=136,
            start_offset=596,
            end=136,
            end_offset=650,
            strand="+",
            gene_id="ENSG00000097007",
            gene_name="ABL1",
            transcript_id="ENST00000372348",
            transcript_name="ABL1-202",
            protein_id="ENSP00000361423",
            refseq="TCCATAAGGAGTAATCTCTTCCTCGTTGATGAAGCTTTCATCCTGTCTTCTCCCT",
            altseq="",
        )
    ]


def test_parse_cdna_stop_deletion(ensembl100):
    # TODO: Support positions offset from stop codon
    # result = ensembl100.parse("ENST00000257430:c.*6_*7del")
    # assert result == [
    #     CdnaDeletion(
    #         contig_id="9",
    #         start=10704,
    #         start_offset=6,
    #         end=10704,
    #         end_offset=7,
    #         strand="+",
    #         gene_id="ENSG00000134982",
    #         gene_name="ABL1",
    #         transcript_id="ENST00000257430",
    #         transcript_name="ABL1-201",
    #         protein_id="ENSP00000257430",
    #         refseq="AG",
    #         altseq="",
    #     )
    # ]
    with pytest.raises(ValueError):
        ensembl100.parse("ENST00000257430:c.*6_*7del")


def test_parse_cdna_promoter_delins_multiple(ensembl100):
    result = ensembl100.parse("ENST00000257430:c.-30347_-30346delinsA")
    assert result == [
        CdnaDelins(
            contig_id="5",
            start=1,
            start_offset=-30347,
            end=1,
            end_offset=-30346,
            strand="+",
            gene_id="ENSG00000134982",
            gene_name="APC",
            transcript_id="ENST00000257430",
            transcript_name="APC-201",
            protein_id="ENSP00000257430",
            refseq="CG",
            altseq="A",
        )
    ]


def test_parse_cdna_promoter_delins_to_deletion(ensembl100):
    result = ensembl100.parse("ENST00000257430:c.-30353_-30352delinsA")
    assert result == [
        CdnaDeletion(
            contig_id="5",
            start=1,
            start_offset=-30353,
            end=1,
            end_offset=-30353,
            strand="+",
            gene_id="ENSG00000134982",
            gene_name="APC",
            transcript_id="ENST00000257430",
            transcript_name="APC-201",
            protein_id="ENSP00000257430",
            refseq="T",
            altseq="",
        )
    ]


def test_parse_cdna_duplication(ensembl100):
    result = ensembl100.parse("ENST00000307078:c.1394_1399dup")
    assert result == [
        CdnaDuplication(
            contig_id="17",
            start=1394,
            start_offset=0,
            end=1399,
            end_offset=0,
            strand="-",
            gene_id="ENSG00000168646",
            gene_name="AXIN2",
            transcript_id="ENST00000307078",
            transcript_name="AXIN2-201",
            protein_id="ENSP00000302625",
            refseq="GCTCCC",
            altseq="GCTCCCGCTCCC",
        )
    ]


def test_parse_cdna_promoter_substitution(ensembl100):
    result = ensembl100.parse("ENST00000257430:c.-290G>A")
    assert result == [
        CdnaSubstitution(
            contig_id="5",
            start=1,
            start_offset=-290,
            end=1,
            end_offset=-290,
            strand="+",
            gene_id="ENSG00000134982",
            gene_name="APC",
            transcript_id="ENST00000257430",
            transcript_name="APC-201",
            protein_id="ENSP00000257430",
            refseq="G",
            altseq="A",
        )
    ]


def test_parse_cdna_substitution(ensembl100):
    result = ensembl100.parse("ENST00000256078:c.38G>A")
    assert result == [
        CdnaSubstitution(
            contig_id="12",
            start=38,
            start_offset=0,
            end=38,
            end_offset=0,
            strand="-",
            gene_id="ENSG00000133703",
            gene_name="KRAS",
            transcript_id="ENST00000256078",
            transcript_name="KRAS-201",
            protein_id="ENSP00000256078",
            refseq="G",
            altseq="A",
        )
    ]


def test_parse_dna_position(ensembl100):
    result = ensembl100.parse("5:g.1282623_1282626")
    assert result == [
        DnaPosition(
            contig_id="5", start=1282623, start_offset=0, end=1282626, end_offset=0, strand=""
        )
    ]


def test_parse_dna_substitution(ensembl100):
    result = ensembl100.parse("5:g.1282623C>G")
    assert result == [
        DnaSubstitution(
            contig_id="5",
            start=1282623,
            start_offset=0,
            end=1282623,
            end_offset=0,
            strand="",
            refseq="C",
            altseq="G",
        )
    ]


def test_parse_exon_fusion(ensembl100):
    result = ensembl100.parse("ENST00000315869:e.3_4::ENST00000271526:e.2")
    assert result == [
        ExonFusion(
            ExonPosition(
                contig_id="X",
                start=3,
                start_offset=0,
                end=4,
                end_offset=0,
                strand="-",
                gene_id="ENSG00000068323",
                gene_name="TFE3",
                transcript_id="ENST00000315869",
                transcript_name="TFE3-201",
                exon_id="ENSE00003528623",
            ),
            ExonPosition(
                contig_id="1",
                start=2,
                start_offset=0,
                end=2,
                end_offset=0,
                strand="+",
                gene_id="ENSG00000143294",
                gene_name="PRCC",
                transcript_id="ENST00000271526",
                transcript_name="PRCC-201",
                exon_id="ENSE00003525835",
            ),
        )
    ]


# -------------------------------------------------------------------------------------------------
# variant
# -------------------------------------------------------------------------------------------------
def test_variant_cdna_minimal(ensembl100):
    result = ensembl100.variant(position_type="cdna", feature="ENST00000375562", start=123)
    assert result == [
        CdnaPosition(
            contig_id="6",
            start=123,
            start_offset=0,
            end=123,
            end_offset=0,
            strand="-",
            gene_id="ENSG00000204385",
            gene_name="SLC44A4",
            transcript_id="ENST00000375562",
            transcript_name="SLC44A4-203",
            protein_id="ENSP00000364712",
        )
    ]


def test_variant_cdna_position(ensembl100):
    result = ensembl100.variant(
        position_type="cdna",
        feature="ENST00000288135",
        start=68,
        start_offset=-1,
        end=68,
        end_offset=-1,
        strand="+",
    )
    assert result == [
        CdnaPosition(
            contig_id="4",
            start=68,
            start_offset=-1,
            end=68,
            end_offset=-1,
            strand="+",
            gene_id="ENSG00000157404",
            gene_name="KIT",
            transcript_id="ENST00000288135",
            transcript_name="KIT-201",
            protein_id="ENSP00000288135",
        )
    ]


def test_variant_cdna_substitution(ensembl100):
    result = ensembl100.variant(
        position_type="cdna",
        feature="ENST00000256078",
        start=38,
        start_offset=0,
        end=38,
        end_offset=0,
        strand="-",
        refseq="G",
        altseq="A",
        variant_type="substitution",
    )
    assert result == [
        CdnaSubstitution(
            contig_id="12",
            start=38,
            start_offset=0,
            end=38,
            end_offset=0,
            strand="-",
            gene_id="ENSG00000133703",
            gene_name="KRAS",
            transcript_id="ENST00000256078",
            transcript_name="KRAS-201",
            protein_id="ENSP00000256078",
            refseq="G",
            altseq="A",
        )
    ]


def test_variant_dna_minimal(ensembl100):
    result = ensembl100.variant(position_type="dna", feature="5", start=1282623)
    assert result == [
        DnaPosition(
            contig_id="5", start=1282623, start_offset=0, end=1282623, end_offset=0, strand=""
        )
    ]


def test_variant_dna_position(ensembl100):
    result = ensembl100.variant(
        position_type="dna", feature="5", start=1282623, end=1282626, strand="-"
    )
    assert result == [
        DnaPosition(
            contig_id="5", start=1282623, start_offset=0, end=1282626, end_offset=0, strand="-"
        )
    ]


def test_variant_dna_insertion_normalized(ensembl100):
    result = ensembl100.variant(
        position_type="dna",
        feature="1",
        start=826577,
        end=826577,
        strand="+",
        refseq="A",
        altseq="AT",
        variant_type="insertion",
    )
    assert result == [
        DnaInsertion(
            contig_id="1",
            start=826577,
            start_offset=0,
            end=826578,
            end_offset=0,
            strand="+",
            refseq="AC",
            altseq="ATC",
        )
    ]


def test_variant_dna_substitution(ensembl100):
    result = ensembl100.variant(
        position_type="dna",
        feature="5",
        start=1282623,
        end=1282623,
        strand="+",
        refseq="C",
        altseq="G",
        variant_type="substitution",
    )
    assert result == [
        DnaSubstitution(
            contig_id="5",
            start=1282623,
            start_offset=0,
            end=1282623,
            end_offset=0,
            strand="+",
            refseq="C",
            altseq="G",
        )
    ]


def test_variant_exon_fusion(ensembl100):
    result = ensembl100.variant(
        position_type="exon",
        feature="ENST00000315869",
        start=3,
        end=4,
        strand="-",
        variant_type="fusion",
        position_type2="exon",
        feature2="ENST00000271526",
        start2=2,
        end2=2,
        strand2="+",
    )
    assert result == [
        ExonFusion(
            ExonPosition(
                contig_id="X",
                start=3,
                start_offset=0,
                end=4,
                end_offset=0,
                strand="-",
                gene_id="ENSG00000068323",
                gene_name="TFE3",
                transcript_id="ENST00000315869",
                transcript_name="TFE3-201",
                exon_id="ENSE00003528623",
            ),
            ExonPosition(
                contig_id="1",
                start=2,
                start_offset=0,
                end=2,
                end_offset=0,
                strand="+",
                gene_id="ENSG00000143294",
                gene_name="PRCC",
                transcript_id="ENST00000271526",
                transcript_name="PRCC-201",
                exon_id="ENSE00003525835",
            ),
        )
    ]


# -------------------------------------------------------------------------------------------------
# to_all
# -------------------------------------------------------------------------------------------------
def test_to_all_from_cdna_delins(ensembl100):
    result = ensembl100.to_all("ENST00000288135:c.126_128delinsGT")
    assert result == {
        "cdna": [
            CdnaDelins(
                refseq="AAA",
                altseq="GT",
                contig_id="4",
                start=126,
                start_offset=0,
                end=128,
                end_offset=0,
                strand="+",
                gene_id="ENSG00000157404",
                gene_name="KIT",
                transcript_id="ENST00000288135",
                transcript_name="KIT-201",
                protein_id="ENSP00000288135",
            )
        ],
        "dna": [
            DnaDelins(
                refseq="AAA",
                altseq="GT",
                contig_id="4",
                start=54695570,
                start_offset=0,
                end=54695572,
                end_offset=0,
                strand="+",
            )
        ],
        "exon": [],
        "protein": [
            ProteinFrameshift(
                refseq="K",
                altseq="",
                contig_id="4",
                start=43,
                start_offset=0,
                end=43,
                end_offset=0,
                strand="+",
                gene_id="ENSG00000157404",
                gene_name="KIT",
                transcript_id="ENST00000288135",
                transcript_name="KIT-201",
                protein_id="ENSP00000288135",
            )
        ],
        "rna": [
            RnaDelins(
                refseq="AAA",
                altseq="GT",
                contig_id="4",
                start=184,
                start_offset=0,
                end=186,
                end_offset=0,
                strand="+",
                gene_id="ENSG00000157404",
                gene_name="KIT",
                transcript_id="ENST00000288135",
                transcript_name="KIT-201",
            )
        ],
    }


def test_to_all_from_dna_position(ensembl100):
    result = ensembl100.to_all("4:g.54695570_54695572")
    assert result == {
        "cdna": [
            CdnaPosition(
                contig_id="4",
                start=126,
                start_offset=0,
                end=128,
                end_offset=0,
                strand="+",
                gene_id="ENSG00000157404",
                gene_name="KIT",
                transcript_id="ENST00000288135",
                transcript_name="KIT-201",
                protein_id="ENSP00000288135",
            ),
            CdnaPosition(
                contig_id="4",
                start=126,
                start_offset=0,
                end=128,
                end_offset=0,
                strand="+",
                gene_id="ENSG00000157404",
                gene_name="KIT",
                transcript_id="ENST00000412167",
                transcript_name="KIT-202",
                protein_id="ENSP00000390987",
            ),
        ],
        "dna": [
            DnaPosition(
                contig_id="4", start=54695570, start_offset=0, end=54695572, end_offset=0, strand=""
            )
        ],
        "exon": [
            ExonPosition(
                contig_id="4",
                start=2,
                start_offset=0,
                end=2,
                end_offset=0,
                strand="+",
                gene_id="ENSG00000157404",
                gene_name="KIT",
                transcript_id="ENST00000288135",
                transcript_name="KIT-201",
                exon_id="ENSE00001032350",
            ),
            ExonPosition(
                contig_id="4",
                start=2,
                start_offset=0,
                end=2,
                end_offset=0,
                strand="+",
                gene_id="ENSG00000157404",
                gene_name="KIT",
                transcript_id="ENST00000412167",
                transcript_name="KIT-202",
                exon_id="ENSE00001032350",
            ),
            ExonPosition(
                contig_id="4",
                start=2,
                start_offset=0,
                end=2,
                end_offset=0,
                strand="+",
                gene_id="ENSG00000157404",
                gene_name="KIT",
                transcript_id="ENST00000514582",
                transcript_name="KIT-204",
                exon_id="ENSE00002084370",
            ),
        ],
        "protein": [
            ProteinPosition(
                contig_id="4",
                start=42,
                start_offset=0,
                end=43,
                end_offset=0,
                strand="+",
                gene_id="ENSG00000157404",
                gene_name="KIT",
                transcript_id="ENST00000288135",
                transcript_name="KIT-201",
                protein_id="ENSP00000288135",
            ),
            ProteinPosition(
                contig_id="4",
                start=42,
                start_offset=0,
                end=43,
                end_offset=0,
                strand="+",
                gene_id="ENSG00000157404",
                gene_name="KIT",
                transcript_id="ENST00000412167",
                transcript_name="KIT-202",
                protein_id="ENSP00000390987",
            ),
        ],
        "rna": [
            RnaPosition(
                contig_id="4",
                start=184,
                start_offset=0,
                end=186,
                end_offset=0,
                strand="+",
                gene_id="ENSG00000157404",
                gene_name="KIT",
                transcript_id="ENST00000288135",
                transcript_name="KIT-201",
            ),
            RnaPosition(
                contig_id="4",
                start=223,
                start_offset=0,
                end=225,
                end_offset=0,
                strand="+",
                gene_id="ENSG00000157404",
                gene_name="KIT",
                transcript_id="ENST00000412167",
                transcript_name="KIT-202",
            ),
            RnaPosition(
                contig_id="4",
                start=202,
                start_offset=0,
                end=204,
                end_offset=0,
                strand="+",
                gene_id="ENSG00000157404",
                gene_name="KIT",
                transcript_id="ENST00000514582",
                transcript_name="KIT-204",
            ),
        ],
    }


# -------------------------------------------------------------------------------------------------
# same_<position_type>
# -------------------------------------------------------------------------------------------------
def test_diff(ensembl100):
    assert ensembl100.diff("ENSP00000358548:p.Q61K", "NRAS:c.181C>A") == {
        "cdna": (
            [
                CdnaDelins(
                    refseq="CAA",
                    altseq="AAG",
                    contig_id="1",
                    start=181,
                    start_offset=0,
                    end=183,
                    end_offset=0,
                    strand="-",
                    gene_id="ENSG00000213281",
                    gene_name="NRAS",
                    transcript_id="ENST00000369535",
                    transcript_name="NRAS-201",
                    protein_id="ENSP00000358548",
                )
            ],
            [],
        ),
        "dna": (
            [
                DnaDelins(
                    refseq="CAA",
                    altseq="AAG",
                    contig_id="1",
                    start=114713907,
                    start_offset=0,
                    end=114713909,
                    end_offset=0,
                    strand="-",
                )
            ],
            [],
        ),
        "exon": ([], []),
        "protein": ([], []),
        "rna": (
            [
                RnaDelins(
                    refseq="CAA",
                    altseq="AAG",
                    contig_id="1",
                    start=312,
                    start_offset=0,
                    end=314,
                    end_offset=0,
                    strand="-",
                    gene_id="ENSG00000213281",
                    gene_name="NRAS",
                    transcript_id="ENST00000369535",
                    transcript_name="NRAS-201",
                )
            ],
            [],
        ),
    }


def test_same(ensembl100):
    assert ensembl100.same("ENSP00000358548:p.Q61K", "NRAS:c.181C>A") == {
        "cdna": [
            CdnaSubstitution(
                refseq="C",
                altseq="A",
                contig_id="1",
                start=181,
                start_offset=0,
                end=181,
                end_offset=0,
                strand="-",
                gene_id="ENSG00000213281",
                gene_name="NRAS",
                transcript_id="ENST00000369535",
                transcript_name="NRAS-201",
                protein_id="ENSP00000358548",
            )
        ],
        "dna": [
            DnaSubstitution(
                refseq="C",
                altseq="A",
                contig_id="1",
                start=114713909,
                start_offset=0,
                end=114713909,
                end_offset=0,
                strand="-",
            )
        ],
        "exon": [],
        "protein": [
            ProteinSubstitution(
                refseq="Q",
                altseq="K",
                contig_id="1",
                start=61,
                start_offset=0,
                end=61,
                end_offset=0,
                strand="-",
                gene_id="ENSG00000213281",
                gene_name="NRAS",
                transcript_id="ENST00000369535",
                transcript_name="NRAS-201",
                protein_id="ENSP00000358548",
            )
        ],
        "rna": [
            RnaSubstitution(
                refseq="C",
                altseq="A",
                contig_id="1",
                start=312,
                start_offset=0,
                end=312,
                end_offset=0,
                strand="-",
                gene_id="ENSG00000213281",
                gene_name="NRAS",
                transcript_id="ENST00000369535",
                transcript_name="NRAS-201",
            )
        ],
    }


def test_same_cdna(ensembl100):
    assert ensembl100.same_cdna("ENSP00000358548:p.Q61K", "NRAS:c.181C>A") == [
        CdnaSubstitution(
            refseq="C",
            altseq="A",
            contig_id="1",
            start=181,
            start_offset=0,
            end=181,
            end_offset=0,
            strand="-",
            gene_id="ENSG00000213281",
            gene_name="NRAS",
            transcript_id="ENST00000369535",
            transcript_name="NRAS-201",
            protein_id="ENSP00000358548",
        )
    ]


def test_same_dna(ensembl100):
    assert ensembl100.same_dna("ENSP00000358548:p.Q61K", "NRAS:c.181C>A") == [
        DnaSubstitution(
            refseq="C",
            altseq="A",
            contig_id="1",
            start=114713909,
            start_offset=0,
            end=114713909,
            end_offset=0,
            strand="-",
        )
    ]


def test_same_exon(ensembl100):
    assert ensembl100.same_exon("ENSP00000358548:p.61", "NRAS:c.181") == [
        ExonPosition(
            contig_id="1",
            start=3,
            start_offset=0,
            end=3,
            end_offset=0,
            strand="-",
            gene_id="ENSG00000213281",
            gene_name="NRAS",
            transcript_id="ENST00000369535",
            transcript_name="NRAS-201",
            exon_id="ENSE00001751295",
        )
    ]


def test_same_protein(ensembl100):
    assert ensembl100.same_protein("ENSP00000358548:p.Q61K", "NRAS:c.181C>A") == [
        ProteinSubstitution(
            refseq="Q",
            altseq="K",
            contig_id="1",
            start=61,
            start_offset=0,
            end=61,
            end_offset=0,
            strand="-",
            gene_id="ENSG00000213281",
            gene_name="NRAS",
            transcript_id="ENST00000369535",
            transcript_name="NRAS-201",
            protein_id="ENSP00000358548",
        )
    ]


def test_same_rna(ensembl100):
    assert ensembl100.same_rna("ENSP00000358548:p.Q61K", "NRAS:c.181C>A") == [
        RnaSubstitution(
            refseq="C",
            altseq="A",
            contig_id="1",
            start=312,
            start_offset=0,
            end=312,
            end_offset=0,
            strand="-",
            gene_id="ENSG00000213281",
            gene_name="NRAS",
            transcript_id="ENST00000369535",
            transcript_name="NRAS-201",
        )
    ]
