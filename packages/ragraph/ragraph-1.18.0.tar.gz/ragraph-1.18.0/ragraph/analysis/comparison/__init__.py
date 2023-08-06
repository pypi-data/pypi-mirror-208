"""
##########
Comparison
##########

Comparison provides classes for comparing :obj:`Graph <ragraph.graph.Graph` objects
to find the commonalities (sigma) and differences (delta).
"""
# flake8: noqa, ignore errors on unused imports here.

from ragraph.analysis.comparison._delta import DeltaAnalysis
from ragraph.analysis.comparison._sigma import SigmaAnalysis
from ragraph.analysis.comparison.utils import (
    check_edge_equality,
    get_common_leafs,
    get_unique_edges,
    get_unique_leafs,
)
