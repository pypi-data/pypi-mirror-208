# pyvariant

## What is it?

**pyvariant** is a Python package for mapping biological sequence variants (mutations) to their equivalent chromosome, cDNA, gene, exon, protein, and RNA positions.

## How to get it

The easiest way to get pyvariant is using [pip](https://pip.pypa.io/en/latest/quickstart.html):

```sh
pip install pyvariant
```

The source code is hosted on GitHub at: <https://github.com/mattdoug604/pyvariant>

## How to use it

Before you can use pyvariant, you will need to download the necessary genomic data.

To download and install data from Ensembl, run:

```shell
pyvariant install --species <species-name> --release <Ensembl-release-number>
```

For example:

```shell
pyvariant install --species 'homo sapiens' --release 100
```

At the time of writing, installing a human dataset takes roughly 30-45 minutes and 1.5G of storage space. However, the actual time and space required to install a dataset will depend entirely on the size of the dataset, your computer, internet speed, etc.

By default, the data is downloaded to a [platform-specific data directory](https://pypi.org/project/appdirs/) that is generally only accessible by the user (e.g. `/home/<you>/.local/share/pyvariant/`). If you want the data to be accessible to other users, or your home directory does have enough storage space, you may to specify a different directory to download to with the `--cache` option:

```shell
pyvariant install --species homo_sapiens --release 100 --cache /path/to/cache/
```

For more options, run:

```shell
pyvariant install --help
```

Alternatively, you can run the installation from inside a Python process:

```python
>>> from pyvariant import EnsemblRelease
>>> ensembl100 = EnsemblRelease(species='homo_sapiens', release=100, cache_dir="/path/to/cache/")
>>> ensembl100.install()
```

Once the data is installed, the `EnsemblRelease` object provides methods for getting information about different features, getting the DNA/RNA/protein sequence at a position, and converting between positions, etc.

### Map between feature types

The main use of the package is for converting between equivalent cDNA, DNA, exon, protein, and RNA positions. For example:

cDNA to DNA:

```python
>>> ensembl100.to_dna("ENST00000310581:c.-124C>T")
[DnaSubstitution(refseq='C', altseq='T', contig_id='5', start=1295113, start_offset=0, end=1295113, end_offset=0, strand='-')]
```

Protein to DNA:

```python
>>> ensembl100.to_dna("BRCA1:p.Q1458*")
[DnaDelins(refseq='CAG', altseq='TAA', contig_id='17', start=43076598, start_offset=0, end=43076600, end_offset=0, strand='-'), DnaDelins(refseq='CAG', altseq='TGA', contig_id='17', start=43076598, start_offset=0, end=43076600, end_offset=0, strand='-'), DnaSubstitution(refseq='C', altseq='T', contig_id='17', start=43076600, start_offset=0, end=43076600, end_offset=0, strand='-')]
```

Exon to RNA:

```python
>>> ensembl100.to_rna("ENST00000266970:e.7::ENST00000360299:e.2")
[RnaFusion(breakpoint1=RnaPosition(contig_id='12', start=972, start_offset=0, end=2240, end_offset=0, strand='+', gene_id='ENSG00000123374', gene_name='CDK2', transcript_id='ENST00000266970', transcript_name='CDK2-201'), breakpoint2=RnaPosition(contig_id='12', start=63, start_offset=0, end=317, end_offset=0, strand='+', gene_id='ENSG00000111540', gene_name='RAB5B', transcript_id='ENST00000360299', transcript_name='RAB5B-201'))]
```

You can also limit mapping to the canonical transcript only:

```python
>>> ensembl100 = EnsemblRelease(species='homo_sapiens', release=100, canonical_transcript=["ENST00000000233"])
>>> ensembl100.to_cdna("7:g.127589084", canonical=False)
[CdnaPosition(contig_id='7', start=69, start_offset=0, end=69, end_offset=0, strand='+', gene_id='ENSG00000004059', gene_name='ARF5', transcript_id='ENST00000000233', transcript_name='ARF5-201', protein_id='ENSP00000000233'), CdnaPosition(contig_id='7', start=69, start_offset=0, end=69, end_offset=0, strand='+', gene_id='ENSG00000004059', gene_name='ARF5', transcript_id='ENST00000415666', transcript_name='ARF5-202', protein_id='ENSP00000412701')]
>>> ensembl100.to_cdna("7:g.127589084", canonical=True)
[CdnaPosition(contig_id='7', start=69, start_offset=0, end=69, end_offset=0, strand='+', gene_id='ENSG00000004059', gene_name='ARF5', transcript_id='ENST00000000233', transcript_name='ARF5-201', protein_id='ENSP00000000233')]
```

### Check if two variants are equivalent

Get the notation(s) that represent both variants:

```python
>>> x = ensembl100.same("ENSP00000358548:p.Q61K", "NRAS:c.181C>A")
>>> x.keys()
dict_keys(['cdna', 'dna', 'exon', 'protein', 'rna'])
>>> x["dna"]
[DnaSubstitution(refseq='C', altseq='A', contig_id='1', start=114713909, start_offset=0, end=114713909, end_offset=0, strand='-')]
```

...or get the notation(s) that are unique to each variant:

```python
>>> x = ensembl100.diff("ENSP00000358548:p.Q61K", "NRAS:c.181C>A")
>>> x.keys()
dict_keys(['cdna', 'dna', 'exon', 'protein', 'rna'])
>>> x["dna"]
([DnaDelins(refseq='CAA', altseq='AAG', contig_id='1', start=114713907, start_offset=0, end=114713909, end_offset=0, strand='-')], [])
```

### Fetch sequences

Get the mutated reference sequence, within a given window:

```python
>>> ensembl100.sequence("ENST00000635293:c.1044A>C", window=50)
CGCCTCTTTCAGAGACTTTTAACTTCAACATCTGTCCCTACCCAGCAGGC
```

The sequence can also be normalized to a specific strand of the genome:

```python
>>> ensembl100.sequence("ENST00000635293:c.1044A>C", window=50, strand='+')
GCCTGCTGGGTAGGGACAGATGTTGAAGTTAAAAGTCTCTGAAAGAGGCG
```

Get the sequence surrounding a fusion breakpoint:

```python
>>> ensembl100.sequence("ENST00000399410:r.2871::ENST00000561813:r.317", window=50)
ACAGTGCAGGGAAGCAACTGCAGAGGCTGTGCAATCTTGCACAAATATCT
```

### Retrieve feature information

`pyvariant` also has functions for retrieving general information about various features. For example:

Get a list of transcript IDs for a gene:

```python
>>> ensembl100.transcript_ids("BRCA2")
['ENST00000380152', 'ENST00000470094', 'ENST00000528762', 'ENST00000530893', 'ENST00000533776', 'ENST00000544455', 'ENST00000614259', 'ENST00000665585', 'ENST00000666593', 'ENST00000670614', 'ENST00000671466']
```

For a complete list of methods, run:

```python
>>> help(EnsemblRelease)
```

## Variant naming standards

This package follows [HGVS nomenclature](https://varnomen.hgvs.org/) recommendations for representing variants.

### Offset positions

When describing variants in an intron or UTR, it can be more informative to describe the position relative to a transcript, rather than the genome. These positions are described with a "+" or "-". For example, "TERT:c.-125" means "a position 125 nucleotides 5’ of the ATG translation initiation codon." See the [HGVS nomenclature](https://varnomen.hgvs.org/bg-material/numbering/) documentation for more information.

## License

This package is distributed with the [MIT](LICENSE) license.
