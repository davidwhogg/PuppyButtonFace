#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

__all__ = []

import re
import nltk
import redis
import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool
from nltk.tokenize import PunktSentenceTokenizer


tokenizer = PunktSentenceTokenizer()
stripper = re.compile(r"^[a-zA-Z]")

redis_pool = redis.ConnectionPool()


def run_one(*args):
    # Redis setup.
    rdb = redis.Redis(connection_pool=redis_pool)
    pipe = rdb.pipeline(transaction=False)

    # Download a random article.
    url = "http://en.wikipedia.org/wiki/Special:Random"
    r = requests.get(url)
    if r.status_code != requests.codes.ok:
        print("Returned {0}. Re-trying".format(r.status_code))
        return run_one()
    print(r.url)

    # Parse and walk the document.
    tree = BeautifulSoup(r.text)
    for el in tree.find(id="mw-content-text").find_all("p"):
        for s in tokenizer.tokenize(el.text):
            for t in nltk.pos_tag(nltk.word_tokenize(s)):
                if t[1][0] == "N" and t[1][-1] != "P":
                    w = re.sub(r"[0-9,.;?\[\]\(\)]", "", t[0].lower())
                    if len(w) > 2:
                        pipe.zincrby("puppy:words", w, 1)
    pipe.execute()


if __name__ == "__main__":
    pool = Pool()
    for i in range(1024):
        pool.map(run_one, range(128 * pool._processes))
