# https://github.com/lighttransport/japanese-llama-experiment/blob/main/03_clean_step2/clean_mc4_task.py

from bunkai import Bunkai
import hashlib
import nltk
# from fugashi import Tagger
# import MeCab

zstd_comp_level = 5  # default = 3

# tagger = Tagger('-Owakati')
# tagger = MeCab.Tagger("-Owakati")
bunkai = Bunkai()

# in UTF-8 chars
min_doc_len = 10
max_doc_len = 327000

min_sent_len = 1
max_sent_len = 2048


def hash_text(text):
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def is_repetition_removal(
    text, duplicate_line_fraction=0.3, duplicate_line_character_faction=0.2
):
    """Check if there is repeated content in the input text. Excessive
    repetition is often linked with uninformative content and can be used to
    determine whether it is low-quality text. This function implements
    "Repetition Removal" as described in Gopher_.

    .. _Gopher: https://arxiv.org/abs/2112.11446

    Args:
        text (str): input text.
        duplicate_line_fraction (float, optional): Duplicate row deduplication
            threshold. Defaults to 0.3.
        duplicate_line_character_faction (float, optional): Threshold for the
            proportion of repeated line characters. Defaults to 0.2.

    Returns:
        bool: If there is repeated content in the input text.
    """
    line_count = 0
    dup_line = 0
    dup_line_chars = 0
    visit_lines = {}
    for line in text.split("\n"):
        line_hash = hash_text(line)
        if line_hash in visit_lines:
            dup_line += 1
            dup_line_chars += len(line)
        visit_lines[line_hash] = True

        line_count += 1

    if float(dup_line) / line_count > duplicate_line_fraction:
        return True

    if float(dup_line_chars) / len(text) > duplicate_line_character_faction:
        return True

    top_ngram_character_fractions = [
        (2, 0.2),
        (3, 0.18),
        (4, 0.16),
    ]
    for ngram, threshold in top_ngram_character_fractions:
        # word_list = list(jieba.cut(text))
        # wakachi-gaki
        word_list = tagger.parse(text).split()
        bgs = nltk.ngrams(word_list, ngram)
        fdist = nltk.FreqDist(bgs)
        for word_list, repeat in fdist.items():
            char_count = sum([len(word) for word in word_list])
            if char_count * (repeat - 1) / len(text) > threshold:
                return True

    duplicate_ngram_character_fractions = [
        (5, 0.15),
        (6, 0.14),
        (7, 0.13),
        (8, 0.12),
        (9, 0.11),
        (10, 0.10),
    ]
    for ngram, threshold in duplicate_ngram_character_fractions:
        fdist = {}
        word_list = tagger.parse(text).split()
        mark = [0] * len(word_list)
        for i in range(len(word_list) - ngram + 1):
            bag = tuple(word_list[i: i + ngram])
            if bag in fdist:
                for j in range(i, i + ngram):
                    mark[j] = len(word_list[j])
                fdist[bag] += 1
            else:
                fdist[bag] = 1

        if sum(mark) / float(len(text)) > threshold:
            return True

    return False


def do_length_filter(text: str):

    if len(text) < min_doc_len:
        return None

    if len(text) > max_doc_len:
        return None

    out_texts = []

    sents = text.split('\n')

    for sent in sents:
        if len(sent) < min_sent_len:
            return None

        if len(sent) > max_sent_len:
            return None

        out_texts.append(sent)

    return "\n".join(out_texts)


def do_repetition_removal(text: str):

    # Use normalizer for dedup(e.g. replace the number with a placeholder(0))
    # in_text = text_normalizer.normalize_for_dedup(text)
    in_text = text
    if is_repetition_removal(in_text):
        return None

    return text


def bunkai_text(text):
    lb_sep = '\n'  # (U+2581)
    text = text.replace('\n', lb_sep)
    join_text = ""
    for line in bunkai(text):
        join_text += line

    join_text = join_text.replace(lb_sep, '\n')
    return join_text


def do_filter(text):
    if text is None:
        return None
    text = bunkai_text(text)

    text = do_length_filter(text)
    if text is None:
        return None

    # text = do_repetition_removal(text)
    # if text is None:
    #    return None

    return text
