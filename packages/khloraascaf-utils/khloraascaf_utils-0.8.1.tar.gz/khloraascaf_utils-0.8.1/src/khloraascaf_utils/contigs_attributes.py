# -*- coding=utf-8 -*-

"""Utility to compute contigs attributes."""

from decimal import Context, Decimal
from math import ceil, floor

from khloraascaf.inputs import MultT, PresScoreT


# ============================================================================ #
#                                     TYPES                                    #
# ============================================================================ #
LenT = int
"""Contig's length type."""

CovT = int
"""Coverage type."""

DisUnionAlignLenT = int
"""Disjoint union of alignment length type.

For a sequence :math:`s` of length :math:`|s|`, the disjoint union alignment
length is the number of nucleotides in :math:`s` covered by at least one
alignment of a sequence :math:`q` in a sequences set :math:`Q`.
Thus, the disjoint union alignment length can equals :math:`0` to :math:`|s|`.
"""

# ============================================================================ #
#                                   CONSTANTS                                  #
# ============================================================================ #
__DECIMAL_CONTEXT = Context(prec=3)


# ============================================================================ #
#                                   FUNCTIONS                                  #
# ============================================================================ #
def cov_to_mult(cov_contig: CovT, cov_unique: CovT) -> MultT:
    r"""Set multiplicity according to the given coverages.

    .. math::

        mult = max\left(1, \left\lceil \frac{c_{cov}}{s_{cov}} - 0.9 \right\rceil\right)

    Parameters
    ----------
    cov_contig : CovT
        Contig's coverage
    cov_unique : CovT
        Unique contig's coverage

    Returns
    -------
    MultT
        Contig's multiplicities

    Warnings
    --------
    Because of floating operation the result may vary a little.
    """  # noqa
    mult_contig = (
        __DECIMAL_CONTEXT.create_decimal_from_float(cov_contig)
        / __DECIMAL_CONTEXT.create_decimal_from_float(cov_unique)
    )
    fraction = mult_contig - int(mult_contig)
    if fraction > 0.1:
        return max(1, ceil(mult_contig))
    return max(1, floor(mult_contig))


def dis_union_align_len_to_presence_score(align_length: DisUnionAlignLenT,
                                          contig_length: LenT) -> PresScoreT:
    r"""Calculate the presence score of contig.

    .. math::

        c_{pres} = \frac{align\_length}{contig\_length}

    Parameters
    ----------
    align_length : DisUnionAlignLenT
        Disjoint union of alignement length over the contig
    contig_length : LenT
        Contig's length

    Returns
    -------
    PresScoreT
        Contig's presence score
    """
    return PresScoreT(align_length / contig_length)
