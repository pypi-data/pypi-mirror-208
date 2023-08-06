"""
Time normaliser
"""
import re

from .lookups import mut_numbers, numbers

_time_re = re.compile(
    r"""\b
                          ((0?[0-9])|(1[0-1])|(1[2-9])|(2[0-3]))  # oriau
                          :
                          ([0-5][0-9])                            # munud
                          \s*(y\\.b\\.|yb|yh|y\\.h\\.)? # yb/yh
                          \b""",
    re.IGNORECASE | re.X,
)


def known_times(hour):
    """
    a list of known times that don't follow the normal pattern
    :param hour:
    :return:
    """
    time = ""
    if hour == 12:
        time = "hanner dydd"
    if hour == 0:
        time = "hanner nos"
    return time


def _expand_num(n: int, pre: str) -> str:
    exp_num = numbers[n]
    if pre == "i":
        exp_num = mut_numbers[n]
    return exp_num


def mutate(time_input: str) -> str:
    """
    mutate the know times
    :param time_input:
    :return:
    """
    replacements = [["dau munud", "dau funud"], ["chwech munud", "chwe munud"]]
    for replacement in replacements:
        time_input = time_input.replace(replacement[0], replacement[1])
    return time_input


def _expand_time_welsh(match: "re.Match") -> str:
    time = []
    # nifer munud (wedi/i) nifer awr o'r gloch y bore/nos
    minute = int(match.group(6))
    sep = "i"
    if minute <= 30:
        sep = "wedi"
    hour = int(match.group(1))
    if sep == "i":
        hour += 1
        minute = 60 - minute
    if minute > 0:
        ex_min = _expand_num(minute, "")
        ex_min = ex_min.replace(" ar ", " munud ar ")
        time.append(ex_min)
        if minute not in [15, 30]:
            if "munud" not in ex_min:
                time.append("munud")
        else:
            time.append("awr")
        time.append(sep)
    real_hour = hour
    if hour > 12:
        hour -= 12

    kt = known_times(hour)
    if kt:
        time.append(kt)
    else:
        time.append(_expand_num(hour, sep))
        am_pm = match.group(7)
        if am_pm is not None:
            if "h" in am_pm:
                if real_hour < 12:
                    real_hour += 12
        # bore = 12:01am - 11:59am
        # canol dydd = 12:00 (dydd)
        # prynhawn = 12:01pm - 5:00pm
        # hwyr = 5:01pm - 11:59pm
        if real_hour < 12:
            time.append("y bore")
        elif 12 < real_hour < 18:
            time.append("y prynhawn")
        elif 17 < real_hour < 24:
            time.append("yr hwyr")

    return " ".join(time)


def expand_time_welsh(text: str) -> str:
    """
    expand and mutate time
    :param text:
    :return:
    """
    return mutate(re.sub(_time_re, _expand_time_welsh, text))
