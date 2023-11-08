import json
import argparse

from read_work_write_json_keys import read_work_write

standard_keys = ["md5", "keep", "filters", "lang", "len_char", "len_utf8bytes", "len_words", "len_sents", "text"]


def fix_line(line: str) -> str:
    obj = json.loads(line)
    # Remove all non-standard json keys
    obj = {
        k: obj[k] for k in standard_keys
    }

    return json.dumps(obj, ensure_ascii=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_file', type=str, default=None,
                        help='Input file')
    parser.add_argument('--output_file', type=str, default=None,
                        help='Output file')
    args = parser.parse_args()

    read_work_write(args.input_file, args.output_file, fix_line)
