#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function

import re
import requests
from collections import Counter
from multiprocessing import Pool

from bs4 import BeautifulSoup

import nltk
from nltk.tokenize import PunktSentenceTokenizer

__all__ = []


tokenizer = PunktSentenceTokenizer()
stripper = re.compile(r"^[a-zA-Z]")


def run_one(*args):
    # Download a random article.
    url = "http://en.wikipedia.org/wiki/Special:Random"
    r = requests.get(url)
    if r.status_code != requests.codes.ok:
        print("Returned {0}. Re-trying".format(r.status_code))
        return run_one()
    print(r.url)

    # Parse and walk the document.
    tree = BeautifulSoup(r.text, "lxml")
    words = []
    for el in tree.find(id="mw-content-text").find_all("p"):
        for s in tokenizer.tokenize(el.text):
            for t in nltk.pos_tag(nltk.word_tokenize(s)):
                if t[1][0] == "N" and t[1][-1] != "P":
                    w = re.sub(r"[0-9,.;?\[\]\(\)]", "", t[0].lower())
                    if len(w) > 2:
                        words.append(w)

    return r.url, Counter(words)


if __name__ == "__main__":
    fn = "words.txt"
    counter = Counter()
    pool = Pool()
    for i in range(1024):
        for c in pool.map(run_one, range(128 * pool._processes)):
            counter.update(c)
        with open(fn, "w") as f:
            f.write("\n".join(counter.most_common(2048)))
