#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import deque, Counter
import re
import json

import MeCab

import preprocessing
import jptokenizer

STOP_WORDS = set([u'話題', u'入り', u'題入り', u'話', u'話題入り',
                      u'祝', u'感謝', u'有難',
                                        u'ありが', u'がとう', u'ござい', u'ありがとう'])



class FeatureVector(dict):
    def todict(self):
        def kv():
            for fname, fval in self.iteritems():
                yield ':'.join(fname), fval
        return dict(kv())

mecab = MeCab.Tagger("-Owakati")


def tokenize(s):
    output = mecab.parse(s)
    tokens = output.decode('utf8')
    for token in tokens.strip().split(' '):
        yield token

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

def ngrams(string):
    tokens = tokenize(string)
    for (c, w) in _ngrams(tokens):
        words = set(''.join(w.split()))
        if words & STOP_WORDS:
            continue
        yield (c, w)

def description(recipe):
    desc = recipe['description']
    for (c, w) in ngrams(desc):
        yield ('text', 'desc', str(c), w)

def ingredients(recipe):
    ingredientz = recipe['ingredients']
    for ingredient in ingredientz:
        normalized_ingredients = preprocessing.normalize(ingredient)
        for normalized_ingredient in normalized_ingredients:
            yield ('meta', 'ingr', normalized_ingredient)

def title(recipe):
    name = recipe['name']
    for (c, w) in ngrams(name):
        yield ('text', 'title', str(c), w)

def categories(recipe):
    for category in recipe['categories']:
        yield ('meta', 'categ', str(category))

def author(recipe):
    return ('meta', 'author', str(recipe['author']))

def history(recipe):
    hist = recipe['history'] if 'history' in recipe else ''
    for (c, w) in ngrams(hist):
        yield ('text', 'history', str(c), w)

def advice(recipe):
    adv = recipe['advice'] if 'advice' in recipe else ''
    for (c, w) in ngrams(adv):
        yield ('text', 'advice', str(c), w)

def has_instruction_images(recipe):
    key = 'images_instruction'
    return int(key in recipe and len(recipe[key]) > 0)

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
            for ngram in title(recipe):
                features[ngram] = 1
            for ngram in history(recipe):
                features[ngram] = 1
            for ngram in advice(recipe):
                features[ngram] = 1

            features[author(recipe)] = 1
            features[('meta', 'inst_img')] = has_instruction_images(recipe)

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

