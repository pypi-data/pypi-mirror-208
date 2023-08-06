#!/usr/bin/env python3

"""
** Interacts with ``graphviz`` to position and draw the assembly graph. **
--------------------------------------------------------------------------

Note
----
Requires  the ``pygraphviz`` python module and the installation is not very simple.
See ``https://pygraphviz.github.io/documentation/stable/install.html``.
"""

import numbers

import cv2
import networkx
import numpy as np
try:
    import pygraphviz
except ImportError as err:
    raise ImportError(
            "need pygraphviz: https://pygraphviz.github.io/documentation/stable/install.html"
        ) from err



def clear_positions(agraph: pygraphviz.AGraph) -> None:
    """
    ** Delete all position and dimension attribute on nodes and edges. **

    Parameters
    ----------
    agraph : pygraphviz.AGraph
        The graph whose you want to delete all positions.
    """
    assert isinstance(agraph, pygraphviz.AGraph), agraph.__class__.__name__

    for node in agraph.nodes_iter():
        for key in ("pos", "height", "width"):
            node.attr[key] = None
    for edge_name in agraph.edges_iter(keys=True):
        node_src, node_dst, key = edge_name
        edge = agraph.get_edge(node_src, node_dst, key=key)
        if edge.attr.has_key("pos"):
            edge.attr["pos"] = ""


def compute_positions(agraph: pygraphviz.AGraph) -> dict[str]:
    """
    ** Find a position for the nodes and edges. **

    Compute the dimensions only if they where not already defines.

    Parameters
    ----------
    agraph : pygraphviz.AGraph
        The graph whose elements you want to position.
        The formatting parameters must be filled in beforehand.

    Returns
    -------
    layouts : dict
        To each node and edge name, associate the positions, dimensions and style.
        Normalizes the positions and dimensions between 0 and 1.
    """
    assert isinstance(agraph, pygraphviz.AGraph), agraph.__class__.__name__

    # calculates the positions and dimensions of nodes and edges
    pad = 5.0 # in point
    if not has_positions(agraph):
        clear_positions(agraph)
        agraph.graph_attr["margin"] = 0
        agraph.graph_attr["pad"] = pad / 72 # inch to point
        agraph.graph_attr["splines"] = "spline" # or "polyline"
        agraph.graph_attr.update(rankdir="LR")
        agraph.layout(prog="dot", args="") # available progs are "neato, dot, twopi, circo, fdp, nop

    # scale factors
    x_min, y_min, x_max, y_max = agraph.graph_attr.get("bb").split(",")
    x_min, y_min, x_max, y_max = float(x_min), float(y_min), float(x_max), float(y_max)
    x_min, y_min, x_max, y_max = (
        min(x_min, x_max), min(y_min, y_max), max(x_min, x_max), max(y_min, y_max)
    )
    x_min, x_max = x_min-pad, x_max+pad
    y_min, y_max = y_min-pad, y_max+pad
    factor_pxl = 1 / max((x_max-x_min), (y_max-y_min))

    # extracts positions and dimensions
    layouts = {}
    for node in agraph.nodes_iter():
        layouts[node.name] = {
            "x": factor_pxl * (float(node.attr["pos"].split(",")[0])-x_min),
            "y": factor_pxl * (float(node.attr["pos"].split(",")[1])-y_min),
            "width": factor_pxl * float(node.attr["width"]) * 72, # point to inch
            "height": factor_pxl * float(node.attr["height"]) * 72,
            "shape": node.attr["shape"],
        }
    for edge_name in agraph.edges_iter(keys=True):
        edge = agraph.get_edge(*edge_name)
        pos = [
            (factor_pxl * (float(x)-x_min), factor_pxl * (float(y)-y_min))
            for *t, x, y in (p.split(",") for p in edge.attr["pos"].split(" ")) if not t
        ]
        layouts[edge_name] = {"pos": pos}
    return layouts


