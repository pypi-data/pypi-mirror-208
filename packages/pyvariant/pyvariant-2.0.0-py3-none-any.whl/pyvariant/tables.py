"""Nucleotide and amino acid codon tables."""
# IUPAC nucleotide codes
DNA = {
    "A": ["A"],
    "C": ["C"],
    "G": ["G"],
    "T": ["T"],
    "R": ["A", "G"],
    "Y": ["C", "T"],
    "S": ["C", "G"],
    "W": ["A", "T"],
    "K": ["G", "T"],
    "M": ["A", "C"],
    "B": ["C", "G", "T"],
    "D": ["A", "G", "T"],
    "H": ["A", "C", "T"],
    "V": ["A", "C", "G"],
    "N": ["A", "C", "G", "T"],
}

# single-letter amino acid to all possible codons
# NOTE: these are only the mammalian (non-mitochondrial) codons!
DNA_CODON_TABLE = {
    "A": ["GCA", "GCC", "GCG", "GCT"],
    "C": ["TGC", "TGT"],
    "D": ["GAC", "GAT"],
    "E": ["GAA", "GAG"],
    "F": ["TTC", "TTT"],
    "G": ["GGA", "GGC", "GGG", "GGT"],
    "H": ["CAC", "CAT"],
    "I": ["ATA", "ATC", "ATT"],
    "K": ["AAA", "AAG"],
    "L": ["CTA", "CTC", "CTG", "CTT", "TTA", "TTG"],
    "M": ["ATG"],
    "N": ["AAC", "AAT"],
    "P": ["CCA", "CCC", "CCG", "CCT"],
    "Q": ["CAA", "CAG"],
    "R": ["AGA", "AGG", "CGA", "CGC", "CGG", "CGT"],
    "S": ["AGC", "AGT", "TCA", "TCC", "TCG", "TCT"],
    "T": ["ACA", "ACC", "ACG", "ACT"],
    "V": ["GTA", "GTC", "GTG", "GTT"],
    "W": ["TGG"],
    "Y": ["TAC", "TAT"],
    "*": ["TAA", "TAG", "TGA"],
}

# codon to single-letter amino acid
AMINO_ACID_TABLE = {
    codon: amino_acid
    for amino_acid, codons in DNA_CODON_TABLE.items()
    if amino_acid != "X"
    for codon in codons
}

# IUPAC single-letter amino acid codes
_PROTEIN = "ARNDCQEGHILKMFPSTWYV*"
PROTEIN = {
    "B": ["D", "N"],
    "Z": ["E", "Q"],
    "X": [aa for aa in _PROTEIN if aa != "*"],
    **{aa: [aa] for aa in _PROTEIN},
}
