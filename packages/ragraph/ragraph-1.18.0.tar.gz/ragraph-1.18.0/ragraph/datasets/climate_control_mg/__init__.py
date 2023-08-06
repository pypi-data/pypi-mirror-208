"""Ford climate control system clustered using the Markov-Gamma clustering and bus
detection heuristic.

Reference: Pimmler, T. U., & Eppinger, S. D. (1994). Integration Analysis of Product
Decompositions. ASME Design Theory and Methodology Conference.
"""


edge_weights = [
    "adjacency",
    "spatial",
    "energy flow",
    "information flow",
    "material flow",
]