def create_and_init_agraph(graph: networkx.MultiDiGraph) -> pygraphviz.AGraph:
    """
    ** Returns the ``pygraphviz.AGraph`` version of the assembly graph. **

    Also initializes node and edge formatting parameters.
    The positioning parameters are not calculated here.

    Parameters
    ----------
    graph : networkx.MultiDiGraph
        The assembly graph generated for example by the function
        ``movia.core.compilation.fraph.to_graph.tree_to_graph``.

    Returns
    -------
    agraph : pygraphviz.AGraph
        The equivalent graphviz version.
    """
    assert isinstance(graph, networkx.MultiDiGraph), graph.__class__.__name__

    # conversion to graphviz
    agraph = networkx.nx_agraph.to_agraph(graph)

    # define general edge style
    agraph.edge_attr["arrowhead"] = "normal" # box, crow, diamond, dot, inv, none, normal, tee, vee
    agraph.edge_attr["color"] = "#000000"
    agraph.edge_attr["fontcolor"] = "#000000"
    agraph.edge_attr["fontname"] = "normal" # ubuntu
    agraph.edge_attr["label"] = "" # accents and \n are supproted
    agraph.edge_attr["style"] = "solid" # solid, dashed, dotted, bold

    # define general node style
    agraph.node_attr["color"] = "#000000" # contour color
    agraph.node_attr["fontcolor"] = "#000000"
    agraph.node_attr["fontname"] = "normal" # ubuntu
    agraph.node_attr["label"] = "" # accents and \n are supproted
    agraph.node_attr["shape"] = "ellipse" # box, ellipse, oval, circle, point, diamond, square
    agraph.node_attr["style"] = "solid" # solid, dashed, dotted, bold

    # apply specific styles
    for edge_name in agraph.edges_iter(keys=True):
        node_src, node_dst, key = edge_name
        edge = agraph.get_edge(node_src, node_dst, key=key)
        src, dst = key.split("->")
        edge.attr["label"] = f"{src}\u2192{dst}"
        edge.attr["fontsize"] = 9.33 # default 14.0

    return agraph


def draw(agraph: pygraphviz.AGraph, dpi: int, form: str) -> tuple[tuple[int, int], bytes]:
    """
    ** Allows to calculate the picture of the graph. **

    Parameters
    ----------
    agraph : pygraphviz.AGraph
        The graph you want to draw.
        The graph must be ready. That is to say that the function
        ``movia.gui.graph.layout.compute_positions`` has been called.
    dpi : int
        The resolution. 100 gives a 'normal' size.
    form : str
        The format of the image. For example "png", jpg", "svg"...

    Returns
    -------
    shape : tuple[int, int]
        The dimensions (width, height) of the image in pxl.
    picture : bytes
        The binary content of the graph picture in the requested format.
    """
    assert isinstance(agraph, pygraphviz.AGraph), agraph.__class__.__name__
    assert isinstance(dpi, numbers.Integral), dpi.__class__.__name__
    assert dpi > 1, dpi
    assert isinstance(form, str), form.__class__.__name__

    agraph.graph_attr["dpi"] = int(dpi)
    if form.lower() in {"png", "svg"}:
        agraph.graph_attr["bgcolor"] = "transparent"

    img_bytes = agraph.draw(path=None, format=form)
    assert img_bytes, f"impossible to draw in the {form} format"
    img_np = np.frombuffer(img_bytes, np.uint8)
    img_cv2 = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
    assert img_cv2 is not None, "failed to convert with cv2"
    height, width, *_ = img_cv2.shape

    return (width, height), img_bytes


def has_positions(agraph: pygraphviz.AGraph) -> bool:
    """
    ** Serach il all positions and shapes are defines. **

    Parameters
    ----------
    agraph : pygraphviz.AGraph
        The graph whose you want to know if the positions are defines.

    Returns
    -------
    bool
        True if all the positions are defines.
    """
    assert isinstance(agraph, pygraphviz.AGraph), agraph.__class__.__name__

    for node in agraph.nodes_iter():
        pos = node.attr.get("pos")
        if not pos or pos == "None":
            return False
        if not node.attr.get("height") or not node.attr.get("width"):
            return False
    for edge_name in agraph.edges_iter(keys=True):
        node_src, node_dst, key = edge_name
        edge = agraph.get_edge(node_src, node_dst, key=key)
        if not edge.attr.get("pos"):
            return False
    return True


def same_structure(agraph: pygraphviz.AGraph, graph: networkx.MultiDiGraph) -> bool:
    """
    ** Check if the two graph are equivalents. **

    Parameters
    ----------
    agraph : pygraphviz.AGraph
        A graph to compare at ``graph``.
    graph : networkx.MultiDiGraph
        A graph to compare at ``agraph``.

    Returns
    -------
    bool
        True is the both graphs have the same nodes and edges.
    """
    assert isinstance(agraph, pygraphviz.AGraph), agraph.__class__.__name__
    assert isinstance(graph, networkx.MultiDiGraph), graph.__class__.__name__

    anodes = {str(n) for n in agraph}
    nodes = set(graph)
    if anodes != nodes:
        return False
    aedges = set(agraph.edges_iter(keys=True))
    edges = set(graph.edges(keys=True))
    if aedges != edges:
        return False
    return True
