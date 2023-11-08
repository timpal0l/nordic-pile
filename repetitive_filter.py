# Code implementing instructions in Gopher paper
# https://arxiv.org/pdf/2112.11446.pdf, pages 40-41

import re
from collections import Counter

threshold_duplicate_lines = 0.35
threshold_duplicate_paragraph = 0.35
threshold_lines_chars = 0.20
threshold_paragraph_chars = 0.20
# thresholds_2_to_4_grams = [0.20, 0.18, 0.16]
# thresholds_5_to_10_grams = [0.15, 0.14, 0.13, 0.12, 0.11, 0.10]
thresholds_2_to_4_grams = [0.25, 0.23, 0.21]
thresholds_5_to_10_grams = [0.20, 0.19, 0.18, 0.17, 0.16, 0.15]


# For lines and paragraphs separately, we calculate over the document both the fraction that are duplicates,
# and the fraction of characters contained within those duplicates
def handle_duplicate_segments(segments, num_chars_tot, segment_threshold, character_threshold):
    counter = Counter(segments)
    duplicate_segments = [(t, count) for t, count in counter.items() if count >= 2]

    num_dup_segments = sum([count for _, count in duplicate_segments])
    fraction = num_dup_segments / len(segments)
    if fraction > segment_threshold:
        return False

    chars_dup = sum([len(t) * count for t, count in duplicate_segments])
    fraction = chars_dup / num_chars_tot
    if fraction > character_threshold:
        return False

    return True


# for each 𝑛 ∈ {2, . . . , 4}, we calculate the fraction of characters
# contained within the most frequently-occurring 𝑛-gram
def handle_2_to_4_gram(text, n_grams, threshold):
    # Find the most common n-gram
    counter = Counter(n_grams)

    top_n_gram, freq = counter.most_common(1)[0]
    if freq < 2:
        return True

    num_chars_within_top_n_gram = len(top_n_gram) * freq
    fraction = num_chars_within_top_n_gram / len(text)
    if fraction > threshold:
        return False

    return True


# for each 𝑛 ∈ {5, . . . , 10}, we calculate the fraction of characters contained within all duplicate 𝑛-grams,
# taking care not to count characters that occur in overlapping 𝑛-grams more than once
def handle_5_to_10_gram(text, n_grams, threshold):
    # Find all n-grams with at least one duplicate
    counter = Counter(n_grams)
    n = len(n_grams[0])

    duplicate_n_grams = [n_gram for n_gram, count in counter.items() if count >= 2]
    if len(duplicate_n_grams) == 0:
        return True

    duplicate_n_grams_set = set(duplicate_n_grams)  # Set gives constant lookup

    # Could likely be optimized if indices are kept when computing n_grams in first place
    last_index_used = -1
    freq_chars_in_dup = 0
    for start_idx in range(len(text) - n + 1):
        end_idx = start_idx + n
        n_gram = text[start_idx: end_idx]
        if n_gram in duplicate_n_grams_set:
            first_index_available = max(start_idx, last_index_used + 1)
            freq_chars_in_dup += end_idx - first_index_available
            last_index_used = end_idx - 1

    fraction = freq_chars_in_dup / len(text)

    if fraction > threshold:
        return False

    return True


def check_duplicate_lines_and_paragraphs(text, lines):
    # Lines
    if not handle_duplicate_segments(lines, len(text), threshold_duplicate_lines, threshold_lines_chars):
        return False

    # Paragraphs
    paragraphs = [t for t in re.split(r'\n{2,}', text) if len(t.strip()) > 0]
    if not handle_duplicate_segments(paragraphs, len(text), threshold_duplicate_paragraph, threshold_paragraph_chars):
        return False

    return True


def check_2_to_4_grams(text, doc_split):
    for n in range(2, 5):
        n_grams = custom_get_n_grams(doc_split, n)
        if len(n_grams) == 0:
            continue
        if not handle_2_to_4_gram(text, n_grams, thresholds_2_to_4_grams[n - 2]):
            return False

    return True


def check_5_to_10_grams(text, doc_split):
    for n in range(5, 11):
        n_grams = custom_get_n_grams(doc_split, n)
        if len(n_grams) == 0:
            continue
        if not handle_5_to_10_gram(text, n_grams, thresholds_5_to_10_grams[n - 5]):
            return False
        break

    return True


def custom_get_n_grams(doc_split, n):
    return [" ".join(doc_split[i: i + n]) for i in range(len(doc_split) - n + 1)]


def repetitive_filter(text, doc_split, lines, tokenizer=None):

    if not check_duplicate_lines_and_paragraphs(text, lines):
        return False

    if not check_2_to_4_grams(text, doc_split):
        return False

    if not check_5_to_10_grams(text, doc_split):
        return False

    return True


if __name__ == '__main__':
    # Test case
    text_example = "hej svejs i stugan där min vän, hej svejs ejsan"
    word_split = [x for x in re.split(r'\s+', text_example) if x]
    lines_ex = [line.strip() for line in text_example.splitlines() if len(line.strip()) > 0]
    repetitive_filter(text_example, word_split, lines_ex)
