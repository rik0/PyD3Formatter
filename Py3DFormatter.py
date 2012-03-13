# Copyright (C) 2012 Enrico Franchi
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import argparse
import json
import networkx as nx

from os import path
import sys

FORMATS = ('dot', 'gexf', 'gml', 'gpickle',
           'graphml', 'pajek', 'yaml')
"""Available formats"""

def read_network(network_path, fmt=None, **kwargs):
    """
    Reads a network from filesystem.

    :param network_path: The file to read the network from
    :param fmt: the format the network was stored in (some kind of guessing is made from the filename, if left blank)
    :param kwargs: Additional arguments to be passed to the corresponding networkx.read_* function
    :return: the network
    :rtype: networkx.Graph
    """
    if fmt is None:
        _, ext = path.splitext(network_path)
        fmt = ext[1:]
        if fmt not in FORMATS:
            raise IOError(
                "Did not understand format from filename %s." % network_path)
    fn = getattr(nx, 'read_' + fmt)
    return fn(network_path, **kwargs)

def convert_network(network):
    """
    Coverts network to a dict based format

    :param network: the network
    :type network: networkx.Graph
    :return: the dict like structure
    :rtype: dict
    """

    assert isinstance(network, nx.Graph)

    nodes_list = []
    edges_list = []

    for node, neighbours in network.adjacency_iter():
        node_dict = dict(
            name=str(node),
            **network.node[node])
        nodes_list.append(node_dict)
        for target, attributes in neighbours.iteritems():
            edge_dict = dict(
                source=node,
                target=target,
                **attributes )
            edges_list.append(edge_dict)
    return dict(nodes=nodes_list, links=edges_list)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', help="Input file path", default=None)
    parser.add_argument(
        '-o', '--output', help="Output file path",
        default=None)
    parser.add_argument('--page-rank',
                        help="Adds page rank to the output network",
                        action='store_const', default=False, const=True)

    namespace = parser.parse_args()

    if namespace.input is None:
        graph = nx.powerlaw_cluster_graph(100, 8, 0.1)
    else:
        graph = read_network(namespace.input)

    if namespace.page_rank:
        page_rank_dictionary = nx.pagerank(graph)
        for node, rank in page_rank_dictionary.iteritems():
            graph.add_node(node, pagerank=rank)

    if namespace.eigenvector:
        eig_dictionary = nx.eigenvector_centrality(graph)
        for node, rank in eig_dictionary.iteritems():
            graph.add_node(node, eigenvector_centrality=rank)

    if namespace.betweenness:
        betw_dictionary = nx.betweenness_centrality(graph)
        for node, rank in betw_dictionary.iteritems():
            graph.add_node(node, betweenness=rank)

    graph_dict = convert_network(graph)

    if namespace.output is None:
        out = sys.stdout
    else:
        out = file(namespace.output, 'w')

    json.dump(graph_dict, out)


if __name__ == '__main__':
    main()
