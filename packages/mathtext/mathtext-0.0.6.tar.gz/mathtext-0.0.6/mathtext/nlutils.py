""" Utilites for processing chatbot message text to extract number words (text2int)

  * [ ] has_comma_thousands_separator
  * [ ] render_int(with_comma=False, exponential_notation=False)
  * [ ] render_num(with_comma=False, exponential_notation=False)
  * [ ] render_float(with_comma=False, exponential_notation=False)
  * [ ] num_to_str()
  * [ ] get_ints()
  * [ ] all functions need doctests and/or unittests

  * [ ] text2nums function that Seb (catasaurus) is working on
  * [ ] tag_nums function to return tokens tagged with num or POS (spacy does this)
  * [ ] tag_math_tokens returns POS including plus, minus, times, etc
  * [ ] extract_expression
  * [ ] >>> get_math_tokens("1+2") => ["1", "+", "2"]
  * [ ] >>> eval_math_tokens(["1", "+", "2"]) => 3
"""
import datetime
import re
import spacy  # noqa
from transformers import pipeline
from collections import Counter
from mathtext.spacy_language_model import nlp
from mathtext.constants import TOKENS2INT_ERROR_INT
from unidecode import unidecode


# import os
# os.environ['KMP_DUPLICATE_LIB_OK']='True'
# import spacy

# Change this according to what words should be corrected to
SPELL_CORRECT_MIN_CHAR_DIFF = 2

ONES = [
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
    "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
    "sixteen", "seventeen", "eighteen", "nineteen",
]

CHAR_MAPPING = {
    "-": " ",
    "_": " ",
    "and": " ",
}
# CHAR_MAPPING.update((str(i), word) for i, word in enumerate([" " + s + " " for s in ONES]))

TOKEN_MAPPING = {
    "and": " ",
    "oh": "0",
}


def has_comma_thousands_separator(number_word, sep=','):
    """ Return True if string contains a valid number representation with comma as thousands seperator

    >>> has_comma_thousands_separator('10,000')
    True
    >>> has_comma_thousands_separator('9,123,456.')
    True
    >>> has_comma_thousands_separator('123,456,789,012,345.678901')
    True
    >>> has_comma_thousands_separator('123456789012345.678901')
    False
    >>> has_comma_thousands_separator('123_456_789_012_345.678901')
    False

    >>> has_comma_thousands_separator('1,2,3')
    Traceback (most recent call last):
     ...
    ValueError: Invalid number representation. has_comma_thousands_separator() only accepts a string representation of a single number (not a number sequence)
    """
    if sep not in number_word:
        return False

    r = re.search(r'^\d{1,3}(,\d{3})*(\.\d*)?$', number_word)
    if r:
        return True
    else:
        # TODO: Deal with exponential notation
        # for strings that are not numbers
        if not number_word.replace(sep, '').replace('.', "").replace('_', "").isdigit():
            raise ValueError('Invalid number representation. has_comma_thousands_separator() only accepts a valid string representation of a single number')
        # for strings that are sequences of numbers
        else:
            raise ValueError('Invalid number representation. has_comma_thousands_separator() only accepts a string representation of a single number (not a number sequence)')

    return False


def is_int(x):
    """ Return False if values is not a valid integer and cannot be coerced into an integer

    >>> is_int('123')
    True
    >>> is_int('0.0')
    True
    >>> is_int(float('nan'))
    False
    >>> is_int('1.234e5')
    True
    >>> is_int(1234567)
    True
    """
    try:
        if float(x) == int(float(x)):
            return True
    except ValueError:
        pass
    return False


def is_float(x):
    """ Return False if the value is not a valid float and cannot be coerced into a float

    >>> is_float('0.4')
    True
    >>> is_float('1')
    True
    >>> is_float('Not sure')
    False
    >>> is_float("Don't know if it's 0.5 or 1")
    False
    """
    try:
        float(x)
        return True
    except ValueError:
        return False


