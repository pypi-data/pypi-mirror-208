#!/usr/bin/env python3

"""
** Allows to summarize the state of each node of the graph. **
--------------------------------------------------------------

This allows a finer management of the cache by a fine tracking of the unchanged elements.
"""

import hashlib
import typing

import networkx



def compute_graph_items_hash(
    graph: networkx.MultiDiGraph
) -> dict[typing.Union[str, tuple[str, str, str]], str]:
    """
    ** Computes a signature for each node and edge, which reflects its state in the graph. **

    This is mean to detecting a change of attributes in one of the upstream elements.

    Parameters
    ----------
    graph : networkx.MultiDiGraph
        The assembly graph.

    Returns
    -------
    hashes : dict[typing.Union[str, tuple[str, str, str]], str]
        To each node and edge name, associate its state as a string.

    Notes
    -----
    The graph must not contain any cycles because the function would never returns.

    Examples
    --------
    >>> import pprint
    >>> from movia.core.classes.container import ContainerOutput
    >>> from movia.core.compilation.tree_to_graph import tree_to_graph
    >>> from movia.core.filters.basic.truncate import FilterTruncate
    >>> from movia.core.generation.audio.noise import GeneratorAudioNoise
    >>> from movia.core.optimisation.cache.hashes.graph import compute_graph_items_hash
    >>> container_out = ContainerOutput(
    ...     FilterTruncate(GeneratorAudioNoise.default().out_streams, 1).out_streams
    ... )
    >>> graph = tree_to_graph(container_out)
    >>> pprint.pprint(compute_graph_items_hash(graph))
    {'container_output_1': '93c8085e4619bd1d5a04a71e005441f5',
     'filter_truncate_1': '8725be07b5f831cf9d9d5e9e7bb5b5ac',
     'generator_audio_noise_1': 'b60c0f567ed5ef0ded54d08ea1f6c80a',
     ('filter_truncate_1', 'container_output_1', '0->0'): '8725be07b5f831cf9d9d5e9e7bb5b5ac|0',
     ('generator_audio_noise_1', 'filter_truncate_1', '0->0'): 'b60c0f567ed5ef0ded54d08ea1f6c80a|0'}
    >>>
    """
    assert isinstance(graph, networkx.MultiDiGraph), graph.__class__.__name__

    def complete(hashes, graph, node_name) -> str:
        if node_name not in hashes:
            node_attr = graph.nodes[node_name]
            local_node_signature = (
                f"{node_attr['class'].__name__}-"
                f"{'-'.join(str(node_attr['state'][k]) for k in sorted(node_attr['state']))}"
            )
            in_edges = sorted( # the name of the edges in order of arrival on the node
                graph.in_edges(node_name, data=False, keys=True),
                key=lambda src_dst_key: int(src_dst_key[2].split("->")[1])
            )
            local_edges_signature = "-".join(k.split("->")[0] for _, _, k in in_edges)
            parents_signature = "-".join(complete(hashes, graph, n) for n, _, _ in in_edges)
            signature = hashlib.md5( # md5 is the fastest
                f"{parents_signature}|{local_edges_signature}|{local_node_signature}".encode()
            ).hexdigest()
            hashes[node_name] = signature
            for _, dst, key in graph.out_edges(node_name, keys=True):
                hashes[(node_name, dst, key)] = f"{signature}|{int(key.split('->')[0])}"
        return hashes[node_name]

    hashes = {}
    for node_name in graph:
        complete(hashes, graph, node_name)
    return hashes
