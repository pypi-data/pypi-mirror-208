from pathlib import Path
import spacy
import json
from text2int import correction
from collections import Counter
import re

FILE = Path(__file__)
DATA_PATH = FILE.parent / 'data' / 'part_speech_tagging_test_set.jsonl'
nlp = spacy.load("en_core_web_sm")
tagger_pipe = nlp.get_pipe("tagger")
QWERTY = [
    ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
    ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
    ['z', 'x', 'c', 'v', 'b', 'n', 'm'],
    [' ']
]

def qwerty_distance(a, b):
    distance = 0
    if len(a) > len(b):
        b += (len(a) - len(b)) * ' '
    else:
        a += (len(b) - len(a)) * ' '
    for i, j in enumerate(a):
        if j == b[i]:
            pass
        else:
            if j and b[i] in [i for j in QWERTY for i in j]:
                a_c = 0
                a_r = 0
                b_c = 0
                b_r = 0
                for row in QWERTY:
                    a_r += 1
                    if j in row:
                        for column in row:
                            a_c += 1
                            if j == column:
                                break
                        break
                
                for row in QWERTY:
                    b_r += 1
                    if b[i] in row:
                        for column in row:
                            b_c += 1
                            if b[i] == column:
                                break
                        break
                
                col_d = abs(a_c - b_c)
                row_d = abs(a_r - b_r)
                distance += col_d + row_d

            else:
                distance += 5
    return distance


def words(text): return re.findall(r'\w+', text.lower())

with open(FILE.parent / 'data' / 'big.txt', 'r') as f:
    BIG = [i for i in f.read().split()]

WORDS = Counter(BIG)

def P(a, b, N=sum(WORDS.values())):
    "Probability of `word`."
    prob = WORDS[a] / N
    q_dist = qwerty_distance(a, b)
    if qwerty_distance(a, b) != 0:
        if (prob / q_dist) >= 8. ** -7 and find_char_diff(a, b) <= 5:
            return prob
    
        else:
            return 0.
    else:
        if prob >= 8. ** -7 and find_char_diff(a, b) <= 5:
            return prob
    
        else:
            return 0.

def big_correction(word):
    "Most probable spelling correction for word."
    c = list(candidates(word))
    probs = []
    for i in c:
        probs.append(P(i, word))
    
    return c[probs.index(max(probs))]


def candidates(word):
    "Generate possible spelling corrections for word."
    return (known([word]) or known(edits1(word)) or known(edits2(word)) or [word])


def known(words):
    "The subset of `words` that appear in the dictionary of WORDS."
    return set(w for w in words if w in WORDS)


def edits1(word):
    "All edits that are one edit away from `word`."
    letters = 'abcdefghijklmnopqrstuvwxyz'
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes = [L + R[1:] for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
    replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
    inserts = [L + c + R for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)


def edits2(word):
    "All edits that are two edits away from `word`."
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))


def find_char_diff(a, b):
    # Finds the character difference between two str objects by counting the occurences of every character. Not edit distance.
    char_counts_a = {}
    char_counts_b = {}
    for char in a:
        if char in char_counts_a.keys():
            char_counts_a[char] += 1
        else:
            char_counts_a[char] = 1
    for char in b:
        if char in char_counts_b.keys():
            char_counts_b[char] += 1
        else:
            char_counts_b[char] = 1
    char_diff = 0
    for i in char_counts_a:
        if i in char_counts_b.keys():
            char_diff += abs(char_counts_a[i] - char_counts_b[i])
        else:
            char_diff += char_counts_a[i]
    return char_diff

def tagger(text):
    toks = text.split()
    toks = [big_correction(tok) for tok in toks]
    u = probs(text)
    tags = {i[2]:i[1] for i in u}
    corrected = " ".join([i[1] if tags[i[0]] >= 10 else correction(i[1]) for i in zip(tags.keys(), toks)])
    return [(tok.text, tok.pos_) for tok in nlp(corrected)]

def probs(text):
    toks = text.split()
    doc = nlp(text)
    pred = tagger_pipe.model.predict([doc])
    probs = []
    for i in range(len(pred[0])):
        keys = [*enumerate(pred[0][i])]
        keys.sort(key=lambda x: x[1])
        new_item = [(tagger_pipe.labels[int(i[0])], i[1]) for i in keys]
        probs.append(new_item[-1] + tuple([toks[i]]))
    return probs