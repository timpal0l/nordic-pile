# Adapted from https://github.com/bigscience-workshop/data_tooling/blob/master/ac_dc/normalization.py

import re
from typing import Dict


unicode_punctuation: Dict[str, str] = {
    "，": ",",
    "。": ".",
    "、": ",",
    "„": '"',
    "”": '"',
    "“": '"',
    "«": '"',
    "»": '"',
    "１": '"',
    "」": '"',
    "「": '"',
    "《": '"',
    "》": '"',
    "´": "'",
    "∶": ":",
    "：": ":",
    "？": "?",
    "！": "!",
    "（": "(",
    "）": ")",
    "；": ";",
    "–": "-",
    "—": " - ",
    "．": ". ",
    "～": "~",
    "’": "'",
    "…": "...",
    "━": "-",
    "〈": "<",
    "〉": ">",
    "【": "[",
    "】": "]",
    "％": "%",
    "►": "-",
}


whitespace = {
    " ",
    " ",
    " ",
    " ",
    " ",
    "　",
    " ",
    " ",
    " ",
    " ",
    "￼",
    "",
}

# Control chars except newlines and tabs, soft-hyphens, and non-breaking space, zero-width space
additional_chars_to_remove = [160, 173, 8203]
non_printing_characters_re = re.compile(
    # f"[{''.join(map(chr, list(range(0,32)) + list(range(127,160))))}]"
    f"[{''.join(map(chr, list(range(0,9)) + list(range(11, 32)) + list(range(127,160)) + additional_chars_to_remove))}]"
)


def replace_unicode_punctuation(document):
    return "".join(unicode_punctuation.get(c, c) for c in document)


def uniform_whitespace(document_text):
    """There are different whitespace characters."""
    # whitespace = set(whitespace)
    document_text = "".join(
        [char if char not in whitespace else " " for char in document_text]
    )
    return document_text


def remove_non_printing_characters(document_text):
    return non_printing_characters_re.sub("", document_text)
