"""
#####################
Sequencing algorithms
#####################

Sequencing algorithms search for sequences of nodes according to some objective or
logic. Simple are sorting by name and more elaborate examples sort according to Markov
transisition probabilities or sequences without feedback (edges to earlier nodes).

There are several metrics from literature available to grade sequences as well. The
metrics are documented over at :obj:`metrics`.

Finally, there are some utilities like branch-sorting (recursively sorting all branches
in a hierarchical tree instead of all leaf nodes as a whole) available in :obj:`utils`.

********************
Available algorithms
********************

The following algorithms are directly accessible after importing
:obj:`ragraph.analysis.sequence`:

* :func:`markov() <ragraph.analysis.sequence.markov.markov_sequencing>`: Markov
  sequencing based on relative node dependency and influence.
* :func:`name() <ragraph.analysis.sequence.name.name>`: Sequence nodes by node name.
* :func:`tarjans_dfs() <ragraph.analysis.sequence.tarjan.tarjans_dfs>`: Sequence nodes
  according to Tarjan's Depth First Search algorithm. Sequence a Directed Acyclic Graphs
  (DAG) into a sequence without feedback edges to earlier nodes.
"""
# flake8: noqa, ignore errors on unused imports here.

from ragraph.analysis.sequence import metrics, utils
from ragraph.analysis.sequence._axis import axis_sequencing as axis
from ragraph.analysis.sequence._markov import markov_sequencing as markov
from ragraph.analysis.sequence._name import sort_by_name as name
from ragraph.analysis.sequence._scc_tearing import scc_tearing
from ragraph.analysis.sequence._tarjan import tarjans_dfs_sequencing as tarjans_dfs
from ragraph.analysis.sequence.utils import branchsort
