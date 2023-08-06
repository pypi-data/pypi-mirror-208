# -*- coding=utf-8 -*-

"""Data generation module."""

from collections.abc import Iterable, Iterator
from random import randint, random

from khloraascaf.inputs import MultT, PresScoreT
from khloraascaf.multiplied_doubled_contig_graph import (
    MULT_ATTR,
    PRESSCORE_ATTR,
    MDCGraph,
)
from revsymg.graphs import RevSymGraph
from revsymg.index_lib import (
    FORWARD_INT,
    REVERSE_INT,
    IndexT,
    IndOrT,
    OrT,
    rev_vertex,
)


# DOCU all artificial data module
# ============================================================================ #
#                                     CLASS                                    #
# ============================================================================ #
class ArtificialData(RevSymGraph):
    """Artificial data class.

    Warnings
    --------
    Please, let the first region be a unique one.
    Thus, the starter will be the very first contig of this region.
    """

    def __init__(self, oriented_region_order: Iterable[IndOrT],
                 region_length: list[int],
                 proba_over_mult: float = 0.0,
                 proba_extra_link: float = 0.0):
        """The Initialiser."""
        super().__init__()
        #
        # New attributes
        #
        self._vertices.new_attr(MULT_ATTR, 1)
        self._vertices.new_attr(PRESSCORE_ATTR, 0.0)
        #
        # Regions and their oriented contigs
        #
        self.__oriented_region_order: tuple[IndOrT, ...] = tuple(
            oriented_region_order,
        )
        self.__region_oriented_contig: list[list[IndOrT]] = []
        #
        # Noise probabilities
        #
        self.__proba_over_mult: float = proba_over_mult
        self.__proba_extra_link: float = proba_extra_link
        #
        # Separate noise from perfect data
        #
        self.__base_links: list[tuple[IndOrT, IndOrT]] = []
        self.__extra_links: list[tuple[IndOrT, IndOrT]] = []
        #
        # Build artificial data
        #
        self.__generate_region_orc(region_length)
        self.__generate_intra_links()
        self.__generate_inter_links()
        self.__generate_extra_links()

    # ~*~ Getter ~*~

    def starter(self) -> IndOrT:
        """The starter.

        Returns
        -------
        IndOrT
            Oriented contig
        """
        return 0, FORWARD_INT

    def contig_attrs(self) -> Iterator[tuple[IndexT, MultT, PresScoreT]]:
        """Iterate over the contigs and their attributes.

        Yields
        ------
        IndexT
            Contig's index
        MultT
            Contig's multiplicity
        PresScoreT
            Contig's presence score
        """
        for c_ind in range(self._vertices.card_index()):
            yield (
                c_ind,
                self._vertices.attr(c_ind, MULT_ATTR),
                self._vertices.attr(c_ind, PRESSCORE_ATTR),
            )

    def links(self) -> Iterator[tuple[IndexT, IndOrT, IndOrT]]:
        """Iterate over the links.

        Yields
        ------
        IndexT
            Link's index
        IndOrT
            First oriented contig
        IndOrT
            Second oriented contig
        """
        for l_ind, (u, v) in enumerate(self.__base_links):
            yield l_ind, u, v
        for l_ind, (u, v) in enumerate(self.__extra_links):
            yield l_ind + len(self.__base_links), u, v

    def extra_links(self) -> Iterator[tuple[IndexT, IndOrT, IndOrT]]:
        """Iterate over the links.

        Yields
        ------
        IndexT
            Link's index
        IndOrT
            First oriented contig
        IndOrT
            Second oriented contig
        """
        for l_ind, (u, v) in enumerate(self.__extra_links):
            yield l_ind + len(self.__base_links), u, v

    def region_contigs(self, region_ind: IndexT) -> (
            Iterator[tuple[IndexT, MultT, PresScoreT]]):
        """Iterate over the contigs and their attributes of a region.

        Parameters
        ----------
        region_ind : IndexT
            Index of the region

        Yields
        ------
        IndexT
            Contig's index
        MultT
            Contig's multiplicity
        PresScoreT
            Contig's presence score
        """
        for c_ind, _ in self.__region_oriented_contig[region_ind]:
            yield (
                c_ind,
                self._vertices.attr(c_ind, MULT_ATTR),
                self._vertices.attr(c_ind, PRESSCORE_ATTR),
            )

    # ~*~ Regions ~*~

    def __generate_region_orc(self, region_length: list[int]):
        for reg_ind, _ in self.__oriented_region_order:
            if reg_ind == len(self.__region_oriented_contig):
                # Generate the region
                self.__region_oriented_contig.append([])
                for c_ind in range(region_length[reg_ind]):
                    v_ind = self._vertices.add()
                    self._vertices.set_attr(
                        v_ind, MULT_ATTR,
                        (
                            self.__generate_mult()
                            if reg_ind > 0 or c_ind > 0
                            else 1
                        ),
                    )
                    self._vertices.set_attr(
                        v_ind, PRESSCORE_ATTR,
                        self.__generate_presencescore(),
                    )

                    self.__region_oriented_contig[-1].append(
                        (  # type: ignore
                            v_ind,  # new contig index
                            (
                                # new contig orientation
                                randint(FORWARD_INT, REVERSE_INT)
                                if reg_ind > 0 or c_ind > 0
                                else FORWARD_INT
                            ),
                        ),
                    )
            else:
                # Add one to the multiplicities of each contig
                for c_ind, _ in self.__region_oriented_contig[reg_ind]:
                    self._vertices.set_attr(
                        c_ind, MULT_ATTR,
                        self._vertices.attr(c_ind, MULT_ATTR) + 1,
                    )

    # ~*~ Contigs ~*~

    def __generate_mult(self, base: int = 1) -> int:
        mult = base
        if random() < self.__proba_over_mult:
            mult += 1
        return mult

    def __generate_presencescore(self) -> float:
        return random()

    # ~*~ Links ~*~

    def __generate_intra_links(self):
        for region_orc in self.__region_oriented_contig:
            orc_iter = iter(region_orc)
            u = next(orc_iter)
            for v in orc_iter:
                self._edges.add(u, v)
                self.__base_links.append((u, v))
                u = v

    def __generate_inter_links(self):
        orreg_map_iter = iter(self.__oriented_region_order)
        start = next(orreg_map_iter)
        u = start
        start_beg, u_end = self.__orreg_extremity(*u)
        for v in orreg_map_iter:
            v_beg, v_end = self.__orreg_extremity(*v)
            self._edges.add(u, v)
            self.__base_links.append((u_end, v_beg))
            u = v
            u_end = v_end
        self._edges.add(u, start)
        self.__base_links.append((u_end, start_beg))

    def __generate_extra_links(self):
        for c_ind in range(self._vertices.card_index()):
            if random() < self.__proba_extra_link:
                c_or: OrT = randint(
                    FORWARD_INT,
                    REVERSE_INT,
                )  # type: ignore
                d_ind = randint(0, self._vertices.card_index() - 1)
                d_or: OrT = randint(
                    FORWARD_INT,
                    REVERSE_INT,
                )  # type: ignore
                if ((c_ind, c_or), (d_ind, d_or)) not in self._edges:
                    self._edges.add((c_ind, c_or), (d_ind, d_or))
                    self.__extra_links.append(
                        ((c_ind, c_or), (d_ind, d_or)),
                    )

    def __orreg_extremity(self, reg_ind: IndexT,
                          reg_or: OrT) -> tuple[IndOrT, IndOrT]:
        if reg_or == FORWARD_INT:
            return (
                self.__region_oriented_contig[reg_ind][0],
                self.__region_oriented_contig[reg_ind][-1],
            )
        return (
            rev_vertex(self.__region_oriented_contig[reg_ind][-1]),
            rev_vertex(self.__region_oriented_contig[reg_ind][0]),
        )


# ============================================================================ #
#                                   FUNCTIONS                                  #
# ============================================================================ #
def artificial_to_mdcg(artificial_data: ArtificialData) -> (
        tuple[MDCGraph, IndOrT]):
    """Create a multiplied doubled contig graph from artificial data.

    Parameters
    ----------
    artificial_data : ArtificialData
        Artificial data

    Returns
    -------
    MDCGraph
        Multiplied doubled contig graph
    IndOrT
        Starter in the multiplied doubled contig graph
    """
    mdcg = MDCGraph()
    for c_ind, c_mult, c_presscore in artificial_data.contig_attrs():
        assert c_ind == mdcg.add_multiplied_vertex(c_mult, c_presscore)
    for l_ind, u, v in artificial_data.links():
        assert l_ind == mdcg.edges().add(u, v)
    return mdcg, artificial_data.starter()
