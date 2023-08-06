"""
Make a lexicon of words and their gender
"""
import importlib.resources as ir

from . import data


def build_lexicon():
    """
    build a dict lookup from the lexicon file
    :return:
    """
    lex = ir.read_text(data, "lecsicon_cc0.txt")
    lexicon = {}
    for line in lex.splitlines():
        if "Gender" in line:
            cells = line.split("\t")
            for cell in cells:
                if "Gender" in cell:
                    lexicon[cells[0]] = cell[cell.index("Gender") :]
                    break
    return lexicon
