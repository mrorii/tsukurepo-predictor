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

import preprocessing

def load_ingredient2recipes(filename):
    ingredient2recipes = defaultdict(set)
    with open(filename, 'r') as f:
        for line in f:
            recipe = json.loads(line.strip())
            recipe_id = recipe['id']
            ingredients = recipe['ingredients']
            for ingredient in ingredients:
                for normalized_ingredient in preprocessing.normalize(ingredient):
                    ingredient2recipes[normalized_ingredient].add(recipe_id)
    return ingredient2recipes

def calc_pmis(ingredient2recipes, valid_ingredients, num_recipes, use_log=False):
    for a, b in itertools.combinations(ingredient2recipes.iterkeys(), 2):
        if not a in valid_ingredients or not b in valid_ingredients:
            continue

        numerator = len(ingredient2recipes[a] & ingredient2recipes[b]) * num_recipes
        if numerator == 0:
            continue

        denominator = len(ingredient2recipes[a]) * len(ingredient2recipes[b])

        pmi = float(numerator) / denominator
        if use_log:
            pmi = math.log(pmi)

        yield a, b, pmi

def main():
    parser = argparse.ArgumentParser(description='Generate ingredient complement network')
    parser.add_argument('json', help='Input data file')
    parser.add_argument('mapping', help='Input ingredient-ID mapping file')
    parser.add_argument('pkl', help='Output network pkl file')
    parser.add_argument('--num_recipes', help='Number of recipes', type=int, default=47884)
    parser.add_argument('--histo', help='Output PMI histogram file')
    parser.add_argument('--log', action='store_true', help='Use log for calculating PMI',
                        default=False)
    args = parser.parse_args()

    with open(args.mapping, 'r') as f:
        ingredient2id = pickle.load(f)['ingredient2id']
    valid_ingredients = set(ingredient2id.iterkeys())

    ingredient2recipes = load_ingredient2recipes(args.json)

    graph = nx.Graph()
    pmis = []
    for a, b, pmi in calc_pmis(ingredient2recipes, valid_ingredients, args.num_recipes, args.log):
        graph.add_edge(a, b, weight=pmi)
        graph.node[a]['num_recipes'] = len(ingredient2recipes[a])
        graph.node[b]['num_recipes'] = len(ingredient2recipes[b])
        pmis.append(pmi)
        # print '{}\t{}\t{}\t{}\t{}'.format(pmi, a.encode('utf8'), b.encode('utf8'),
        #                                   len(ingredient2recipes[a]), len(ingredient2recipes[b]))

    with open(args.pkl, 'w') as f:
        pickle.dump(graph, f)

    if args.histo:
        import pylab as pl
        n, bins, patches = pl.hist(pmis, bins=1000)
        pl.savefig(args.histo)

if __name__ == '__main__':
    main()
