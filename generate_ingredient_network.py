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

def calc_pmis(ingredient2recipes, valid_ingredients, num_recipes):
    for a, b in itertools.combinations(ingredient2recipes.iterkeys(), 2):
        if not a in valid_ingredients or not b in valid_ingredients:
            continue

        numerator = len(ingredient2recipes[a] & ingredient2recipes[b]) * num_recipes
        if numerator == 0:
            continue

        denominator = len(ingredient2recipes[a]) * len(ingredient2recipes[b])
        pmi = math.log(float(numerator) / denominator)
        yield a, b, pmi

def main():
    parser = argparse.ArgumentParser(description='Generate ingredient complement network')
    parser.add_argument('json', help='Input data file')
    parser.add_argument('mapping', help='Input ingredient-ID mapping file')
    parser.add_argument('gml', help='Output network gml file')
    parser.add_argument('--num_recipes', help='Number of recipes', type=int, default=47884)
    parser.add_argument('--histo', help='Output PMI histogram file')
    args = parser.parse_args()

    with open(args.mapping, 'r') as f:
        ingredient2id = pickle.load(f)['ingredient2id']
    valid_ingredients = set(ingredient2id.iterkeys())

    ingredient2recipes = load_ingredient2recipes(args.json)

    graph = nx.Graph()
    pmis = [] 
    for a, b, pmi in calc_pmis(ingredient2recipes, valid_ingredients, args.num_recipes):
        graph.add_edge(ingredient2id[a], ingredient2id[b], weight=pmi)
        pmis.append(pmi)

    with open(args.gml, 'w') as f:
        for line in nx.generate_gml(graph):
            f.write('{}\n'.format(line))

    if args.histo:
        import pylab as pl
        n, bins, patches = pl.hist(pmis, bins=1000)
        pl.savefig(args.histo)

if __name__ == '__main__':
    main()
