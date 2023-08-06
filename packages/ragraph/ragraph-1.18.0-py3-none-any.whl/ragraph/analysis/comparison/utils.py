from typing import List

from ragraph.edge import Edge
from ragraph.graph import Graph
from ragraph.node import Node


def get_unique_leafs(a: Graph, b: Graph) -> List[Node]:
    """Get unique leafs in graph a.

    Arguments:
        a: Graph object.
        b: Graph object.

    Returns:
        List of unique leafs in Graph a.
    """
    return [
        a.node_dict[n] for n in a.node_dict.keys() - b.node_dict.keys() if a.node_dict[n].is_leaf
    ]


def get_common_leafs(a: Graph, b: Graph, ue: List[Edge]) -> List[Node]:
    """Get common leafs in graph a and b

    Arguments:
      a: Graph object.
      b: Graph object.
      ue: List of unique edges.

    Returns:
      List of common leafs in graphs a and b.
    """
    # Shared leafs in both graphs, which do NOT participate in unique edges.
    common_leafs = [
        a.node_dict[n] for n in (a.node_dict.keys() & b.node_dict.keys()) if a.node_dict[n].is_leaf
    ]
    return common_leafs


def check_edge_equality(a: Edge, b: Edge) -> bool:
    """Checks if two edges are equal based on source, target, kind, labels.

    Arguments:
        a: Edge a.
        b: Edge b

    Returns:
        Whether edges are considered equal.
    """
    return (
        a.source.name == b.source.name
        and a.target.name == b.target.name
        and a.kind == b.kind
        and set(a.labels) == set(b.labels)
    )


def get_unique_edges(a: Graph, b: Graph) -> List[Edge]:
    """Get unique edges in graph a.

    Arguments:
        a: Graph object.
        b: Graph object.

    Returns:
        List of unique edges in a.
    """
    unq = [ea for ea in a.edges if not any(check_edge_equality(ea, eb) for eb in b.edges)]
    return unq
