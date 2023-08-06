"""Capability to import GRIP data exports."""
from pathlib import Path
from typing import Union
from uuid import UUID

from lxml import etree

from ragraph.edge import Edge
from ragraph.graph import Graph
from ragraph.node import Node


def from_grip(path: Union[str, Path]) -> Graph:
    """Decode GRIP XML file, string, or element into a Graph.

    Arguments:
        path: GRIP XML file path.

    Returns:
        Graph object.
    """

    tree = etree.parse(str(path))
    root = tree.getroot()

    graph = Graph(
        uuid=root.attrib.get("WorkspaceID"),
        name=root.attrib.get("WorkspaceName"),
        annotations=dict(root.attrib),
    )

    parse_collection(graph, root, "Objecten", "Object", "object")
    parse_objectenboom(graph, root)

    parse_collection(graph, root, "Functies", "Functie", "functie")
    parse_collection(graph, root, "Systeemeisen", "Systeemeis", "systeemeis")
    parse_collection(graph, root, "Scope", "Scope", "scope")
    parse_collection(graph, root, "Raakvlakken", "Raakvlak", "raakvlak")

    parse_systeemeis_edges(graph, root)
    parse_object_edges(graph, root)
    parse_scope_edges(graph, root)
    parse_raakvlak_edges(graph, root)

    return graph


def parse_collection(graph: Graph, root: etree.Element, collection: str, item: str, kind: str):
    coll = root.find(collection)
    for el in coll.iterfind(item):
        annotations = dict(el.attrib)
        if el.find("ID") is not None:
            id1 = el.find("ID").attrib.get("ID1")
            name = el.attrib.get("Name")
            if name:
                name = f"{name} | {id1}"
            else:
                name = id1
        else:
            name = el.attrib.get("Name")
        graph.add_node(
            Node(
                uuid=el.attrib.get("GUID"),
                name=name,
                kind=kind,
                annotations=annotations,
            )
        )


def parse_objectenboom(graph: Graph, root: etree.Element):
    collection = root.find("Objecten")
    for el in collection.iterfind("Object"):
        parent = graph[UUID(el.attrib.get("GUID"))]
        for sub in el.iterfind("SI_Onderliggend"):
            for obj in sub.iterfind("ObjectOnderliggend"):
                child_id = UUID(obj.attrib.get("GUID"))
                graph[child_id].parent = parent


def parse_systeemeis_edges(graph: Graph, root: etree.Element, kind="systeemeis"):
    elems = root.find("Systeemeisen").iterfind("Systeemeis")
    for el in elems:
        source = graph[UUID(el.attrib.get("GUID"))]

        for me_eis in el.iterfind("CI_MEEisObject"):
            eis_obj = me_eis.find("EisObject")
            eis_obj.attrib.get("GUID")
            object_id = eis_obj.find("SI_Object").find("Object").attrib.get("GUID")
            target = graph[UUID(object_id)]
            graph.add_edge(Edge(source, target, kind=kind))
            graph.add_edge(Edge(target, source, kind=kind))


def parse_object_edges(graph: Graph, root: etree.Element, kind="object"):
    collection = root.find("Objecten")
    for el in collection.iterfind("Object"):
        source = graph[UUID(el.attrib.get("GUID"))]

        for sub in el.iterfind("SI_Functie"):
            for functie in sub.iterfind("Functie"):
                functie_id = UUID(functie.attrib.get("GUID"))
                target = graph[functie_id]
                graph.add_edge(Edge(source, target, kind=kind))
                graph.add_edge(Edge(target, source, kind=kind))


def parse_scope_edges(graph: Graph, root: etree.Element, kind="scope"):
    elems = root.find("Scope").iterfind("Scope")
    for el in elems:
        source = graph[UUID(el.attrib.get("GUID"))]

        for eis in el.iterfind("SI_Systeemeis"):
            eis_id = eis.find("Systeemeis").attrib.get("GUID")
            target = graph[UUID(eis_id)]
            graph.add_edge(Edge(source, target, kind=kind))
            graph.add_edge(Edge(target, source, kind=kind))

        for functie in el.iterfind("SI_Functie"):
            functie_id = functie.find("Functie").attrib.get("GUID")
            target = graph[UUID(functie_id)]
            graph.add_edge(Edge(source, target, kind=kind))
            graph.add_edge(Edge(target, source, kind=kind))

        for raakvlak in el.iterfind("SI_Raakvlak"):
            raakvlak_id = raakvlak.find("Raakvlak").attrib.get("GUID")
            target = graph[UUID(raakvlak_id)]
            graph.add_edge(Edge(source, target, kind=kind))
            graph.add_edge(Edge(target, source, kind=kind))

        for obj in el.iterfind("SI_Object"):
            obj_id = obj.find("Object").attrib.get("GUID")
            target = graph[UUID(obj_id)]
            graph.add_edge(Edge(source, target, kind=kind))
            graph.add_edge(Edge(target, source, kind=kind))


def parse_raakvlak_edges(graph: Graph, root: etree.Element, kind="raakvlak"):
    elems = root.find("Raakvlakken").iterfind("Raakvlak")
    for el in elems:
        raakvlak = graph[UUID(el.attrib.get("GUID"))]

        objecten = [
            graph[UUID(item.find("Objecttype").attrib.get("GUID"))]
            for item in el.iterfind("SI_Objecttype")
        ]

        functies = [
            graph[UUID(item.find("Functie").attrib.get("GUID"))]
            for item in el.iterfind("SI_Functie")
        ]

        for i, obj in enumerate(objecten):
            graph.add_edge(Edge(raakvlak, obj, kind=kind))
            graph.add_edge(Edge(obj, raakvlak, kind=kind))
            for func in functies:
                graph.add_edge(Edge(obj, func, kind=kind))
                graph.add_edge(Edge(func, obj, kind=kind))

            for other in objecten[i + 1 :]:
                graph.add_edge(Edge(obj, other, kind=kind))
                graph.add_edge(Edge(other, obj, kind=kind))

        for func in functies:
            graph.add_edge(Edge(raakvlak, func, kind=kind))
            graph.add_edge(Edge(func, raakvlak, kind=kind))
