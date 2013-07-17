#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import deque, Counter
import re
import json

import helper
import jptokenizer

STOP_WORDS = set([u'話題', u'題入り', u'話'])

class FeatureVector(dict):
    def todict(self):
        def kv():
            for fname, fval in self.iteritems():
                yield ':'.join(fname), fval
        return dict(kv())

TOKENIZER = jptokenizer.JPSimpleTokenizer()

def tokenize(s):
    return TOKENIZER.tokenize(s)

def _ngrams(tokens):
    """ N-gram features """
    ngram = deque(maxlen=3)
    for token in tokens:
        ngram.append(token)
        yield (1, token)
        if len(ngram) >= 2:
            yield (2, '%s %s' % (ngram[-2], ngram[-1]))
        if len(ngram) == 3:
            yield (3, ' '.join(ngram))

def ngrams(tokens):
    for (c, w) in _ngrams(tokens):
        words = set(w.split())
        if words & STOP_WORDS:
            continue
        yield (c, w)

def description(recipe):
    desc = tokenize(recipe['description'])
    for (c, w) in ngrams(desc):
        yield ('desc', str(c), w)

def ingredients(recipe):
    ingredientz = recipe['ingredients']
    for ingredient in ingredientz:
        normalized_ingredients = helper.normalize(ingredient)
        for normalized_ingredient in normalized_ingredients:
            yield ('ingr', normalized_ingredient)

def name(recipe):
    name = recipe['name']
    for (c, w) in ngrams(name):
        yield ('name', str(c), w)

def categories(recipe):
    for category in recipe['categories']:
        yield ('categ', category)

def extract(filename):
    with open(filename) as f:
        for line in f:
            recipe = json.loads(line.strip())
            features = FeatureVector()

            for ingredient in ingredients(recipe):
                features[ingredient] = 1
            for category in categories(recipe):
                features[category] = 1
            for ngram in description(recipe):
                features[ngram] = 1
            for ngram in name(recipe):
                features[ngram] = 1

            label = recipe['label'] if 'label' in recipe else 0
            yield features, label

def filter(stream, mask):
    for features, label in stream:
        features = FeatureVector((k, v) for k, v in features.iteritems() if k[0] in mask)
        yield features, label


def prune(instances, threshold=5):
    feature_counts = Counter()
    for instance in instances:
        for feature in instance:
            feature_counts[feature] += 1

    valid_features = set(f for f in feature_counts if feature_counts[f] >= threshold)

    for instance in instances:
        for feature in instance.keys():
            if not feature in valid_features:
                del instance[feature]
    return instances

