# Code implementing repetitive filter of Big Science Park's data cleaning:
# https://github.com/bigscience-workshop/data_tooling/blob/master/ac_dc/filtering.py

import numpy as np
import re
import string
import emoji

main_special_characters = string.punctuation + string.digits + string.whitespace
other_special_characters = (
    "    　    ￼’“”–ー一▬…✦�­£​•€«»°·═"
    "×士＾˘⇓↓↑←→（）§″′´¿−±∈﻿¢ø‚„½¼¾¹²³―⁃，ˌ¸‹›ʺˈʻ¦‐⠀‰‑≤≥‖"
    "◆●■►▼▲▴∆▻¡★☆✱ːº。¯˜¥ɪ≈†上ン：∼⁄・♡✓⊕․．⋅÷１‟；،、¨ाাी्े◦˚"
    "゜ʼ≖ʼ¤ッツシ℃√！【】‿∞➤～πه۩☛₨➩☻๑٪♥ıॽ《‘©﴿٬？▷Г♫∟™ª₪®「—❖"
    "」﴾》"
)
emoji = list(emoji.UNICODE_EMOJI["en"].keys())

special_characters_default = set(main_special_characters + other_special_characters)
special_characters_default.update(emoji)


#### get words from document ####
def remove_empty_el_from_list(list_):
    return [el for el in list_ if el]


def split_on_whitespace(document, new_line=False, tab=False):
    """This method also removes concatenated spaces."""
    sep = [" "] + new_line * ["\n"] + tab * ["\t"]
    sep = "|".join(sep)
    split_document = re.split(sep, document)
    split_document = remove_empty_el_from_list(split_document)
    return split_document


def strip(document, strip_characters):
    """Way faster than document.strip(strip_characters)
    since strip_characters is now a set instead of a str,
    and it contains a lot of elements (all the emojis)."""
    if not document:
        return document
    beg_ind = 0
    end_ind = len(document)
    for i in range(len(document)):
        if document[i] in strip_characters:
            beg_ind += 1
        else:
            break
    for i in range(1, len(document) + 1):
        if document[-i] in strip_characters:
            end_ind -= 1
        else:
            break
    document_stripped = document[beg_ind:end_ind]
    return document_stripped


def get_words_from_document(document, lower_case, strip_characters):
    """Get words from a document. Non reversible since the document
    is split on multiple characters, words are stripped of
    special characters and characters are converted to lower case.
    Useful to compute ratios, like the stopwords ratio."""
    """if sentencepiece_model_tok:  -> False in parameter file
        document_normalized = ModifyingDocuments.normalization(
            document=document,
            remove_non_printing_characters=True,
            strip=True,
            lower_case=True,
            uniform_whitespace=True,
            replace_digits_with_zeros=True,
            replace_unicode_punctuation=True,
        )
        words = ModifyingDocuments.tokenization(
            document_normalized, sentencepiece_model_tok, join_on_whitespace=False
        )"""

    words = split_on_whitespace(
        document, new_line=True, tab=True
    )
    if lower_case:
        words = [word.lower() for word in words]
    if strip_characters:
        words = [strip(word, strip_characters) for word in words]
        words = remove_empty_el_from_list(words)
    return words


def repetitive_filter_bsp(text, doc_split): #they have different values for different languages...
    if not check_character_repetition_removal(text, 10, 0.3): # higher tresholds, is less restrictive, so less removal
        return False
    if not check_word_repetition_removal(text, doc_split, 5, 0.4):
        return False
    return True


####### Character repetition ######
def get_freq_character_ngrams(document, n):
    character_ngrams = [
        document[i: i + n] for i in range(len(document) - n + 1)
    ]
    freq_character_ngrams = {}
    for character_ngram in character_ngrams:
        freq_character_ngrams[character_ngram] = (
                freq_character_ngrams.get(character_ngram, 0) + 1
        )
    return freq_character_ngrams


def compute_character_repetition_ratio(document, character_repetition_length):
    freq_character_ngrams = get_freq_character_ngrams(
        document, character_repetition_length
    )
    if len(freq_character_ngrams) == 0:
        return 0
    freq_character_ngrams = list(freq_character_ngrams.values())
    freq_character_ngrams = sorted(freq_character_ngrams, reverse=True)
    val_less_than_one = len([el for el in freq_character_ngrams if el > 1])
    num_rep_character_ngrams = min(
        int(np.sqrt(len(freq_character_ngrams))),
        len(freq_character_ngrams) - val_less_than_one,
    )
    character_repetition_ratio = sum(
        freq_character_ngrams[:num_rep_character_ngrams]
    ) / sum(freq_character_ngrams)
    return character_repetition_ratio


def check_character_repetition_removal(document, character_repetition_length, character_repetition_max_cutoff):
    character_repetition_ratio = compute_character_repetition_ratio(document, character_repetition_length)
    cond = character_repetition_ratio <= character_repetition_max_cutoff
    return cond


###### word repetition ######
def get_freq_word_ngrams(document, words, n):  # , sentencepiece_model_tok, strip_characters
    """
    ModifyingDocuments.get_words_from_document(
        document,
        sentencepiece_model_tok,
        lower_case=True,
        strip_characters=strip_characters,
    )"""
    word_ngrams = [
        " ".join(words[i: i + n]) for i in range(len(words) - n + 1)
    ]
    freq_word_ngrams = {}
    for word_ngram in word_ngrams:
        freq_word_ngrams[word_ngram] = freq_word_ngrams.get(word_ngram, 0) + 1
    return freq_word_ngrams


def compute_word_repetition_ratio(document, words,
                                  word_repetition_length):  # sentencepiece_model_tok, strip_characters,
    words = get_words_from_document(document, True, special_characters_default)

    freq_word_ngrams = get_freq_word_ngrams(
        document, words, word_repetition_length  # sentencepiece_model_tok, strip_characters,
    )
    if len(freq_word_ngrams) == 0:
        return 0
    freq_word_ngrams = list(freq_word_ngrams.values())
    word_repetition_ratio = sum(
        freq for freq in freq_word_ngrams if freq > 1
    ) / sum(freq_word_ngrams)
    return word_repetition_ratio


def check_word_repetition_removal(  # sentencepiece_model_tok, strip_characters,
        document,
        words,
        word_repetition_length,
        word_repetition_max_cutoff,
):
    word_repetition_ratio = compute_word_repetition_ratio(
        document, words, word_repetition_length  # sentencepiece_model_tok, strip_characters,
    )
    cond = word_repetition_ratio <= word_repetition_max_cutoff
    return cond
