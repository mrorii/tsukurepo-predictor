#!/usr/bin/env python

import json
import argparse
from collections import Counter

import preprocessing

def main():
    parser = argparse.ArgumentParser(description='Inspect top n ingredients')
    parser.add_argument('json', help='Input data file')
    parser.add_argument('--n', help='Number of ingredients to print', type=int, default=1000)
    args = parser.parse_args()

    ingredients_counter = Counter()

    with open(args.json, 'r') as f:
        for line in f:
            recipe = json.loads(line.strip())
            ingredients = recipe['ingredients']

            for ingredient in ingredients:
                for normalized_ingredient in preprocessing.normalize(ingredient):
                    ingredients_counter[normalized_ingredient] += 1

    for ingredient, count in ingredients_counter.most_common(args.n):
        print('{}\t{}'.format(ingredient.encode('utf8'), count))

if __name__ == '__main__':
    main()