def extract_num_token(text):
    """ Extract the first number we find in a message

    >>> extract_num_token("1,2,3")
    ['1']
    >>> extract_num_token("4, 5, 6")
    ['4']
    >>> extract_num_token("I don't know.... 3")
    ['3']
    >>> extract_num_token("Maybe 9.5 is the answer")
    ['9.5']
    >>> extract_num_token("The answer is either 764 or 42")
    ['764']
    """
    text = text.replace(",", " ")
    doc = nlp(text)

    for tok in doc:
        if tok.pos_ == 'NUM':
            return [tok.text]
    return []


def extract_nums_tokens(text):
    """ Return all tokens that are numbers part of speech as a list

    >>> extract_nums_tokens("1 2, 3")
    [['1', '2'], ['3']]

    >>> extract_nums_tokens("1 two, 3")
    [['1', 'two'], ['3']]

    >>> extract_nums_tokens(",9")
    [['9']]
    """
    doc = nlp(text)
    nums_toks = []
    num_toks = []

    # Handle cases like 'twenty-two' the same as 'twenty two'
    doc_tokens = list(doc)
    for i in range(1, len(doc_tokens)):
        try:
            if doc_tokens[i].text == '-' and doc_tokens[i-1].pos_ == 'NUM' and doc_tokens[i+1].pos_ == 'NUM':
                del doc_tokens[i]
        except IndexError:
            pass

    # NOTE: Before just used doc
    for tok in doc_tokens:
        if tok.pos_ == 'NUM':
            num_toks.append(tok.text)
        elif num_toks:
            nums_toks.append(num_toks)
            num_toks = []
    if num_toks:
        nums_toks.append(num_toks)
    return nums_toks


def extract_num_str(num):
    """ Extract the string representation of the number

    >>> extract_num_str(42)
    '42'
    >>> extract_num_str(3849)
    '3849'
    >>> extract_num_str(3.78)
    '3.78'
    >>> extract_num_str(0)
    '0'
    """
    return str(num)


def tokens2float(tokens):
    """ Convert each token in a list to a float representation of the number

    >>> tokens2float([1, 2, 3])
    [1.0, 2.0, 3.0]
    >>> tokens2float([1.74, 0, 3495])
    [1.74, 0.0, 3495.0]
    >>> tokens2float(["I", "don't", "know", 5])
    [5.0]
    >>> tokens2float(["Oh", "no"])
    []
    """
    float_toks = []
    for tok in tokens:
        try:
            float_toks.append(float(tok))
        except ValueError:
            pass

    return float_toks


def text2float(text):
    """ Convert text representation of a float into a float

    >>> text2float("1.23")
    1.23
    >>> text2float("1")
    1.0
    >>> text2float("I don't know")
    Traceback (most recent call last):
    ...
    ValueError: could not convert string to float: "Idon'tknow"
    >>> text2float("2..0")
    2.0
    >>> text2float("4 . 5")
    4.5
    """
    # if isinstance(text, str):
    text_spaces_stripped = text.replace(" ", "")
    processed_text = re.sub(r'\.+', '.', text_spaces_stripped)

    return float(processed_text)


def render_int(x, with_comma=False, exponential_notation=False):
    """ Coerce integer into a string for inclusion in a chat text message.

    For non-integer types, raises ValueError.

    >>> render_int(123)
    '123'
    >>> render_int(123_456)
    '123456'
    >>> render_int(123.4)
    Traceback (most recent call last):
    ...
    ValueError: The value 123.4 doesn't appear to be an integer nor an integer representation.
    >>> render_int(123_456, with_comma=True)
    '123,456'
    >>> render_int(-123)
    '-123'

    TODO:
    >> > render_int(12;3456)
    '123456'
    """
    if isinstance(x, int):
        if with_comma:
            return "{:,}".format(x)
        else:
            return str(x)
    elif isinstance(x, str) and x.isdigit():
        if with_comma:
            return "{:,}".format(int(x))
        else:
            return x
    else:
        raise ValueError(f"The value {x} doesn't appear to be an integer nor an integer representation.")


def render_float(with_comma=False, exponential_notation=False):
    pass


