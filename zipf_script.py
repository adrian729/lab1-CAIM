"""
.. module:: CountWords

CountWords
*************

:Description: CountWords

    Generates a list with the counts and the words in the 'text' field of the documents  in an index

:Authors: bejar


:Version:

:Created on: 04/07/2017 11:58

"""

from __future__ import print_function
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
from elasticsearch.exceptions import NotFoundError
from scipy.optimize import curve_fit

import argparse
import bisect
import math
import numpy as np
import matplotlib.pyplot as plt

"""
-zipf_script:
CountWords modified by Adrián Sánchez Albanell
"""
__author__ = 'bejar, Adr'


def rem_bad_chars(word):
    """
    Returns the word without bad characters.
    :param word:
    :return:
    """
    bad_chars = "\\&|`'\"*_{}[]()>#+-.,;:!$0123456789"
    for c in bad_chars:
        if c in word:
            word = word.replace(c, '')
    return word


def void_uwords(word):
    """
    Returns and empty string if the word is an article.
    :param word:
    :return:
    """
    uwords = []
    if word in uwords:
        return ''
    return word


def func(x, a, b, c):
    return c / (x + b) ** a


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--index', default=None, required=True, help='Index to search')
    parser.add_argument('--alpha', action='store_true', default=False, help='Sort words alphabetically')
    args = parser.parse_args()

    index = args.index

    try:
        client = Elasticsearch()
        voc = {}
        sc = scan(client, index=index, doc_type='document', query={"query": {"match_all": {}}})

        for s in sc:
            tv = client.termvectors(index=index, doc_type='document', id=s['_id'], fields=['text'])
            if 'text' in tv['term_vectors']:
                for t in tv['term_vectors']['text']['terms']:
                    parsed_t = rem_bad_chars(t)
                    if len(parsed_t) > 1:
                        if parsed_t in voc:
                            voc[parsed_t] += tv['term_vectors']['text']['terms'][t]['term_freq']
                        else:
                            voc[parsed_t] = tv['term_vectors']['text']['terms'][t]['term_freq']

        lpal = []
        fwl = []
        for v in voc:
            lpal.append((v.encode("utf8", "ignore"), voc[v]))
            bisect.insort(fwl, voc[v])
        fwl.reverse()

        first_words = math.floor(len(fwl) * 0.005)
        print('Removed first %d words' % first_words)
        del fwl[:first_words]

        xdata = xdata = np.linspace(0, len(fwl), len(fwl))
        ydata = fwl
        plt.plot(xdata, ydata, 'b-', label='data')

        # Fit for the parameters a, b, c of the function func
        popt, pcov = curve_fit(func, xdata, ydata)
        plt.plot(xdata, func(xdata, *popt), 'r-', label='fit')

        print("[a, b, c]", popt)

        plt.xlabel('x')
        plt.ylabel('y')
        plt.legend()
        plt.show()

        # print(fwl)
        # print(len(fwl))
        # print(len(lpal))
        #
        # plt.plot(fwl)
        # plt.ylabel('memememe')
        # plt.show()
        # for pal, cnt in sorted(lpal, key=lambda x: x[0 if args.alpha else 1]):
        #     print('%d, %s' % (cnt, pal))
        # print('%s Words' % len(lpal))
    except NotFoundError:
        print('Index %s does not exists' % index)
