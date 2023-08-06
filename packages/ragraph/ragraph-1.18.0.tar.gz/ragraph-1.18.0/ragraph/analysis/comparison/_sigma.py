"""Sigma analysis module. """

from collections import defaultdict
from typing import Dict, List, Tuple, Union

from ragraph.edge import Edge
from ragraph.graph import Graph
from ragraph.node import Node


class SigmaAnalysis:
    """Basic class to perform a sigma analysis on :obj:`ragraph.graph.Graph` objects.

    Arguments:
        graphs: List of graphs to compare. mode: One of "absolute" or "fraction".
        mode: Determines whether edge label overlap should be calculated as an absolute
            count over all edges between certain nodes or whether a fraction (percentage
            of label occurrence) is calculated as edge weights. Defaults to fraction.

    Note:
        Graphs are compared on leaf node level. The resulting sigma or overlap is
        currently only calculated in terms of overlapping edge labels.

    Note:
        Apart from label occurrence, the overall edge count is also added as an Edge
        weight, named `"_count"`. (The underscore prefix is added so it doesn't
        collide with regular label names)
    """

    def __init__(self, graphs: List[Graph], mode: str = "fraction"):
        self.graphs = graphs
        self.mode = mode

    def _reset_lazy_props(self):
        """Reset all lazy properties."""
        self._nodes = []
        self._node_dict = None
        self._edges = []
        self._edge_dict = None

    @property
    def graphs(self) -> List[Graph]:
        """List of graphs to be compared."""
        return self._graphs

    @graphs.setter
    def graphs(self, value):
        if not isinstance(value, list):
            raise TypeError(f"Key '{value}' should be a list of Graph objects.")

        for v in value:
            if not isinstance(v, Graph):
                raise TypeError(f"Key '{v}' should be a Graph object.")

        self._graphs = value
        self._reset_lazy_props()

    @property
    def mode(self) -> str:
        """Edge weight mode."""
        return self._mode

    @mode.setter
    def mode(self, value):
        if value not in ["fraction", "absolute"]:
            raise ValueError(f"'{value}' should be one of 'fraction' or 'absolute'.")

        self._mode = value
        self._reset_lazy_props()

    @property
    def nodes(self) -> List[Node]:
        """List of leaf nodes within the graph."""
        if not self._nodes:
            node_dict = {n.name: n for g in self.graphs for n in g.leafs}
            for n in node_dict.values():
                self._nodes.append(
                    Node(
                        name=n.name,
                        kind=n.kind,
                        labels=n.labels,
                        weights=n.weights,
                        annotations=n.annotations,
                    )
                )

        return self._nodes

    @property
    def node_dict(self) -> Dict[str, Node]:
        """Dictionary of node name to node."""
        if not self._node_dict:
            self._node_dict = {n.name: n for n in self.nodes}

        return self._node_dict

    @property
    def edges(self) -> List[Edge]:
        if not self._edges:
            edge_dict = defaultdict(list)

            for g in self._graphs:
                for e in g.edges:
                    edge_dict[e.source.name, e.target.name, e.kind].append(e)

            for key, edges in edge_dict.items():
                self._edges.append(
                    Edge(
                        source=self.node_dict[key[0]],
                        target=self.node_dict[key[1]],
                        kind=key[2],
                        labels=sorted(set([label for e in edges for label in e.labels])),
                        weights=self._get_edge_weights(edges),
                    )
                )

        return self._edges

    @property
    def edge_dict(self) -> Dict[Tuple[str, str], List[Edge]]:
        """Dictionary of source and target names to list of edges."""
        if not self._edge_dict:
            self._edge_dict = defaultdict(list)
            for e in self.edges:
                self._edge_dict[e.source.name, e.target.name].append(e)

        return self._edge_dict

    def _get_edge_weights(self, edges: List[Edge]) -> Dict[str, Union[int, float]]:
        """Compute weights for edge in Sigma DSM from the provided list of edges."""
        weight_counts: Dict[str, Union[int, float]] = {"_count": len(edges)}

        for e in edges:
            for label in e.labels:
                weight_counts[label] = weight_counts.get(label, 0) + 1

        div = 1 / len(self.graphs)
        return (
            weight_counts
            if self.mode == "absolute"
            else {key: value * div for key, value in weight_counts.items()}
        )
