"""
Test known_phrases
"""
from techiaith.tts.testun.known_phrases import replace_phrase

# ERAILL POSIB: S4C ("es pedwar ec")


def test_replace_phrase():
    expected = "gwefan yw golwg tri chwech dim"
    result = replace_phrase("gwefan yw golwg360")
    assert expected == result
