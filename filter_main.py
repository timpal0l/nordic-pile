import argparse
import datetime
import json
import time
from typing import Tuple, List
from best_download import download_file
import os

import yaml
from tabulate import tabulate

import url_handler
from Document import Document
from read_work_write_parallel import read_work_write

# SETUP THIS FROM FILE, READONLY AFTER THAT! =)
CONFIG_DICT = {}
FILTER_FUNC_NAMES = []


# Mapping from directory/file to config file. These are set up on the rise ice server
CONFIG_MAP = {
    "web_commoncrawl": "web_commoncrawl.yaml",
    "web_sources": "web_sources.yaml",
    "conversational": "conversational.yaml",
    "books": "books.yaml",
    "code": "code.yaml",
    "ncc": "ncc.yaml",
    "math": "math.yaml",
    "stackexchange": "stackexchange.yaml",
    "natural_instructions": "natural_instructions.yaml",
    "isgw": "books.yaml",
    "dn_summarization": "books.yaml",
    "movie_scripts": "books.yaml",
    "p3": "natural_instructions.yaml",
    "pile_arxiv.jsonl": "stackexchange.yaml",
    "pile_pubmed_central": "pubmed_central.yaml"
}

standard_doc_keys = ["md5", "keep", "filters", "lang", "len_char", "len_utf8bytes", "len_words", "len_sents", "text"]


def print_filter_statistics(docs_total, kept_count, counter_dict):
    """
    Prints statistics table from the filtering process

    :param docs_total: Total number of lines/documents seen
    :param kept_count: Number of documents kept (i.e. not removed)
    :param counter_dict: The dictionary counting how many documents each filter removed
    """

    counter_tuples = list(counter_dict.items())
    counter_tuples = sorted(counter_tuples, key=lambda x: x[0])
    # docs_total = sum(count for idx, count in counter_tuples)
    filter_counters = [0] * len(FILTER_FUNC_NAMES)  # An extra for documents kept
    for filter_idx, counter in counter_tuples:
        filter_counters[filter_idx] += counter

    filter_counters.append(kept_count)
    filter_counters.append(docs_total)

    names = FILTER_FUNC_NAMES.copy()
    names.append("*Kept")
    names.append("*Total")

    table = tabulate(list(zip(names, filter_counters)), headers=['Filter', '#Docs'], tablefmt='orgtbl')
    print("\n" + table + "\n")


def processing_func(json_line: str) -> Tuple[str, List[int]]:
    """
    Parses the json line, creates a Document class, filter & metrics

    :param json_line: the read json line
    :return: (processed json line, filter indices that removes the document)
    """
    json_dict = json.loads(json_line[1].strip())

    # json_dict["filename"] = json_line[0]

    doc = Document(FILTER_FUNC_NAMES, json_dict)
    keep_doc, filter_indices = doc.filter_doc()

    json_doc = doc.compute_and_add_metrics()

    # Remove all non-standard json keys, and set consistent ordering of keys
    json_doc = {
        k: json_doc[k] for k in standard_doc_keys
    }

    return json.dumps(json_doc, ensure_ascii=False), filter_indices


def main(args) -> None:
    """
    Main driver function of this repository:
    Initializes structures needed, loads & parses config, filters documents, and prints statistics.

    :param args: args object from argparse
    """
    # Load url blacklist files and initialize its global variables/regex
    url_handler.init()

    # Parse config and decide filter function names
    global CONFIG_DICT, FILTER_FUNC_NAMES
    if args.config_file is None:
        assert args.config_dir_path is not None, "Neither config_file nor config_dir_path is present"
        config_path_base = args.config_dir_path

        for key in CONFIG_MAP:
            if key in args.in_file:
                config_path = config_path_base + "/" + CONFIG_MAP[key]
                break
    else:
        config_path = args.config_file

    assert config_path is not None, "No config found in mapping for this file"

    print("Loading filter config from:", config_path)

    with open(config_path, 'r') as f:
        CONFIG_DICT = yaml.safe_load(f)

    filters = list(CONFIG_DICT["filters"].items())
    active_filters = [f for f, active in filters if active and f != "empty"]
    FILTER_FUNC_NAMES = ["empty"] + active_filters
    print(f"Filter pipeline to apply on documents:")
    for i, filter_name in enumerate(FILTER_FUNC_NAMES):
        print(f"{i + 1}. {filter_name}")
    print()

    # Do all work
    doc_count, kept_count, filter_counters = read_work_write(args.in_file, args.out_file, processing_func, args.num_workers)

    # Print resulting statistics
    print_filter_statistics(doc_count, kept_count, filter_counters)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--in_file', type=str, default=None,
                        help='Input .jsonl file')
    parser.add_argument('--out_file', type=str, default=None,
                        help='Output .jsonl file')
    parser.add_argument('--config_file', type=str, default=None,
                        help='Config yaml file, path to specific file. Only used for single-file cleaning')
    parser.add_argument('--config_dir_path', type=str, default=None,
                        help='Config yaml files directory, used when cleaning entire directory tree')
    parser.add_argument('--num_workers', type=int, default=1,
                        help='Number of CPU workers to use for data processing. You should probably leave a couple of '
                             'threads for I/O. E.g. use 14 workers with 16 CPU threads')
    in_args = parser.parse_args()

    time_started = time.time()

    if not os.path.isfile("lid.176.bin"):
        print("Downloading fasttext language detection model: lid.176.bin")
        download_file('https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin',
                      expected_checksum='7e69ec5451bc261cc7844e49e4792a85d7f09c06789ec800fc4a44aec362764e',
                      local_file='lid.176.bin', )

    main(in_args)
    seconds_elapsed = round(time.time() - time_started)
    print(f"Time Elapsed: {str(datetime.timedelta(seconds=seconds_elapsed))}")
