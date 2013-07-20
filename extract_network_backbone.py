#!/usr/bin/env python

import argparse
try:
    import cPickle as pickle
except:
    import pickle

import networkx as nx
import scipy.integrate

def extract_backbone(g, alpha):
    backbone_graph = nx.Graph()
    for node in g:
        k_n = len(g[node])
        if k_n > 1:
            sum_w = sum(g[node][neighbor]['weight'] for neighbor in g[node])
            for neighbor in g[node]:
                edge_weight = g[node][neighbor]['weight']
                pij = float(edge_weight) / sum_w
                f = lambda x: (1-x)**(k_n-2)
                alpha_ij =  1 - (k_n-1) * scipy.integrate.quad(f, 0, pij)[0]
                if alpha_ij < alpha:
                    backbone_graph.add_edge(node, neighbor, weight=edge_weight)

                    # copy over node attributes
                    backbone_graph.node[node]['num_recipes'] = g.node[node]['num_recipes']
                    backbone_graph.node[neighbor]['num_recipes'] = g.node[neighbor]['num_recipes']
    return backbone_graph

def extract_backbone2(g, alpha):
    g2 = nx.Graph()
    for node1, node2 in g.edges_iter():
        weight = g.get_edge_data(node1, node2)['weight']

        if weight >= alpha:
            g2.add_edge(node1, node2, weight=weight)

    return g2

def main():
    parser = argparse.ArgumentParser(description='Extract the backbone of the network')
    parser.add_argument('in_gml', help='Input network gml file')
    parser.add_argument('out_gexf', help='Output network gexf file')
    parser.add_argument('--alpha', help='alpha', type=float, default=0.01)
    args = parser.parse_args()

    with open(args.in_gml) as f:
        graph = pickle.load(f)
    backbone_graph = extract_backbone(graph, args.alpha)
    nx.write_gexf(backbone_graph, args.out_gexf, encoding='utf-8')

if __name__ == '__main__':
    main()