def render_num(with_comma=False, exponential_notation=False):
    pass


def replace_words(s, word_dict, whole_word=True):
    """ Like str.replace(word_dict) - replace occurrences of a dict's keys with its values

    SEE ALSO: replace_tokens(text)

    >>> word_dict = {'Спорт': 'Досуг', 'russianA': 'englishA'}
    >>> replace_words('Спорт not russianA', word_dict)
    'Досуг not englishA'
    """
    word_sep = ''  # word separator regex pattern
    if whole_word:
        word_sep = r'\b'
    keys = (re.escape(k) for k in word_dict.keys())
    pattern = re.compile(f'{word_sep}(' + '|'.join(keys) + f'){word_sep}')
    return pattern.sub(lambda x: word_dict[x.group()], s)


def replace_substrings(s, word_dict, whole_word=False):
    """ Like replace_words except ignore word boundaries(default to whole_word=False)

    >>> word_dict = {'Спорт': 'Досуг', 'russianA': 'englishA'}
    >>> replace_substrings('Спорт notrussianA', word_dict)
    'Досуг notenglishA'
    """
    return replace_words(s, word_dict, whole_word=whole_word)


def find_char_diff(a, b):
    """ Character difference between two str - counts occurrences of chars independently. Not edit distance.

    >>> find_char_diff('eight', 'eht')
    2
    >>> find_char_diff('eight', 'iht')
    2
    >>> find_char_diff('eight', 'hit')
    2
    >>> find_char_diff('feet', 'feeet')
    1

    >>  edit_distance('eight', 'hit')
    3
    """

    char_counts_a = Counter(a)
    char_counts_b = Counter(b)
    char_diff = 0
    for i in char_counts_a:
        if i in char_counts_b:
            char_diff += abs(char_counts_a[i] - char_counts_b[i])
        else:
            char_diff += char_counts_a[i]
    return char_diff


def tokenize(text):
    text = text.lower()
    text = replace_tokens(
        ''.join(i for i in replace_chars(
            text, char_mapping=CHAR_MAPPING)
        ).split(),
        token_mapping=TOKEN_MAPPING)
    # print(text)
    text = [i for i in text if i != ' ']
    # print(text)
    output = []
    for word in text:
        # print(word)
        output.append(convert_word_to_int(word))
    output = [i for i in output if i != ' ']
    # print(output)
    return output


def detokenize(tokens):
    return ' '.join(tokens)


def replace_tokens(tokens, token_mapping=TOKEN_MAPPING):
    return [token_mapping.get(tok, tok) for tok in tokens]


def replace_chars(text, char_mapping=CHAR_MAPPING):
    return [char_mapping.get(c, c) for c in text]


def convert_word_to_int(in_word, numwords={}):
    # Converts a single word/str into a single int
    tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
    scales = ["hundred", "thousand", "million", "billion", "trillion"]
    if not numwords:
        for idx, word in enumerate(ONES):
            numwords[word] = idx
        for idx, word in enumerate(tens):
            numwords[word] = idx * 10
        for idx, word in enumerate(scales):
            numwords[word] = 10 ** (idx * 3 or 2)
    if in_word in numwords:
        # print(in_word)
        # print(numwords[in_word])
        return numwords[in_word]
    try:
        int(in_word)
        return int(in_word)
    except ValueError:
        pass
    # Spell correction using find_char_diff
    char_diffs = [find_char_diff(in_word, i) for i in ONES + tens + scales]
    min_char_diff = min(char_diffs)
    if min_char_diff <= SPELL_CORRECT_MIN_CHAR_DIFF:
        return char_diffs.index(min_char_diff)


