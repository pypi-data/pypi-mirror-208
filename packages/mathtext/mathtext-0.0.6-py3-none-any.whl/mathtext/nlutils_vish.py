import time
from editdistance import eval as edit_dist, tokenize, tokens2int
from nlutils import TOKENS2INT_ERROR_INT


def correct_number_text(text):
    """ Convert an English str containing number words with possibly incorrect spellings into an int

    >>> correct_number_text("too")
    2
    >>> correct_number_text("fore")
    4
    >>> correct_number_text("1 2 tree")
    123
    """
    words = {
        "zero": 0,
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,
        "eleven": 11,
        "twelve": 12,
        "thirteen": 13,
        "fourteen": 14,
        "fifteen": 15,
        "sixteen": 16,
        "seventeen": 17,
        "eighteen": 18,
        "nineteen": 19,
        "score": 20,
        "twenty": 20,
        "thirty": 30,
        "forty": 40,
        "fifty": 50,
        "sixty": 60,
        "seventy": 70,
        "eighty": 80,
        "ninety": 90,
        "hundred": 100,
        "thousand": 1000,
        "million": 1000000,
        "billion": 1000000000,
    }

    text = text.lower()
    text_words = text.replace("-", " ").split()
    corrected_words = []
    for text_word in text_words:
        if text_word is None:
            continue
        if text_word not in words:
            print(f"{text_word} not in words")
            if not isinstance(text_word, str):
                return TOKENS2INT_ERROR_INT
            t0 = time.time()
            min_dist = len(text_word)
            correct_spelling = None
            for word in words:
                dist = edit_dist(word, text_word)
                if dist < min_dist:
                    correct_spelling = word
                    min_dist = dist
            corrected_words.append(correct_spelling)
            t1 = time.time()
            print(f"{text_word} dt:{t1-t0}")
        else:
            corrected_words.append(text_word)

    corrected_text = " ".join(corrected_words)

    print(corrected_text)
    return corrected_text


def text2int(text):
    """ Correct spelling of number words in text before using text2int """
    try:
        return tokens2int(tokenize(correct_number_text(text)))
    except Exception as e:
        print(e)
    return TOKENS2INT_ERROR_INT
