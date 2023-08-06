"""
Date normaliser
"""
import re

from .lookups import days, months, mutations, number_dict
from .number_norm import find_numbers

_time_re = re.compile(
    r"""\b
                          ((0?[0-9])|(1[0-9])|(2[0-9])|(3[0-1]))  # diwrnod
                          /
                          ((0?[0-9])|(1[0-2]))  # mis
                          /
                          ([0-9]{4})  # blywddyn
                          \b""",
    re.IGNORECASE | re.X,
)


def mutate(time_input, replacements):
    """
    mutate the know times
    :param time_input:
    :param replacements:
    :return:
    """
    for replacement in replacements:
        time_input = time_input.replace(replacement[0], replacement[1])
    return time_input


known_years = {
    "2020": "dwy fil ac ugain",
}


def _expand_date_welsh(match):
    # TODO: Ychwanegu pob mis i xx/xx/xx
    # TODO: Trin yn + nnnn fel blwyddyn o fewn cyfnod penodol?
    # TODO: ym + 19xxx = ym mil naw x x
    # TODO: yn + 2000 - 2050(?) = yn nwy fil x x
    # TODO: Degawdau 1920au - "un naw dau ddegau" (?) 20au - "ugeiniau"

    date = []
    day = 0
    if match.group(1):
        day = int(match.group(1))
    elif match.group(2):
        day = int(match.group(2))
    elif match.group(3):
        day = int(match.group(3))
    elif match.group(4):
        day = int(match.group(4))
    date.append(days[day])
    date.append("o")
    month = 0
    if match.group(6):
        month = int(match.group(6))
    elif match.group(7):
        month = int(match.group(7))
    date.append(months[month])
    if match.group(9) in known_years:
        date.append(known_years[match.group(9)])
    else:
        if match.group(9).startswith("20"):
            print(match.group(9), "<")
            date.append(find_numbers(match.group(9)))
        else:
            c = 0
            for digit in match.group(9):
                if c == 2:
                    n_index = digit + match.group(9)[c + 1]
                    if n_index in number_dict:
                        new_word = number_dict[n_index]["lemma"]
                        if new_word:
                            if new_word == "ugain":
                                new_word = "dau ddeg"
                            date.append(new_word)
                            break
                if c == 0 and digit == "1":
                    date.append("mil")
                else:
                    date.append(number_dict[digit]["lemma"])
                c += 1
    return " ".join(date)


def expand_date_welsh(text):
    """
    expand and mutate time
    :param text:
    :return:
    """
    return mutate(re.sub(_time_re, _expand_date_welsh, text), mutations)