def tokens2int(tokens):
    """ Takes a list of tokens and returns a int representation of them """
    types = []
    for i in tokens:
        if i <= 9:
            types.append(1)

        elif i <= 90:
            types.append(2)

        else:
            types.append(3)
    # print(tokens)
    if len(tokens) <= 3:
        current = 0
        for i, number in enumerate(tokens):
            if i != 0 and types[i] < types[i - 1] and current != tokens[i - 1] and types[i - 1] != 3:
                current += tokens[i] + tokens[i - 1]
            elif current <= tokens[i] and current != 0:
                current *= tokens[i]
            elif 3 not in types and 1 not in types:
                current = int(''.join(str(i) for i in tokens))
                break
            elif '111' in ''.join(str(i) for i in types) and 2 not in types and 3 not in types:
                current = int(''.join(str(i) for i in tokens))
                break
            else:
                current += number

    elif 3 not in types and 2 not in types:
        current = int(''.join(str(i) for i in tokens))

    else:
        count = 0
        current = 0
        for i, token in enumerate(tokens):
            count += 1
            if count == 2:
                if types[i - 1] == types[i]:
                    current += int(str(token) + str(tokens[i - 1]))
                elif types[i - 1] > types[i]:
                    current += tokens[i - 1] + token
                else:
                    current += tokens[i - 1] * token
                count = 0
            elif i == len(tokens) - 1:
                current += token

    return current


def text2int(text):
    # Wraps all of the functions up into one
    return tokens2int(tokenize(text))


def text2num(text):
    """ is it an integer or float and return the appropriate type, or send 32202

    >>> text2num("0.2")
    0.2
    >>> text2num("1")
    1
    >>> text2num("Not sure")
    32202
    """
    if text.isdigit():
        return int(text)

    if is_float(text):
        return text2float(text)

    return 32202


def is_time(text):
    match = re.search(r"\b(\d{1,2}):(\d{2})\b", text)
    if match:
        # Check that the matched hour and minute values are valid
        hour = int(match.group(1))
        minute = int(match.group(2))
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return True
    return False


def text2time(text, expected_answer=None):
    """ Converts a time string or object to a hh:mm formatted str or returns error code
    >>> text2time("11:30")
    '11:30'
    >>> text2time("10: 20")
    '10:20'
    >>> text2time("13:20 PM")
    '13:20'
    >>> text2time("0:50")
    '0:50'
    >>> text2time("09:22")
    '9:22'
    >>> text2time("I don't know")
    32202
    >>> text2time("Maybe it's thirty")
    32202
    >>> text2time("2.0")
    32202
    """
    formatted_time = text
    try:
        timestamp = datetime.datetime.strptime(text[3:-1], '%H:%M:%S')
        formatted_time = timestamp.strftime('%H:%M')
    except ValueError:
        pass

    text_normalized = formatted_time.lower().replace(" ", "").replace("am", "").replace("pm", "")
    # Remove leading 0 if 2 or more digits
    text_reformatted = re.sub(
        r'(?<!\d)0(\d{1,2}?:)',
        r'\1',
        text_normalized
    )

    if not is_time(text_reformatted):
        return TOKENS2INT_ERROR_INT
    return text_reformatted


symbol_answer_types = {
    '>': ['>', 'g', 'gt', 'greater'],
    '<': ['<', 'l', 'lt', 'less'],
    '>=': ['>=', 'gte'],
    '<=': ['<=', 'lte'],
    '=': ['=', 'e', 'equal'],
}


def text2symbol(text, expected_answer):
    """ Returns a properly formatted >, <, = answer or the error code

    >>> text2symbol(">", ">")
    '>'
    >>> text2symbol(">=", ">=")
    '>='
    >>> text2symbol("<", "L")
    'L'
    >>> text2symbol("gte", ">=")
    '>='
    >>> text2symbol(">", ">")
    '>'
    >>> text2symbol("1", ">")
    32202
    """
    expected_answer_type = None
    for answer_type in symbol_answer_types:
        if expected_answer.lower() in symbol_answer_types[answer_type]:
            expected_answer_type = answer_type

    if expected_answer_type:
        message_formatted = text.lower().translate(str.maketrans('', '', '!"#$%&\()*+,-./:;?@[\\]^_`{|}~')).split()

        # Convert student answer to valid format
        for answer_type in symbol_answer_types:
            # Returns the expected_answer if student gave correct answer
            matched_word = [expected_answer for word in message_formatted if word in symbol_answer_types[expected_answer_type]]
            if matched_word:
                return matched_word[0]

            # Returns the properly formatted answer if student gave an appropriate option, but wrong answer
            matched_word = [answer_type for word in message_formatted if word in symbol_answer_types[answer_type]]
            if matched_word:
                return matched_word[0]
    return TOKENS2INT_ERROR_INT


