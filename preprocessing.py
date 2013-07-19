#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import zenhan

SURROUNDS = (
    re.compile(ur'\(.*\)', re.UNICODE),
    re.compile(ur'\（.*\）', re.UNICODE),
    re.compile(ur'\[.*\]', re.UNICODE),
)

STARTS_WITH_ALPHA = re.compile(ur"^[a-zA-Z][.:()（）\s]*([^a-zA-Z]+)")  # do NOT use UNICODE

SPLIT = re.compile(ur'or|OR|または|又は|/')

OPTIONAL = re.compile(ur'好みの|お好みの|お好みにより')

SPECIAL_SYMBOLS = (
    re.compile(ur'\*', re.UNICODE),
    re.compile(ur'\u30fb', re.UNICODE),
    re.compile(ur'[\u2000-\u206f]', re.UNICODE),  # punctuation
    re.compile(ur'[\u2460-\u24ff]', re.UNICODE),  # enclosed alphanumerics
    re.compile(ur'[\u2500-\u257f]', re.UNICODE),  # box drawing
    re.compile(ur'[\u25a0-\u25ff]', re.UNICODE),  # geometric shapes
    re.compile(ur'[\u2600-\u26ff]', re.UNICODE),  # miscellaneous symbols
    re.compile(ur'[\u2700-\u27bf]', re.UNICODE),  # dingbats
    re.compile(ur'[\u3000-\u303f]', re.UNICODE),  # cjk symbols and punctuation
    re.compile(ur'[\uff00-\uffef]', re.UNICODE),  # halfwidth and fullwdith forms
)

def normalize(ingredient):
    ingredient = ingredient.strip()

    for SURROUND in SURROUNDS:
        ingredient = SURROUND.sub(lambda s: '', ingredient)

    ingredient = zenhan.h2z(ingredient, mode=4)  # only deal with katakana

    match = STARTS_WITH_ALPHA.match(ingredient)
    if match and not ingrient.startswith('S&B'):
        ingredient = match.groups()[0]

    for SPECIAL_SYMBOL in SPECIAL_SYMBOLS:
        ingredient = SPECIAL_SYMBOL.sub(lambda s: '', ingredient)

    ingredients = map(lambda ingr: ingr.strip(), SPLIT.split(ingredient))
    for ingredient in ingredients:
        yield ingredient

if __name__ == '__main__':
    ingredients = [
        u'a醤油',
        u'Bごま油',
        u'A 塩',
        u'A.醤油',
        u'A)片栗粉',
        u'里芋(冷凍もの可',
        u'ケチャップ+ソース+醤油',
        u'(じゃこ白胡麻海苔',
        u'EXオリーブオイル',
    ]
