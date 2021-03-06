#!/usr/bin/env python

import os
import logging
import argparse
import random
import json
import time
import datetime

def load_data(filename):
    with open(filename, 'r') as f:
        for line in f:
            yield json.loads(line.strip())

def read_date(date_str):
    try:
        return time.strptime(date_str, '%Y-%m-%d')
    except:
        return time.strptime(date_str, '%y/%m/%d')

def has_progressed(days, t1, t2):
    t1 = datetime.datetime.fromtimestamp(time.mktime(t1))
    t2 = datetime.datetime.fromtimestamp(time.mktime(t2))
    return (t2 - t1).days > days

def main():
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    parser = argparse.ArgumentParser(description='Split data into train, dev, and test')
    parser.add_argument('json', help='Input data file')
    parser.add_argument('output_dir')
    parser.add_argument('--threshold', type=int, default=10)
    parser.add_argument('--seed', type=int, default=0)
    parser.add_argument('--crawl_date', type=read_date, default='2013-08-01')
    args = parser.parse_args()

    random.seed(args.seed)

    data = load_data(args.json)
    data = filter(lambda d: has_progressed(90,
                                           read_date(d['published_date']),
                                           args.crawl_date), data)
    data = list(data)  # convert generator into list
    pos_data = filter(lambda d: d['report_count'] >= args.threshold, data)
    neg_data = filter(lambda d: d['report_count'] < args.threshold, data)

    logging.info('Size of pos data: {}'.format(len(pos_data)))
    logging.info('Size of neg data: {}'.format(len(neg_data)))

    for d in pos_data:
        d['label'] = 1
    for d in neg_data:
        d['label'] = 0

    random.shuffle(pos_data)
    random.shuffle(neg_data)

    train_ratio = 0.7
    dev_ratio = 0.2
    assert(train_ratio + dev_ratio < 1)

    pos_num_data = len(pos_data)
    neg_num_data = len(neg_data)

    pos_split1 = int(pos_num_data * train_ratio)
    pos_split2 = int(pos_num_data * (train_ratio + dev_ratio))
    neg_split1 = int(neg_num_data * train_ratio)
    neg_split2 = int(neg_num_data * (train_ratio + dev_ratio))

    train_data = pos_data[:pos_split1] + neg_data[:neg_split1]
    dev_data = pos_data[pos_split1:pos_split2] + neg_data[neg_split1:neg_split2]
    test_data = pos_data[pos_split2:] + neg_data[neg_split2:]

    def write_file(filename, data):
        with open(filename, 'w') as f:
            for d in data:
                f.write('{}\n'.format(json.dumps(d)))

    write_file(os.path.join(args.output_dir, 'train.json'), train_data)
    write_file(os.path.join(args.output_dir, 'dev.json'), dev_data)
    write_file(os.path.join(args.output_dir, 'test.json'), test_data)


if __name__ == '__main__':
    main()
