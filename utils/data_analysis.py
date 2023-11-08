# This file is not clean and has been used as a scratch pad for visualizing dataset statistics

import json
import random
import re
from collections import Counter
import seaborn as sns
import matplotlib.pyplot as plt

import numpy as np

plt.style.use('ggplot')
plt.style.use('seaborn-dark-palette')
plt.rcParams["figure.figsize"] = (18, 10)
cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']

NUM_SAMPLES = 50000

langs = ["da", "en", "is", "no", "sv"]

colors = {
    lang: cycle[idx] for idx, lang in enumerate(langs)
}


def plot_hist(data_dict, title, min_val, max_val):

    plt.title(title)

    for lang in langs:
        label = lang
        color = colors[lang]
        data = data_dict[lang]
        data = [dl for dl in data if min_val <= dl <= max_val]
        sns.kdeplot(data, label=label, color=color, alpha=0.8)
        plt.axvline(np.mean(data), label=label + "_mean", color=color, alpha=0.5, linestyle="--")

    plt.xlim(min_val, max_val)
    plt.legend()
    plt.show()


def main():
    data_dir = "data/wiki/"

    doc_lens_dict = {}
    mean_word_lens_dict = {}
    for lang in langs:
        file_name = f"wiki_{lang}.jsonl"
        file_path = data_dir + file_name
        with open(file_path, 'r') as f:
            lines = f.readlines()

        random.shuffle(lines)

        assert len(lines) >= NUM_SAMPLES

        texts = [json.loads(line)["text"] for line in lines[:NUM_SAMPLES]]
        doc_lens = []
        mean_word_lens = []
        word_counter = Counter()
        for t in texts:
            t = t.lower()
            word_split = [x for x in re.split(r'\s+', t) if x]
            if len(word_split) == 0:
                continue

            doc_lens.append(len(word_split))

            word_lens = [len(w) for w in word_split]
            mean_word_lens.append(np.mean(word_lens))

            word_counter.update(word_split)

        doc_lens_dict[lang] = doc_lens
        mean_word_lens_dict[lang] = mean_word_lens
        print(word_counter.most_common(10))

    plot_hist(mean_word_lens_dict, "mean_word_len", 0, 15)


def single_file():
    file_path = "/home/joey/code/ai/data_analysis_base_pile/data/mc410_sv_subset.jsonl"
    with open(file_path, 'r') as f:
        lines = f.readlines()

    random.shuffle(lines)

    texts = [json.loads(line)["text"] for line in lines[:NUM_SAMPLES]]
    doc_lens = []
    mean_word_lens = []
    word_counter = Counter()
    for t in texts:
        t = t.lower()
        word_split = [x for x in re.split(r'\s+', t) if x]
        if len(word_split) == 0:
            continue

        doc_lens.append(len(word_split))

        word_lens = [len(w) for w in word_split]
        mean_word_lens.append(np.mean(word_lens))

        word_counter.update(word_split)

    print(word_counter.most_common(10))

    plt.title("mean_word_len")

    min_val, max_val = 0, 15
    label = "mc4_sv"
    # data = doc_lens
    data = mean_word_lens
    data = [dl for dl in data if min_val <= dl <= max_val]
    sns.kdeplot(data, label=label, color=colors["sv"], alpha=0.8)
    plt.axvline(np.mean(data), label=label + "_mean", color=colors["sv"], alpha=0.5, linestyle="--")

    plt.xlim(min_val, max_val)
    plt.legend()
    plt.show()


if __name__ == '__main__':
    random.seed(42)
    # in_file = sys.argv[1]
    main()
    # single_file()

