"""
Test building of the lexicon
"""
from techiaith.tts.testun.lexicon import build_lexicon


def test_build_lexicon():
    lexicon = build_lexicon()
    for item in lexicon:
        assert "Gender" in lexicon[item]
