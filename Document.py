import hashlib
import re
import unicodedata
from typing import List, Tuple
import sys
import json

import numpy as np

import read_work_write_parallel
import normalization
from help_filter import alpha_present, stop_word_help
from repetitive_filter import repetitive_filter
from smutdetector import is_smut
from url_handler import url_is_accepted
from repetitive_filter_bsp import repetitive_filter_bsp

BULLET_POINT = [">", "-", "•"]


class Document:

    def __init__(self, filter_funcs: List[str], json_doc: dict):
        self.filter_funcs = filter_funcs
        self.json_doc = json_doc
        self.json_doc["filters"] = []

        self.language_detector = read_work_write_parallel.lang_det
        # self.tokenizer = read_work_write_parallel.tokenizer

        self.word_split = None
        self.language = None
        self.non_empty_lines = None

        self._preprocess_doc()
        self._precompute_data()

    def _preprocess_doc(self) -> None:
        """
        Preprocesses the text field of the json document to a standard format:
        1. Remove non-printing characters
        2. Normalize whitespaces
        3. NFC Unicode normalization
        """
        if self.json_doc["text"] is None:  # Add an empty string if the object in the text field is None
            self.json_doc["text"] = ""

        # False in default parameters
        self.json_doc["text"] = normalization.remove_non_printing_characters(self.json_doc["text"])
        self.json_doc["text"] = normalization.uniform_whitespace(self.json_doc["text"])

        # False in default parameters
        # self.json_doc["text"] = normalization.replace_unicode_punctuation(self.json_doc["text"])
        self.json_doc["text"] = unicodedata.normalize("NFC", self.json_doc["text"])

    def _precompute_data(self) -> None:
        """
        Precomputes data needed for filters/metrics and saves to class properties.
        """
        self.word_split = [x for x in re.split(r'\s+', self.json_doc["text"]) if x]

        lid_input = self.json_doc["text"].lower().replace('\n', ' ')
        self.language = self.language_detector.predict(lid_input, k=1)[0][0].replace('__label__', '')

        self.non_empty_lines = [line.strip() for line in self.json_doc["text"].splitlines() if len(line.strip()) > 0]

    def compute_and_add_metrics(self) -> dict:
        """
        Computes metrics and adds them to the json document in-place as new fields
        :return: New dict with these fields added
        """
        self.json_doc["len_char"] = len(self.json_doc["text"])
        self.json_doc["len_utf8bytes"] = len(self.json_doc["text"].encode("utf-8"))
        self.json_doc["len_words"] = len(self.word_split)
        self.json_doc["len_sents"] = len(re.split("(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s", self.json_doc["text"]))
        self.json_doc["lang"] = self.language
        self.json_doc["md5"] = hashlib.md5(self.json_doc["text"].encode("utf8")).hexdigest()
        return self.json_doc

    def filter_doc(self) -> Tuple[bool, List[int]]:
        """
        Iterates over all given filter function names and check whether this document should be kept.

        :return: True if doc should be kept, else False
        :return: List of filter indices that removes the document
        """

        keep = True
        filters_that_remove = []

        # Check if empty first, so it doesn't crash other filters
        if (not self.empty()) or len(self.word_split) == 0:
            # Empty document
            keep = False
            self.json_doc["filters"].append(self.filter_funcs[0])
            filters_that_remove.append(0)

        else:
            for idx, filter_func_name in enumerate(self.filter_funcs):
                if idx == 0:  # Skip empty as we do it manually
                    continue
                # Assume all filters fail when a document is shorter than 5 characters (avoid crashes)
                if len(self.json_doc["text"]) < 5:
                    self.json_doc["filters"].append(self.filter_funcs[idx])
                    keep = False
                    filters_that_remove.append(idx)
                    continue

                doc_meets_condition = getattr(self, filter_func_name)()
                if not doc_meets_condition:
                    self.json_doc["filters"].append(self.filter_funcs[idx])
                    keep = False
                    filters_that_remove.append(idx)

        self.json_doc["keep"] = 1 if keep else 0
        return keep, filters_that_remove

    def empty(self) -> bool:
        return len(self.json_doc["text"]) >= 5

    def supported_language(self) -> bool:
        return self.language in ["en", "no", "da", "sv", "nn", "is", "fo"]  # ToDo do we add faroese? And nb?

    def blacklist_urls(self) -> bool:
        url = self.json_doc.get("url", None)
        if url is None:
            return True
        else:
            return url_is_accepted(url)

    def doc_length(self) -> bool:
        # return len(self.word_split) >= 40  # TODO: Upper limit?
        return len(self.json_doc["text"]) >= 50  # TODO: Upper limit?

    def mean_word_length(self) -> bool:
        # Average number of characters per word must be in this range
        mean_word_len = np.mean([len(w) for w in self.word_split])
        return 2 <= mean_word_len <= 10

    def mean_line_len(self) -> bool:
        mean_line_len_chars = float(np.mean([len(line) for line in self.non_empty_lines]))
        median_line_len_chars = float(np.median([len(line) for line in self.non_empty_lines]))
        mean_chars = (mean_line_len_chars + median_line_len_chars) / 2
        if mean_chars < 10:
            return False

        mean_line_len_words = float(np.mean([len(line.split()) for line in self.non_empty_lines]))
        median_line_len_words = float(np.median([len(line.split()) for line in self.non_empty_lines]))
        mean_words = (mean_line_len_words + median_line_len_words) / 2
        if mean_words < 2.1:
            return False

        return True

    def stop_word(self) -> bool:
        # Remove documents with less than 2 common stop words
        return stop_word_help(self.word_split)

    def alpha_present(self) -> bool:
        # 80% of words in a document contain at least one alphabetic character
        return alpha_present(self.word_split)

    def digit_fraction(self) -> bool:
        # Remove any document with a digit-to-character ratio greater than 0.2
        num_digits = sum([1 for c in self.json_doc["text"] if c.isdigit()])
        if num_digits / len(self.json_doc["text"]) > 0.2:
            return False

        return True

    def hashtag_to_word_ratio(self) -> bool:
        # Remove any document with a symbol-to-word ratio greater than 0.1 for the hash symbol
        return self.json_doc["text"].count("#") / len(self.word_split) <= 0.1

    def ellipsis_to_word_ratio(self) -> bool:
        # Remove any document with a symbol-to-word ratio greater than 0.1 for the ellipsis
        return self.json_doc["text"].count("…") / len(self.word_split) <= 0.1

    def initial_bullet_points(self) -> bool:
        # Remove any document with more than 90% of lines starting with a bullet point
        # Joey: Added constraint of having at least 3 initial bullet points
        num_initial_bullet_points = sum([1 for line in self.non_empty_lines if line[0] in BULLET_POINT])
        return num_initial_bullet_points < 3 or num_initial_bullet_points / len(self.non_empty_lines) <= 0.9

    def ending_ellipsis(self) -> bool:
        # Remove any document with more than 30% of lines ending with an ellipsis.
        # Joey: Added constraint of having at least 3 ending ellipsis
        num_ending_with_ellipsis = sum([1 for line in self.non_empty_lines if line[-1:] == "…"])
        return num_ending_with_ellipsis < 3 or num_ending_with_ellipsis / len(self.non_empty_lines) <= 0.3

    def repetitive(self) -> bool:
        return repetitive_filter(self.json_doc["text"], self.word_split, self.non_empty_lines)

    def repetitive_bsp(self) -> bool:
        return repetitive_filter_bsp(self.json_doc["text"], self.word_split)

    def smut(self) -> bool:
        # Recommended to only use for e.g. mc4 & Oscar, as this limited approach may introduce biases etc
        return not is_smut(self.json_doc["text"], self.word_split)
