"""Delta analysis module."""

from typing import Dict, List

from ragraph.analysis.comparison.utils import (
    get_common_leafs,
    get_unique_edges,
    get_unique_leafs,
)
from ragraph.edge import Edge
from ragraph.graph import Graph
from ragraph.node import Node


class DeltaAnalysis:
    """Basic class for performing a delta analysis on two Graph objects.

    Arguments:
        graph_a: Base graph object for comparison.
        graph_b: Reference graph object for comparison.

    Note:
        Graphs are compared on leaf node level, where node names are used to determine
        if nodes are unique or not.
    """

    def __init__(self, graph_a: Graph, graph_b: Graph):
        self.graph_a = graph_a
        self.graph_b = graph_b

    def _reset_lazy_props(self):
        """Reset all lazy properties."""
        self._unq_leafs_a = None
        self._unq_leafs_b = None
        self._sm_leafs_ab = None
        self._cm_leafs_ab = None
        self._unq_edges_a = None
        self._unq_edges_b = None
        self._cm_edges_ab = None
        self._node_dict = None
        self._nodes = []
        self._node_dict = None
        self._edges = []

    @property
    def graph_a(self) -> Graph:
        """Graph A to be compared."""
        return self._graph_a

    @graph_a.setter
    def graph_a(self, value):
        if not isinstance(value, Graph):
            raise TypeError(f"Key '{value}' should be a Graph object.")
        self._graph_a = value
        self._reset_lazy_props()

    @property
    def graph_b(self) -> Graph:
        """Graph B to be compared."""
        return self._graph_b

    @graph_b.setter
    def graph_b(self, value):
        if not isinstance(value, Graph):
            raise TypeError(f"Key '{value}' should be a Graph object.")
        self._graph_b = value
        self._reset_lazy_props()

    @property
    def unq_leafs_a(self) -> List[Node]:
        """List of leafs that are only present in graph a."""
        if self._unq_leafs_a is None:
            self._unq_leafs_a = get_unique_leafs(a=self.graph_a, b=self.graph_b)
        return self._unq_leafs_a

    @property
    def unq_leafs_b(self) -> List[Node]:
        """List of leafs that are only present in graph b."""
        if self._unq_leafs_b is None:
            self._unq_leafs_b = get_unique_leafs(a=self.graph_b, b=self.graph_a)
        return self._unq_leafs_b

    @property
    def cm_leafs_ab(self) -> List[Node]:
        """List of leafs that are present in graph a and b."""
        if self._cm_leafs_ab is None:
            ue = self.unq_edges_a + self.unq_edges_b
            self._cm_leafs_ab = get_common_leafs(a=self.graph_a, b=self.graph_b, ue=ue)
        return self._cm_leafs_ab

    @property
    def unq_edges_a(self) -> List[Edge]:
        """List of edges that are only present in graph a."""
        if self._unq_edges_a is None:
            self._unq_edges_a = get_unique_edges(a=self.graph_a, b=self.graph_b)
        return self._unq_edges_a

    @property
    def unq_edges_b(self) -> List[Edge]:
        """List of edges that are only present in graph b."""
        if self._unq_edges_b is None:
            self._unq_edges_b = get_unique_edges(a=self.graph_b, b=self.graph_a)
        return self._unq_edges_b

    @property
    def cm_edges_ab(self) -> List[Edge]:
        """List of edges that are present in both graphs."""
        if self._cm_edges_ab is None:
            self._cm_edges_ab = [
                edge for edge in self.graph_a.edge_list if edge not in set(self.unq_edges_a)
            ]
        return self._cm_edges_ab

    @property
    def node_dict(self) -> Dict[str, Node]:
        """Dictionary from node name to Node object"""
        if self._node_dict is None:
            self._node_dict = {n.name: n for n in self.nodes}

        return self._node_dict

    @property
    def nodes(self) -> List[Node]:
        """List of nodes of the delta graph."""
        if not self._nodes:
            for leaf in self.unq_leafs_a:
                self._add_node(n=leaf, kind=leaf.kind + "_unique_a")
            for leaf in self.cm_leafs_ab:
                self._add_node(n=leaf, kind=leaf.kind + "_common_ab")
            for leaf in self.unq_leafs_b:
                self._add_node(n=leaf, kind=leaf.kind + "_unique_b")

        return self._nodes

    @property
    def edges(self) -> List[Edge]:
        """List of edges of the delta graph."""
        if not self._edges:
            for edge in self.unq_edges_a:
                self._add_edge(e=edge, kind=edge.kind + "_unique_a")
            for edge in self.cm_edges_ab:
                self._add_edge(e=edge, kind=edge.kind + "_common_ab")
            for edge in self.unq_edges_b:
                self._add_edge(e=edge, kind=edge.kind + "_unique_b")

        return self._edges

    def _add_node(self, n: Node, kind: str) -> None:
        """Add Node to Delta Graph."""
        self._nodes.append(
            Node(
                name=n.name,
                kind=kind,
                labels=n.labels,
                weights=n.weights,
                annotations=n.annotations,
            )
        )

    def _add_edge(self, e: Edge, kind: str) -> None:
        """Add edge to Delta Graph."""
        self._edges.append(
            Edge(
                source=self.node_dict[e.source.name],
                target=self.node_dict[e.target.name],
                kind=kind,
                labels=e.labels,
                weights=e.weights,
                annotations=e.annotations,
            )
        )
