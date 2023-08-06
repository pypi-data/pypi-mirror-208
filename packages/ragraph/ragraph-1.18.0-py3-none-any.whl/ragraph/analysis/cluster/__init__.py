"""
#####################
Clustering algorithms
#####################

Clustering algorithms detect (nested) clusters of nodes in graphs that are relatively
tightly connected by means of their edges. Both hierarchical and flat clustering
algorithms are provided.

Apart of algorithm specific parameters, all of them feature the same basic parameters:

* ``graph``: Graph to cluster containing the relevant nodes and edges.
* ``leafs``: Optional list of leaf nodes to cluster. If not provided all the graph's
  leaf nodes are selected.
* ``inplace``: Boolean toggle whether to create the new cluster nodes in the provided
  graph or provided a deepcopy of the graph with only the leaf nodes, their edges and
  newly created cluster nodes.

********************
Available algorithms
********************

The following algorithms are directly accessible after importing
:obj:`ragraph.analysis.cluster`:

* :func:`markov() <ragraph.analysis.cluster.markov.markov_clustering>`: Markov
  Clustering (Flat) algorithm.
* :func:`hierarchical_markov()
  <ragraph.analysis.cluster.markov.hierarchical_markov_clustering>`: Hierarchical Markov
  Clustering algorithm.
* :func:`tarjans_scc() <ragraph.analysis.cluster.tarjan.tarjans_scc_clustering>`:
  Tarjan's Strongly Connected Components algorithm.
"""
# flake8: noqa, ignore errors on unused imports here.

from ragraph.analysis.cluster._markov import (
    hierarchical_markov_clustering as hierarchical_markov,
)
from ragraph.analysis.cluster._markov import markov_clustering as markov
from ragraph.analysis.cluster._tarjan import tarjans_scc_clustering as tarjans_scc
