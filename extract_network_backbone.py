#!/usr/bin/env python

import sys
import json
import argparse
import itertools
import math
from collections import defaultdict
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
    return backbone_graph

def main():
    parser = argparse.ArgumentParser(description='Extract the backbone of the network')
    parser.add_argument('in_gml', help='Input network gml file')
    parser.add_argument('out_gml', help='Output network gml file')
    parser.add_argument('--alpha', help='alpha', type=float, default=0.05)
    args = parser.parse_args()

    graph = nx.read_gml(args.in_gml)
    backbone_graph = extract_backbone(graph, args.alpha)
    nx.write_gml(backbone_graph, args.out_gml)

if __name__ == '__main__':
    main()
