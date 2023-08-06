# -*- coding=utf-8 -*-

"""Module to produce FASTA sequences from assembly graph."""

from pathlib import Path

from Bio import Seq, SeqIO
from khloraascaf.assembly_graph import AssemblyGraph, rev_oriented_contig
from khloraascaf.inputs import IdCT, IdLT, read_contig_links_file
from khloraascaf.outputs import OrCT
from revsymg.index_lib import FORWARD_INT, IndexT, IndOrT, OrT


# TODO subcommand cli from files to sequences

# ============================================================================ #
#                                     CLASS                                    #
# ============================================================================ #
class SequenceGraph():
    """Assembly graph enriched with region sequences.

    Warnings
    --------
    #XXX FASTA format header
    All FASTA file format must respect the following format:
    ```
    >SEQ1_ID
    ACGT
    >SEQ2_ID
    AGTC
    ```
    """

    def __init__(self, asm_graph: AssemblyGraph, contig_sequences_file: Path,
                 contig_links_file: Path, link_sequences_file: Path):
        """The Initialiser."""
        #
        # Canonical couple of oriented contig for each link id (forward)
        #
        self.__orc_link_to_id: dict[tuple[OrCT, OrCT], IdLT] = {}
        #
        # Sequence for each forward link identifier
        # OPTIMIZE stop keeping in hard memory: index method?
        self.__link_sequences: dict[IdLT, Seq.Seq] = {}

        for link_id, c_id, c_or, d_id, d_or in read_contig_links_file(
                contig_links_file):
            self.__orc_link_to_id[(c_id, c_or), (d_id, d_or)] = link_id
            self.__link_sequences[link_id] = Seq.Seq('')

        for record in SeqIO.parse(link_sequences_file, 'fasta'):
            if record.id not in self.__link_sequences:
                raise KeyError(record.id)
            self.__link_sequences[record.id] = record.seq
        #
        # Sequence for each forward region
        #
        # OPTIMIZE stop keeping in hard memory: index method?
        self.__region_sequences: list[Seq.Seq] = []
        #
        # For each region (forward) gives its oriented contig extremities
        #
        self.__region_orc_extrem: list[tuple[OrCT, OrCT]] = []

        self.__build_region_sequences(asm_graph, contig_sequences_file)

    def region_sequence(self, region_ind: IndexT,
                        region_or: OrT = FORWARD_INT) -> Seq.Seq:
        """Return the sequence of the given region.

        Parameters
        ----------
        region_ind : IndexT
            Region's index
        region_or : OrT, optional
            Region's orientation, by default `FORWARD_INT`

        Returns
        -------
        Seq.Seq
            Sequence of the oriented region
        """
        return (
            self.__region_sequences[region_ind] if region_or == FORWARD_INT
            else self.__region_sequences[region_ind].reverse_complement()
        )

    def region_path_to_seq(self, region_path: list[IndOrT]) -> Seq.Seq:
        """Generate the sequence corresponding to the region path.

        Parameters
        ----------
        region_path : list IndOrT
            Oriented region path

        Returns
        -------
        Seq.Seq
            Nucletotide sequence
        """
        region_path_iter = iter(region_path)
        u_ind, u_or = next(region_path_iter)
        begin_ind, begin_or = u_ind, u_or

        path_sequence: Seq.Seq = self.region_sequence(u_ind, u_or)

        for v_ind, v_or in region_path_iter:
            # Add link sequence
            u_ext: OrCT = (
                self.__region_orc_extrem[u_ind][1] if u_or == FORWARD_INT
                else rev_oriented_contig(self.__region_orc_extrem[u_ind][0])
            )
            v_ext: OrCT = (
                self.__region_orc_extrem[v_ind][0] if v_or == FORWARD_INT
                else rev_oriented_contig(self.__region_orc_extrem[v_ind][1])
            )
            path_sequence = (
                path_sequence
                + self.__get_oriented_link_sequence(u_ext, v_ext)
                + self.region_sequence(v_ind, v_or)
            )
            u_ind, u_or = v_ind, v_or
        # Add last link
        u_ext = (
            self.__region_orc_extrem[u_ind][1] if u_or == FORWARD_INT
            else rev_oriented_contig(self.__region_orc_extrem[u_ind][0])
        )
        begin_ext: OrCT = (
            self.__region_orc_extrem[begin_ind][0] if begin_or == FORWARD_INT
            else rev_oriented_contig(self.__region_orc_extrem[begin_ind][1])
        )
        return (
            path_sequence
            + self.__get_oriented_link_sequence(u_ext, begin_ext)
        )

    # ~*~ Private ~*~

    def __build_region_sequences(self, asm_graph: AssemblyGraph,
                                 contig_sequences_file: Path):
        """Give for each region its sequence and its orcontigs extremities.

        Parameters
        ----------
        asm_graph : AssemblyGraph
            Assembly graph
        contig_sequences_file : Path
            File containing contig sequences
        """
        contig_sequences: dict[IdCT, Seq.Seq] = {
            record.id: record.seq
            for record in SeqIO.parse(contig_sequences_file, 'fasta')
        }
        for reg_ind in range(asm_graph.revsymg().vertices().card_index()):
            region_orcs_iter = iter(
                asm_graph.oriented_contigs_of_region(reg_ind),
            )
            u_id, u_or = next(region_orcs_iter)
            begin_ext = u_id, u_or
            self.__region_sequences.append(
                contig_sequences[u_id] if u_or == FORWARD_INT
                else contig_sequences[u_id].reverse_complement(),
            )
            for v_id, v_or in region_orcs_iter:
                self.__region_sequences[reg_ind] = (
                    self.__region_sequences[reg_ind]
                    + self.__get_oriented_link_sequence(
                        (u_id, u_or), (v_id, v_or),
                    )
                    + (
                        contig_sequences[v_id] if v_or == FORWARD_INT
                        else contig_sequences[v_id].reverse_complement()
                    )
                )
                u_id, u_or = v_id, v_or
            self.__region_orc_extrem.append((begin_ext, (u_id, u_or)))

    def __get_oriented_link_sequence(self, u: OrCT, v: OrCT) -> Seq.Seq:
        """Return oriented sequence from couple of oriented contigs.

        Parameters
        ----------
        u : OrCT
            Oriented contig
        v : OrCT
            Oriented contig

        Returns
        -------
        Seq.Seq
            Oriented link sequence

        Raises
        ------
        KeyError
            There is no link for the couple of oriented contigs
        """
        if (u, v) in self.__orc_link_to_id:
            return self.__link_sequences[
                self.__orc_link_to_id[u, v]
            ]
        rev_u, rev_v = rev_oriented_contig(u), rev_oriented_contig(v)
        if (rev_v, rev_u) in self.__orc_link_to_id:
            return self.__link_sequences[
                self.__orc_link_to_id[rev_v, rev_u]
            ].reverse_complement()
        # REFACTOR exception NoLink
        raise KeyError((u, v))
