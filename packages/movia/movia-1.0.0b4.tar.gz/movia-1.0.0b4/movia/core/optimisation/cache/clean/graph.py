#!/usr/bin/env python3

"""
** Allows to delete the obsolete node cache of the graph. **
-------------------------------------------------------------
"""

import itertools

import networkx

from movia.core.optimisation.cache.hashes.graph import compute_graph_items_hash



def clean_graph(graph: networkx.MultiDiGraph) -> networkx.MultiDiGraph:
    """
    ** Update inplace the `cache` attribute of each nodes of the graph. **

    Parameters
    ----------
    graph : networkx.MultiDiGraph
        The assembly graph.

    Returns
    -------
    updated_graph : networkx.MultiDiGraph
        The same graph with the updated `cache` node attribute.
        The underground data are shared, operate in-place.

    Examples
    --------
    >>> import pprint
    >>> from movia.core.classes.container import ContainerOutput
    >>> from movia.core.compilation.tree_to_graph import tree_to_graph
    >>> from movia.core.filters.basic.truncate import FilterTruncate
    >>> from movia.core.generation.audio.noise import GeneratorAudioNoise
    >>> from movia.core.optimisation.cache.clean.graph import clean_graph
    >>> container_out = ContainerOutput(
    ...     FilterTruncate(GeneratorAudioNoise.default().out_streams, 1).out_streams
    ... )
    >>> graph = tree_to_graph(container_out)
    >>> pprint.pprint(dict(clean_graph(graph).nodes("cache")))
    {'container_output_1': ('93c8085e4619bd1d5a04a71e005441f5', {}),
     'filter_truncate_1': ('8725be07b5f831cf9d9d5e9e7bb5b5ac', {}),
     'generator_audio_noise_1': ('b60c0f567ed5ef0ded54d08ea1f6c80a', {})}
    >>> pprint.pprint(list(graph.edges(keys=True, data=True)))
    [('filter_truncate_1',
      'container_output_1',
      '0->0',
      {'cache': ('8725be07b5f831cf9d9d5e9e7bb5b5ac|0', {})}),
     ('generator_audio_noise_1',
      'filter_truncate_1',
      '0->0',
      {'cache': ('b60c0f567ed5ef0ded54d08ea1f6c80a|0', {})})]
    >>> for _, data in graph.nodes(data=True):
    ...     data["cache"][1]["key"] = "value"
    ...
    >>> for *_, data in graph.edges(keys=True, data=True):
    ...     data["cache"][1]["key"] = "value"
    >>> graph.nodes["filter_truncate_1"]["state"]["duration_max"] = "2"
    >>> pprint.pprint(dict(clean_graph(graph).nodes("cache")))
    {'container_output_1': ('283e6b88de47a8bff419ff63c90f7bfe', {}),
     'filter_truncate_1': ('5f282ae75060d96da81046eddf6f42a9', {}),
     'generator_audio_noise_1': ('b60c0f567ed5ef0ded54d08ea1f6c80a',
                                 {'key': 'value'})}
    >>> pprint.pprint(list(graph.edges(keys=True, data=True)))
    [('filter_truncate_1',
      'container_output_1',
      '0->0',
      {'cache': ('5f282ae75060d96da81046eddf6f42a9|0', {})}),
     ('generator_audio_noise_1',
      'filter_truncate_1',
      '0->0',
      {'cache': ('b60c0f567ed5ef0ded54d08ea1f6c80a|0', {'key': 'value'})})]
    >>>
    """
    new_hashes = compute_graph_items_hash(graph) # assertions are done here
    edges_iter = (((s, d, k), data) for s, d, k, data in graph.edges(keys=True, data=True))
    for item, data in itertools.chain(graph.nodes(data=True), edges_iter):
        new_hash = new_hashes[item]
        if "cache" not in data or data["cache"][0] != new_hash:
            data["cache"] = (new_hashes[item], {})
    return graph
