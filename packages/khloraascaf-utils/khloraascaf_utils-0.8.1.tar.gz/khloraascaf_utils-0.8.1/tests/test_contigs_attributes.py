# -*- coding=utf-8 -*-

"""Tests for contigs attributes functions."""

from decimal import Decimal

from khloraascaf_utils.contigs_attributes import (
    cov_to_mult,
    dis_union_align_len_to_presence_score,
)


# ============================================================================ #
#                                TEST FUNCTIONS                                #
# ============================================================================ #
# ---------------------------------------------------------------------------- #
#                                  Cov_to_mult                                 #
# ---------------------------------------------------------------------------- #
def test_cov_to_mult_ceil():
    """Test cov_to_mult function for the ceil branch."""
    assert cov_to_mult(111, 100) == 2
    assert cov_to_mult(1111, 100) == 11
    assert cov_to_mult(3, 2) == 2
    assert cov_to_mult(11, 10) == 1


def test_cov_to_mult_floor():
    """Test cov_to_mult function for the floor branch."""
    assert cov_to_mult(1.09, 1) == 1
    assert cov_to_mult(2.06, 2) == 1


def test_cov_to_mult_inf_to_one():
    """Test cov_to_mult function when contig cov is the fewest."""
    assert cov_to_mult(0.5, 1) == 1


# ---------------------------------------------------------------------------- #
#                     Dis_union_align_len_to_presence_score                    #
# ---------------------------------------------------------------------------- #
def test_align_len_presence_score():
    """Test compute presence score from alignment length."""
    assert dis_union_align_len_to_presence_score(1, 1) == 1.0
    assert dis_union_align_len_to_presence_score(1, 2) == 0.5
    # pylint: disable=compare-to-zero
    assert dis_union_align_len_to_presence_score(0, 2) == 0.0
