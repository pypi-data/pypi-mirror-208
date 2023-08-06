"""
##########
Heuristics
##########

Heuristics are combinations of algorithms available in the other subpackages or have an
output that does not strictly fit one of the other categories. Not all heuristics have a
common argument structure because of their more diverse nature.

********************
Available heuristics
********************

The following heuristics are directly available after importing
:obj:`ragraph.analysis.heuristics`:

* :func:`johnson() <ragraph.analysis.heuristics.johnson.circuit_finding_algorithm>`:
  Johnson's circuit finding algorithm. Generates all cycles in a graph, including
  overlapping and nested cycles.
* :func:`markov_gamma()
  <ragraph.analysis.heuristics.markov_gamma.markov_gamma_clustering>`: Combination of
  :obj:`Gamma bus detection <ragraph.analysis.bus.gamma.gamma_bus_detection>` and
  :obj:`(Hierarchical) Markov Clustering <ragraph.analysis.cluster.markov>`. Detects a
  tree structure with buses on global or local levels.
"""
# flake8: noqa, ignore errors on unused imports here.

from ragraph.analysis.heuristics._johnson import circuit_finding_algorithm as johnson
from ragraph.analysis.heuristics._markov_gamma import (
    markov_gamma_clustering as markov_gamma,
)
