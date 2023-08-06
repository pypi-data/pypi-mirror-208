from typing import NamedTuple
import nltk
from nltk.corpus import brown
from collections import defaultdict

nltk.download("brown", quiet=True)


class Flake8ASTErrorInfo(NamedTuple):
    line_number: int
    offset: int
    msg: str
    cls: type


VERB_CODES = [
    "VB",  # Verb, base form
    "VBD",  # Verb, past tense
    "VBG",  # Verb, gerund or present participle
    "VBN",  # Verb, past participle
    "VBP",  # Verb, non-3rd person singular present
    "VBZ",  # Verb, 3rd person singular present
]


NOUN_CODES = [
    "NN",  # singular or mass noun
    "NN$",  # possessive singular noun
    "NNS",  # plural noun
    "NNS$",  # possessive plural noun
    "NP",  # 	proper noun or part of name phrase
    "NP$",  # possessive proper noun
    "NPS",  # plural proper noun
    "NPS$",  # possessive plural proper noun
    "NR",  # 	adverbial noun	home, today, west
    "NRS",  # plural adverbial noun
]


word_tags = defaultdict(list)

for word, pos in brown.tagged_words():
    if pos not in word_tags[word]:  # to append one tag only once
        word_tags[word].append(pos)  # adding key-value to x
