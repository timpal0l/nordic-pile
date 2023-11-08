import json
import random

# REMOVED_FILE = "data/out_file_removed.jsonl"
REMOVED_FILE = "../data/out_file.jsonl"
# NUM_SAMPLES = 10000
NUM_SAMPLES = 1000000000

filters = ["mean_line_len"]
# filters = ["stop_word"]
# filters = ["supported_language"]
# filters = []
filter_alone = True


def main():
    with open(REMOVED_FILE, 'r') as f:
        json_lines = f.readlines()

    random.shuffle(json_lines)
    n = min(NUM_SAMPLES, len(json_lines))
    samples_found = 0
    for line in json_lines[:n]:

        json_obj = json.loads(line)
        current_filters = json_obj["filters"]

        if len(filters) > 0:
            found_filter = False
            for f in filters:
                if f in current_filters:
                    found_filter = True
                    break
            if not found_filter:
                continue

            if filter_alone and len(current_filters) > 1:
                continue
        else:
            if len(current_filters) > 0:
                continue

        # if len(json_obj["text"]) < 150:
        #     continue
        samples_found += 1
        print("*" * 50)
        print("Hash:", json_obj["md5"])
        print("Filters:", json_obj["filters"])
        print(json_obj["text"])
        print()

    print("#Samples found:", samples_found)


if __name__ == '__main__':
    random.seed(1234)
    main()