text_answer_types = {
    'Yes': ['y', 'yes', 'yah', 'yeah', 'ok', 'okay', 'yea'],
    'No': ['n', 'no', 'nah'],
    'T': ['t', 'true', 'y', 'yes', 'yah', 'yeah', 'ok', 'okay', 'yea'],
    'F': ['f', 'false', 'n', 'no', 'nah'],
    'A': ['a'],
    'B': ['b'],
    'C': ['c'],
    'D': ['d'],
    'Even': ['even'],
    'Odd': ['odd'],
    'Monday': ['mon', 'monday'],
    'Tuesday': ['tues', 'tuesday'],
    'Wednesday': ['wed', 'wednesday'],
    'Thursday': ['thurs', 'thursday'],
    'Friday': ['fri', 'friday'],
    'Saturday': ['sat', 'saturday'],
    'Sunday': ['sun', 'sunday'],
}

expected_answer_type_groups = {
    'yes-no': ['Yes', 'No'],
    'true-false': ['T', 'F'],
    'multiple-choice': ['A', 'B', 'C', 'D'],
    'even-odd': ['Even', 'Odd'],
    'day-of-the-week': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
}


def text2text(text, expected_answer):
    """ Converts a valid text answer to the expected answer's format or returns error code
    >>> text2text("odd", "Odd")
    'Odd'
    >>> text2text("Even", "Even")
    'Even'
    >>> text2text("Y", "Yes")
    'Yes'
    >>> text2text("a", "A")
    'A'
    >>> text2text("Yes", "Yes")
    'Yes'
    >>> text2text("true", "T")
    'T'
    >>> text2text("True", "T")
    'T'
    >>> text2text("1", None)
    32202
    >>> text2text("I have no idea", "F")
    'F'
    >>> text2text("no", "1")
    32202
    """

    # Determine the expected answer type
    expected_answer_group = None
    for group in expected_answer_type_groups:
        if expected_answer in expected_answer_type_groups[group]:
            expected_answer_group = group

    if not expected_answer_group:
        return TOKENS2INT_ERROR_INT

    # Check that the expected answer is one of the types
    expected_answer_type = None
    answer_type_group = None
    for answer_type in expected_answer_type_groups[expected_answer_group]:
        for answer_option in text_answer_types[answer_type]:
            if expected_answer.lower() in text_answer_types[answer_type]:
                expected_answer_type = answer_type

    if not expected_answer_type:
        return TOKENS2INT_ERROR_INT

    message_formatted = text.lower().translate(str.maketrans('', '', '!"#$%&\()*+,-./:;?@[\\]^_`{|}~')).split()

    # Handle if the student entered a right answer that's the right type
    for answer_option in text_answer_types[expected_answer_type]:
        matched_word = [expected_answer for word in message_formatted if word == answer_option]
        if matched_word:
            return matched_word[0]

    # Handle if the student entered a wrong answer that's one of the right types
    for answer_option in expected_answer_type_groups[expected_answer_group]:
        for answer in text_answer_types[answer_option]:
            matched_word = [answer_option for word in message_formatted if word == answer]

            if matched_word:
                return matched_word[0]

    return TOKENS2INT_ERROR_INT


