import json
import random
from collections import defaultdict
from typing import List
from pathlib import Path


# TODO: paths won't work for generating subset files again without updating paths to old ones
IN_FILES = [
    "/data/nordic_pile/jsonl_train_format/original/web_sources/wiki/wiki_en.jsonl"
    "/home/joey/data/mixed/oscarv310_sv.jsonl",
    "/home/joey/data/mixed/conversations_sv_subset.jsonl",
    "/home/joey/data/mixed/1177.jsonl",
    "/home/joey/data/mixed/tradera.jsonl",
    "/home/joey/data/mixed/litteraturbanken.jsonl",
    "/home/severine/mix_mc4.jsonl",
]

OUT_DIR = "/home/joey/data/mixed/subset/"

CLEANED_DIR = "/home/joey/data/mixed/cleaned/"

# FILTER_NAMES = ["doc_length", "mean_word_length", "supported_language", "blacklist_urls", "alpha_present",
#                 "hashtag_to_word_ratio", "ellipsis_to_word_ratio", "stop_word", "initial_bullet_points", ""]


def main():
    # with open("mixed_dataset.jsonl", 'w') as f_out:
    for in_file in IN_FILES:
        print("File:", in_file)
        file_name = in_file.split("/")[-1]

        with open(in_file, 'r') as f_in:
            ##
            # lines = []
            # for idx, line in enumerate(f_in):
            #     lines.append(line)
            #     if idx == 200000:
            #         break
            ##
            lines = f_in.readlines()

        random.shuffle(lines)

        with open(OUT_DIR + file_name, 'w') as f_out:
            n = 20000 if file_name != "litteraturbanken.jsonl" else 500
            for line in lines[:n]:
                obj = json.loads(line)
                obj["dataset"] = file_name
                f_out.write(json.dumps(obj, ensure_ascii=False) + "\n")


def visualize_results():
    files = [path for path in Path(CLEANED_DIR).rglob('*.jsonl')]
    # files = [CLEANED_DIR + fn.split("/")[-1] for fn in IN_FILES]
    lines = []
    for file_path in files:
        with open(file_path, 'r') as f:
            lines += f.readlines()

    random.shuffle(lines)

    filter_sample_dict = defaultdict(list)

    for line in lines:
        obj = json.loads(line)
        if len(obj["text"].strip(" \n")) == 0:
            continue
        filters = obj['filters']
        if len(filters) == 0:
            filter_sample_dict["clean"].append(obj)
        else:
            for f in filters:
                filter_sample_dict[f].append(obj)
            if len(filters) == 1:
                filter_sample_dict[f + " solo"].append(obj)

    filter_name_prev = "clean"
    while True:
        filter_name = input("\nFilter (empty for same query as previous sample): ").strip(" \n")
        # space_split = filter_name.split()
        # filter_name = space_split[0]
        # if len(space_split) > 1 and space_split[1] == "solo":

        if len(filter_name) == 0:
            filter_name = filter_name_prev
            # obj: List[dict] = random.choice(filter_sample_dict["clean"])

        filter_name_prev = filter_name
        if filter_name not in filter_sample_dict:
            print(f"Filter name \"{filter_name}\" is not present in samples!")
            continue

        curr_list = filter_sample_dict[filter_name]
        if len(curr_list) == 0:
            print(f"No samples left in filter list {filter_name}")
            continue
        obj: List[dict] = random.choice(curr_list)
        curr_list.remove(obj)

        text = obj["text"][:10000]
        text = "\n".join(text.split("\n")[:70])

        other_fields = ", ".join([f"{k}: {v}" for k, v in obj.items() if k not in ["text", "dataset"]])
        print("*" * 100)
        # print(f"Keep: {obj['keep']}, Filters: {obj['filters']}, Dataset: {obj['dataset']}, md5: {obj['md5']}"
        #       f", url: {obj['url'] if 'url' in obj else ''}")
        print("Dataset:", obj['dataset'])
        print(other_fields)
        print("-" * 75)
        print("text:")
        print(text)
        if len(obj["text"]) > len(text):
            print(". . . (Truncated Print)")
        print()
        print()
        print("*" * 50)


if __name__ == '__main__':
    random.seed(42)
    # main()
    visualize_results()
