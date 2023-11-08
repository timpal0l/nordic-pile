from glob import glob
import random
import os
from tqdm import tqdm
import shutil
import zstandard
import json
import io

import sys
import math

import matplotlib.pyplot as plt
import numpy as np
import collections
from datetime import date


def readf(f):
    with open(f, 'rb') as fh:
        cctx = zstandard.ZstdDecompressor()
        reader = io.BufferedReader(cctx.stream_reader(fh))
        yield from reader

def rewrite_name(n):
    if n in rewritenames: return rewritenames[n]

    return n

def mean(x):
    return sum(x) / len(x)

def stddev(x):
    mu = mean(x)
    return math.sqrt(mean([(v - mu) ** 2 for v in x]))

def freqs(x):
    ret = collections.defaultdict(int)
    for v in x:
        ret[v] += 1
    
    return ret

def filter_freqs(x, minpass):
    total = sum(x.values())
    torm = []
    for k, v in x.items():
        if v / total < minpass:
            torm.append(k)
    
    for k in torm: del x[k]

    return x


def histogram(x, sname, attr):
    plt.clf()
    plt.cla()
    plt.hist(x, density=True, bins=100) 
    #plt.ylabel('Probability Density')
    plt.xlabel('{} ({})'.format(nicename[attr], sname))
    plt.savefig('figures/analysis_{}_{}.png'.format(sname, attr),bbox_inches='tight')


def barplot(d, sname, attr, normalize=True, yerr=False):
    x, y = zip(*sorted(d.items(), key=lambda x: x[1], reverse=True))
    yerrs = None
    if yerr:
        yerrs = [v[1] for v in y]
        y = [v[0] for v in y]
    if normalize:
        total = sum(d.values())
        y = [val / total for val in y]
    plt.clf()
    plt.cla()
    if yerr:
        plt.errorbar(x, y, yerr=yerrs, fmt='o')
        plt.xticks(rotation=45, ha="right")

        #ymin = None
        #ymax = None

        #if attr == 'len_char':
        #    ymin, ymax = -30000, 1200000
        #if attr == 'len_tokens':
        #    ymin, ymax = -30000, 300000
        #if attr == 'len_utf8bytes':
        #    ymin, ymax = -30000, 1200000
        #if ymin and ymax:
        #    axes = plt.gca()
        #    axes.set_ylim([ymin,ymax])
    else:
        plt.bar(x, y) 
    #plt.ylabel('Proportion')
#    plt.xlabel('{} ({})'.format(nicename[attr], sname))
    plt.xlabel('Pile component')
    plt.ylabel(nicename[attr])
    plt.savefig('figures/analysis_{}_{}.png'.format(sname, attr),bbox_inches='tight', dpi=600)


def format_freqs(d):
    res = []
    total = sum(d.values())
    for k,v in sorted(d.items(), key=lambda x: -x[1]):
        res.append('  {}: {:2f}%'.format(k, v / total * 100))
    return '\n'.join(res)


def rm_outliers_trunc_1p(x):
    x = list(sorted(x))
    return x[:len(x)*99//100]

if __name__ == '__main__':
    dat = collections.defaultdict(list)
    set_names = set()

    rewritenames = {
        'CommonCrawl': 'Pile-CC',
        'Bibliotik': 'Books3',
        'USPTO': 'USPTO Backgrounds',
        'BookCorpus': 'BookCorpus2',
    }

    for f in tqdm(glob('langlen_stage1/*')[:1]):
        # forgot to add \n in stage1 >.>
        for x in map(lambda x: x + b'}', (list(next(readf(f)).split(b'}'))[:-1])):
            ob = json.loads(x)
            setname = "Oscar" #rewrite_name(ob['pile_set_name'])
            # print(ob)
            for attr in ['len_char', 'len_utf8bytes', 'len_words', 'len_tokens', 'lang']:
                dat[(setname, attr)].append(ob[attr])
                dat[('Pile', attr)].append(ob[attr])
                set_names.add(setname)

            if ob['len_tokens'] > 0:
                dat[(setname, 'bytes_per_token')].append(ob['len_utf8bytes'] / ob['len_tokens'])
                dat[('Pile', 'bytes_per_token')].append(ob['len_utf8bytes'] / ob['len_tokens'])

                dat[(setname, 'words_per_token')].append(ob['len_words'] / ob['len_tokens'])
                dat[('Pile', 'words_per_token')].append(ob['len_words'] / ob['len_tokens'])

    set_names = list(set_names)
    set_names.append('Pile')

    nicename = {
        'len_char': 'Length in characters',
        'len_utf8bytes': 'Length in bytes',
        'len_words': 'Length in words',
        'len_tokens': 'Length in tokens',
        "amount_sentences": "Number of sentences",
        'bytes_per_token': 'Mean bytes per token',
        'words_per_token': 'Mean words per token',
        'lang': 'Language'
    }

    summary = collections.defaultdict(dict)

    f = open('statistics_'+str(date.today()),'w')
    f.write('bytes per token, all:', sum(dat[('Pile', 'len_utf8bytes')]) / sum(dat[('Pile', 'len_tokens')]))

    for sname in set_names:
        f.write('**' + sname + '**')
        for attr in ['len_char', 'len_utf8bytes', 'len_words', 'len_tokens', 'bytes_per_token', 'words_per_token']:
            mu, sigma = mean(dat[(sname,attr)]), stddev(dat[(sname,attr)])
            f.write('{}: {:.4f}±{:.4f}'.format(nicename[attr], mu, sigma))
            histogram(rm_outliers_trunc_1p(dat[(sname,attr)]), sname, attr)
            if sname != 'Pile' and (sname != 'Ubuntu IRC' or 'len_' not in attr): summary[attr][sname] = (mu, sigma)

        barplot(filter_freqs(freqs(dat[(sname,'lang')]), 0.001), sname, 'lang')

        f.write('Langs:')
        f.write(format_freqs(freqs(dat[(sname, 'lang')])))


    for attr in ['len_char', 'len_utf8bytes', 'len_words', 'len_tokens', 'bytes_per_token', 'words_per_token']:
        barplot(summary[attr], 'overview', attr, normalize=False, yerr=True)