def text2exponent(text, expected_answer):
    """ Returns a properly formatted exponent answer or the error code

    >>> text2exponent("7^2", "7^2")
    '7^2'
    >>> text2exponent("14 ^2", "14^2")
    '14^2'
    >>> text2exponent("2.5 ^ 80", "2.5^80")
    '2.5^80'
    >>> text2exponent("I don't know", "2.5^80")
    32202
    >>> text2exponent("It might be 2 ^ 8", "2^8")
    '2^8'
    >>> text2exponent("3^4", "5^6")
    '3^4'
    """
    superscript_list = ["⁰", "¹", "²", "³", "⁴", "⁵", "⁶", "⁷", "⁸", "⁹"]

    text = re.sub(
        r"(to\s*the)",
        "^",
        text
    )

    base = ""
    exponent = ""
    for char in text:
        if char in superscript_list:
            exponent += unidecode(char)
        else:
            base += char

    if exponent:
        text = base + "^" + exponent

    match = re.search(r'[-]?\d+(\.\d+)?\s*\^\s*[-]?\d+(\.\d+)?', text)
    try:
        matched_text = match.group(0)
    except AttributeError:
        return TOKENS2INT_ERROR_INT

    answer = matched_text.replace(" ", "")

    return answer


def text2fraction(text, expected_answer):
    """ Returns a properly formatted fraction answer or the error code

    >>> text2fraction("65/6", "65/6")
    '65/6'
    >>> text2fraction("1/3", "1/3")
    '1/3'
    >>> text2fraction("8 / 10", "8/10")
    '8/10'
    >>> text2fraction("55 1 /28", "55 1/28")
    '55 1/28'
    >>> text2fraction("14  1/2", "14 1/2")
    '14 1/2'
    >>> text2fraction("25 12/3 maybe?", "25 12/3")
    '25 12/3'
    """
    if "/" not in expected_answer:
        return TOKENS2INT_ERROR_INT

    text = re.sub(
        r"(over|oer|ovr)",
        "/",
        text
    )

    match = re.search(r'(\d+\s+)?\d+\s*/\s*\d+', text)

    if match:
        normalize_fraction = match[0].replace(" /", "/").replace("/ ", "/").replace("  ", " ")
        return normalize_fraction

    return TOKENS2INT_ERROR_INT


def text2equation(text, expected_answer=None):
    """ Returns a properly formatted multiplication equation or the error code

    >>> text2equation("2 times 15", "2x15")
    '2x15'
    >>> text2equation("3 *9", "3x9")
    '3x9'
    >>> text2equation("4multiply10", "4x10")
    '4x10'
    """
    # Converts multiplication words to x
    text = re.sub(
        r"(times|multiplied\s*by|multiplied|multiply)|\*",
        "x",
        text
    )

    # Extracts multiplication equation from phrases
    match = re.search(r'[-]?\d+(\.\d+)?\s*x\s*[-]?\d+(\.\d+)?', text)
    try:
        normalized_equation = match[0].replace(" ", "")
        return normalized_equation
    except AttributeError:
        return TOKENS2INT_ERROR_INT
    except TypeError:
        return TOKENS2INT_ERROR_INT
    return TOKENS2INT_ERROR_INT


###############################################
# Vish editdistance approach doesn't halt


def lev_dist(a, b):
    '''
    This function will calculate the levenshtein distance between two input
    strings a and b

    params:
        a (String) : The first string you want to compare
        b (String) : The second string you want to compare

    returns:
        This function will return the distance between string a and b.

    example:
        a = 'stamp'
        b = 'stomp'
        lev_dist(a,b)
        >> 1.0
    '''
    if not isinstance(a, str) and isinstance(b, str):
        raise ValueError(f"lev_dist() requires 2 strings not lev_dist({repr(a)}, {repr(b)}")
    if a == b:
        return 0

    def min_dist(s1, s2):

        print(f"{a[s1]}s1{b[s2]}s2 ", end='')
        if s1 >= len(a) or s2 >= len(b):
            return len(a) - s1 + len(b) - s2

        # no change required
        if a[s1] == b[s2]:
            return min_dist(s1 + 1, s2 + 1)

        return 1 + min(
            min_dist(s1, s2 + 1),      # insert character
            min_dist(s1 + 1, s2),      # delete character
            min_dist(s1 + 1, s2 + 1),  # replace character
        )

    dist = min_dist(0, 0)
    print(f"\n  lev_dist({a}, {b}) => {dist}")
    return dist


sentiment = pipeline(
    task="sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)


def get_sentiment(text):
    return sentiment(text)
