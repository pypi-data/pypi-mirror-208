# -*- coding=utf-8 -*-

"""Tests for SequenceGraph class."""

from pathlib import Path

from Bio import SeqIO
from khloraascaf.assembly_graph import AssemblyGraph

from khloraascaf_utils.asm_graph_to_fasta import SequenceGraph


# ============================================================================ #
#                                   CONSTANTS                                  #
# ============================================================================ #
TEST_DIR: Path = Path(__file__).parent.absolute()

_DATA_DIR = TEST_DIR / 'data'

# ---------------------------------------------------------------------------- #
#                                    IR - UN                                   #
# ---------------------------------------------------------------------------- #
_IR_SC_DIR = _DATA_DIR / 'ir_sc'
_IR_SC_CONTIG_LINKS = _IR_SC_DIR / 'contig_links.tsv'
_IR_SC_CONTIGS_FASTA = _IR_SC_DIR / 'contigs.fasta'
_IR_SC_LINKS_FASTA = _IR_SC_DIR / 'links.fasta'
_IR_SC_SOL_REGMAP = _IR_SC_DIR / 'map_of_regions_sol.tsv'
_IR_SC_SOL_REGCTG_F = _IR_SC_DIR / 'contigs_of_regions_sol_0.tsv'
_IR_SC_FASTA_SOL = _IR_SC_DIR / 'asm_graph_paths.fasta'

# ---------------------------------------------------------------------------- #
#                                    DR - UN                                   #
# ---------------------------------------------------------------------------- #
_DR_SC_DIR = _DATA_DIR / 'dr_sc'
_DR_SC_CONTIG_LINKS = _DR_SC_DIR / 'contig_links.tsv'
_DR_SC_CONTIGS_FASTA = _DR_SC_DIR / 'contigs.fasta'
_DR_SC_LINKS_FASTA = _DR_SC_DIR / 'links.fasta'
_DR_SC_SOL_REGMAP = _DR_SC_DIR / 'map_of_regions_sol.tsv'
_DR_SC_SOL_REGCTG = _DR_SC_DIR / 'contigs_of_regions_sol_0.tsv'
_DR_SC_FASTA_SOL = _DR_SC_DIR / 'asm_graph_paths.fasta'


# ============================================================================ #
#                                   FUNCTIONS                                  #
# ============================================================================ #
# ---------------------------------------------------------------------------- #
#                                    IR - UN                                   #
# ---------------------------------------------------------------------------- #
def test_ir_sc_fasta():
    """Test for IR-UN FASTA."""
    asm_graph = AssemblyGraph(_IR_SC_SOL_REGMAP, _IR_SC_SOL_REGCTG_F)
    seq_graph = SequenceGraph(
        asm_graph, _IR_SC_CONTIGS_FASTA,
        _IR_SC_CONTIG_LINKS, _IR_SC_LINKS_FASTA,
    )
    seq_sol = {
        str(record.seq)
        for record in SeqIO.parse(_IR_SC_FASTA_SOL, 'fasta')
    }
    for region_path in asm_graph.all_region_paths():
        print(seq_graph.region_path_to_seq(region_path))
        assert str(seq_graph.region_path_to_seq(region_path)) in seq_sol


# ---------------------------------------------------------------------------- #
#                                    DR - UN                                   #
# ---------------------------------------------------------------------------- #
def test_dr_sc_fasta():
    """Test for DR-UN FASTA."""
    asm_graph = AssemblyGraph(_DR_SC_SOL_REGMAP, _DR_SC_SOL_REGCTG)
    seq_graph = SequenceGraph(
        asm_graph, _DR_SC_CONTIGS_FASTA,
        _DR_SC_CONTIG_LINKS, _DR_SC_LINKS_FASTA,
    )
    seq_sol = {
        str(record.seq)
        for record in SeqIO.parse(_DR_SC_FASTA_SOL, 'fasta')
    }
    for region_path in asm_graph.all_region_paths():
        print(seq_graph.region_path_to_seq(region_path))
        assert str(seq_graph.region_path_to_seq(region_path)) in seq_sol
