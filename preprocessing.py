#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import zenhan

SURROUNDS = (
    re.compile(ur'\(.*\)'),
    re.compile(ur'\（.*\）'),
    re.compile(ur'\[.*\]'),
)

UNCLOSED_PAREN = re.compile(ur"(\w+)\([^(]+", re.UNICODE)

STARTS_WITH_ALPHA = re.compile(ur"^[a-zA-Z][.:()（）\s]*([^a-zA-Z]+)")

SPLIT = re.compile(ur'or|OR|または|又は|/|\+|あれば')

OPTIONAL_START = re.compile(ur'^(好みの|お好みの|お好みにより|あれば|お好きの|お好きな)')

SPECIAL_SYMBOLS = (
    re.compile(ur'\*'),
    re.compile(ur'\u30fb'),
    re.compile(ur'[\u2000-\u206f]'),  # punctuation
    re.compile(ur'[\u2460-\u24ff]'),  # enclosed alphanumerics
    re.compile(ur'[\u2500-\u257f]'),  # box drawing
    re.compile(ur'[\u25a0-\u25ff]'),  # geometric shapes
    re.compile(ur'[\u2600-\u26ff]'),  # miscellaneous symbols
    re.compile(ur'[\u2700-\u27bf]'),  # dingbats
    re.compile(ur'[\u3000-\u303f]'),  # cjk symbols and punctuation
    re.compile(ur'[\uff00-\uffef]'),  # halfwidth and fullwdith forms
)

def make_function_hiragana():
    re_katakana = re.compile(ur'[ァ-ヴ]')
    def hiragana(text):
        """ひらがな変換"""
        return re_katakana.sub(lambda x: unichr(ord(x.group(0)) - 0x60), text)
    return hiragana
hiragana = make_function_hiragana()

def normalize(ingredient):
    ingredient = ingredient.strip()

    for SURROUND in SURROUNDS:
        ingredient = SURROUND.sub(lambda s: '', ingredient)

    ingredient = OPTIONAL_START.sub(lambda s: '', ingredient)

    match = UNCLOSED_PAREN.match(ingredient)
    if match:
        ingredient = match.groups()[0]

    ingredient = zenhan.h2z(ingredient, mode=4)  # only deal with katakana

    # convert all katakana to hiragana
    ingredient = hiragana(ingredient)

    match = STARTS_WITH_ALPHA.match(ingredient)
    if match and not ingredient.startswith('S&B'):
        ingredient = match.groups()[0]

    for SPECIAL_SYMBOL in SPECIAL_SYMBOLS:
        ingredient = SPECIAL_SYMBOL.sub(lambda s: '', ingredient)

    ingredients = map(lambda ingr: ingr.strip(), SPLIT.split(ingredient))
    for ingredient in ingredients:
        if not ingredient:
            continue
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
        u'スィートチリソース（今回はID：1384495 を使いました。）',
        u'梅干し(ほぐして種ごと',
        u'あればローリエ',
        u'お好きな葉野菜',
        u'酒あれば泡盛',
    ]

    for ingredient in ingredients:
        for normalized_ingredient in normalize(ingredient):
            print normalized_ingredient.encode('utf8')
