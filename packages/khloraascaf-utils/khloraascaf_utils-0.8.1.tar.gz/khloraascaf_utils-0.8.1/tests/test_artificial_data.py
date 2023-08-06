# -*- coding=utf-8 -*-

"""Test module for artificial data generation."""

# pylint: disable=missing-yield-doc, missing-param-doc, redefined-outer-name

from collections.abc import Iterator

import pytest
from revsymg.index_lib import FORWARD_INT, REVERSE_INT

from khloraascaf_utils.artificial_data import (
    ArtificialData,
    artificial_to_mdcg,
)


# ============================================================================ #
#                                    FIXTURE                                   #
# ============================================================================ #
@pytest.fixture()
def art_data_ir_sc() -> Iterator[ArtificialData]:
    """Artificial data for IR-UN perfect."""
    art_data = ArtificialData(
        (
            (0, FORWARD_INT),
            (1, FORWARD_INT),
            (2, FORWARD_INT),
            (1, REVERSE_INT),
        ),
        [4, 3, 2],
        proba_over_mult=0.0,
        proba_extra_link=0.0,
    )
    yield art_data


@pytest.fixture()
def art_data_ir_sc_over_extra() -> Iterator[ArtificialData]:
    """Artificial data for IR-UN with over mult and extra links."""
    art_data = ArtificialData(
        (
            (0, FORWARD_INT),
            (1, FORWARD_INT),
            (2, FORWARD_INT),
            (1, REVERSE_INT),
        ),
        [4, 3, 2],
        proba_over_mult=0.25,
        proba_extra_link=0.25,
    )
    yield art_data


# ============================================================================ #
#                                TEST FUNCTIONS                                #
# ============================================================================ #
# ---------------------------------------------------------------------------- #
#                                ArtificialData                                #
# ---------------------------------------------------------------------------- #
# REFACTOR extract unitary tests
# TOTEST extra_links
def test_art_data_ir_sc(art_data_ir_sc: ArtificialData):
    """Test artificial data fixture."""
    assert art_data_ir_sc.starter() == (0, FORWARD_INT)

    for c_ind, c_mult, c_presscore in art_data_ir_sc.contig_attrs():
        if c_ind < 4 or c_ind > 6:
            assert c_mult == 1
        elif 3 < c_ind < 7:
            assert c_mult == 2
        assert 0 <= c_presscore < 1

    for c_ind, c_mult, c_presscore in art_data_ir_sc.region_contigs(0):
        assert 0 <= c_ind < 4
        assert c_mult == 1
        assert 0 <= c_presscore < 1
    for c_ind, c_mult, c_presscore in art_data_ir_sc.region_contigs(1):
        assert 4 <= c_ind <= 6
        assert c_mult == 2
        assert 0 <= c_presscore < 1
    for c_ind, c_mult, c_presscore in art_data_ir_sc.region_contigs(2):
        assert 7 <= c_ind <= 8
        assert c_mult == 1
        assert 0 <= c_presscore < 1

    assert sum(1 for _ in art_data_ir_sc.links()) == 10
    assert not sum(1 for _ in art_data_ir_sc.extra_links())


# REFACTOR extract unitary tests
# TOTEST test region_contigs
def test_art_data_ir_sc_over_extra(art_data_ir_sc_over_extra: ArtificialData):
    """Test artificial data fixture."""
    assert art_data_ir_sc_over_extra.starter() == (0, FORWARD_INT)
    for c_ind, c_mult, c_presscore in art_data_ir_sc_over_extra.contig_attrs():
        if c_ind < 4 or c_ind > 6:
            assert 0 < c_mult < 3
        elif 3 < c_ind < 7:
            assert 1 < c_mult < 4
        assert 0 <= c_presscore < 1
    assert sum(1 for _ in art_data_ir_sc_over_extra.links()) >= 10
    assert sum(1 for _ in art_data_ir_sc_over_extra.extra_links()) >= 0


# ---------------------------------------------------------------------------- #
#                              Artificial_to_mdcg                              #
# ---------------------------------------------------------------------------- #
def test_art_to_mdcg(art_data_ir_sc: ArtificialData):
    """Test art to mdcg."""
    mdcg, starter = artificial_to_mdcg(art_data_ir_sc)
    assert starter == art_data_ir_sc.starter()
    assert mdcg.multiplied_card() == 12 * 2
    assert mdcg.repeated_contigs() == [4, 5, 6]
