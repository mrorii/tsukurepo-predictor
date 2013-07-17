#!/usr/bin/env python

import argparse
import json

import pylab as pl

def load_data(filename):
    with open(filename, 'r') as f:
        for line in f:
            yield json.loads(line.strip())

def main():
    parser = argparse.ArgumentParser(description='Inspect report count distribution')
    parser.add_argument('json', help='Input data file')
    parser.add_argument('png', help='Output histogram plot file')
    parser.add_argument('--xmax', help='Max x', type=int, default=200)
    args = parser.parse_args()

    report_counts = map(lambda d: d['report_count'], load_data(args.json))
    n, bins, patches = pl.hist(report_counts, bins=100, range=(0, args.xmax))
    pl.savefig(args.png)

if __name__ == '__main__':
    main()
