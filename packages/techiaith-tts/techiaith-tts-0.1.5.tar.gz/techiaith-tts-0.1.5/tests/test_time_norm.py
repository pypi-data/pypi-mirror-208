"""
Test time normalisation
"""
from techiaith.tts.testun.time_norm import expand_time_welsh

# bore = 12:01am - 11:59am
# canol dydd = 12:00 (dydd)
# prynhawn = 12:01pm - 5:00pm
# hwyr = 5:01pm - 11:59pm


tests = [
    ["12:30yh", "hanner awr wedi hanner dydd"],
    ["08:30", "hanner awr wedi wyth y bore"],
    ["20:30", "hanner awr wedi wyth yr hwyr"],
    ["16:01", "un munud wedi pedwar y prynhawn"],
    ["04:01 yb", "un munud wedi pedwar y bore"],
    ["5:15 yb", "chwarter awr wedi pump y bore"],
    ["4:45 yh", "chwarter awr i bump y prynhawn"],
    ["16:22", "dau funud ar hugain wedi pedwar y prynhawn"],
    ["16:34", "chwe munud ar hugain i bump y prynhawn"],
    ["17:22", "dau funud ar hugain wedi pump y prynhawn"],
    ["17:34", "chwe munud ar hugain i chwech yr hwyr"],
    ["Dwi am fynd adref cyn 12:00", "Dwi am fynd adref cyn hanner dydd"],
    ["Dwi am fynd adref cyn 00:00", "Dwi am fynd adref cyn hanner nos"],
]


def test_time():
    for time in tests:
        result = expand_time_welsh(time[0])
        assert result == time[1]
