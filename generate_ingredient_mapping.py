#!/usr/bin/env python

import sys
import argparse
import json
from collections import Counter
try:
    import cPickle as pickle
except:
    import pickle

import preprocessing

def main():
    parser = argparse.ArgumentParser(description='Generate an ingredient-ID mapping file')
    parser.add_argument('json', help='Input data file')
    parser.add_argument('--threshold', type=int, default=5,
                        help='Cutoff of how many times an ingredient should occur in recipes',)
    parser.add_argument('pkl', help='Output pickle file')
    args = parser.parse_args()

    ingredients_counter = Counter()

    with open(args.json, 'r') as f:
        for line in f:
            recipe = json.loads(line.strip())
            ingredients = recipe['ingredients']

            for ingredient in ingredients:
                for normalized_ingredient in preprocessing.normalize(ingredient):
                    ingredients_counter[normalized_ingredient] += 1

    ingredient_id = 1
    ingredient2id = {}
    for ingredient in sorted(ingredients_counter):
        count = ingredients_counter[ingredient]
        if count < args.threshold:
            continue
        ingredient2id[ingredient] = ingredient_id
        ingredient_id += 1

    id2ingredient = dict((v, k) for k, v in ingredient2id.iteritems())

    with open(args.pkl, 'w') as f:
        pickle.dump({
            'ingredient2id': ingredient2id,
            'id2ingredient': id2ingredient,
        }, f)

if __name__ == '__main__':
    main()
