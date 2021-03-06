#!/usr/bin/env python

import os
import logging
import argparse
from itertools import islice

from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (f1_score, precision_recall_curve, auc, confusion_matrix,
                             accuracy_score)
import pylab as pl

import features

def read_dataset(filename, use_text_features):
    if use_text_features:
        mask = set(['meta', 'text'])
    else:
        mask = set(['meta'])

    X, y = [], []
    points = list(features.filter(features.extract(filename), mask))
    for f, v in points:
        X.append(f.todict())
        y.append(v)
    return X, y


def print_confusion_matrix(y_test, y_pred):
    conf_mat = confusion_matrix(y_test, y_pred)
    actual = ' Actual '
    vertical_bar = ' | '
    horizontal_bar = '-'

    conf_mat_as_strings = str(conf_mat).split('\n')
    right_padding_length = max(map(lambda s: len(s), conf_mat_as_strings))
    left_padding_length = len(actual)

    lines = []
    lines.append(' ' * left_padding_length + vertical_bar +  'Predicted')
    lines.append('-' * (left_padding_length + len(vertical_bar) + right_padding_length))
    for i, line in enumerate(conf_mat_as_strings):
        left_padding = actual if i == 0 else ' ' * left_padding_length
        lines.append(left_padding + vertical_bar + line)
    print('Confusion matrix')
    for line in lines:
        print(line)


def plot_pr_curve(filename, y_test, probas_):
        precision, recall, thresholds = precision_recall_curve(y_test, probas_[:, 1])
        area = auc(recall, precision)

        pl.clf()
        pl.plot(recall, precision, label='Precision-Recall curve')
        pl.xlabel('Recall')
        pl.ylabel('Precision')
        pl.ylim([0.0, 1.05])
        pl.xlim([0.0, 1.0])
        pl.title('Precision-Recall: AUC=%0.2f' % area)
        pl.legend(loc="lower left")
        pl.savefig(filename)


def main():
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    parser = argparse.ArgumentParser(description='Run classification')
    parser.add_argument('prefix', help='directory which contains '
                                       '{train,dev,test}.json')
    parser.add_argument('--pr_curve', help='File to save precision-recall curve')
    parser.add_argument('--model', help='Pickled file to save best model')
    parser.add_argument('-t', action='store_true', help='Use text features')

    args = parser.parse_args()

    vectorizer = DictVectorizer()

    logging.info('Loading training data...')
    X_train, y_train = read_dataset(os.path.join(args.prefix, 'train.json'), args.t)

    logging.info('Pruning training data...')
    X_train = features.prune(X_train, threshold=[0.002, 0.998])
    X_train = vectorizer.fit_transform(X_train)

    logging.info('Loading development data...')
    X_dev, y_dev = read_dataset(os.path.join(args.prefix, 'dev.json'), args.t)
    X_dev = vectorizer.transform(X_dev)

    logging.info('Training...')
    scores = []
    for regularization in (0.01, 0.1, 1, 10, 100, 1000):
        model = LogisticRegression(penalty='l1', C=regularization, class_weight='auto')
        logging.info('regularization parameter: {0}'.format(regularization))
        model.fit(X_train, y_train)
        score = f1_score(y_dev, model.predict(X_dev))
        scores.append((score, regularization, model))
        logging.info('Dev score: {0}'.format(score))

    best_score, best_regularization, best_model = max(scores)

    logging.info('Loading test data...')
    X_test, y_test = read_dataset(os.path.join(args.prefix, 'test.json'), args.t)
    X_test = vectorizer.transform(X_test)
    y_pred = best_model.predict(X_test)

    print('Tuned regularization parameter: {0} (score={1})'.format(best_regularization,
                                                                   best_score))
    print('Test score: {0}'.format(f1_score(y_test, y_pred)))

    weights = vectorizer.inverse_transform(best_model.coef_)[0]
    sorted_weights = sorted(weights.iteritems(), key=lambda x: x[1], reverse=True)

    def print_weights(heading, iterator):
        print(heading)
        for i, (feat, weight) in enumerate(iterator):
            print('{0:.4f}  {1}'.format(weight, feat.encode('utf8')))

    print_weights('Most positive 1000 weights', islice(sorted_weights, 1000))
    print_weights('Most negative 1000 weights', islice(reversed(sorted_weights), 1000))

    print_confusion_matrix(y_test, y_pred)

    if args.pr_curve:
        probas_ = best_model.predict_proba(X_test)
        plot_pr_curve(args.pr_curve, y_test, probas_)

    if args.model:
        logging.info('Pickling best model...')
        try:
            import cPickle as pickle
        except:
            import pickle
        with open(args.model, 'w') as f:
            pickle.dump({'model': best_model, 'vectorizer': vectorizer}, f)

if __name__ == '__main__':
    main()
