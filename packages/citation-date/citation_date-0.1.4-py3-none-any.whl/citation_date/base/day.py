import re

# from: https://stackoverflow.com/questions/6076979/regular-expression-to-match-a-valid-day-in-a-date
day = r"""
    (
        (
            ([0]?[1-9])| # 01-09
            ([1-2][0-9])| # 10-29
            (3[01]) # 30-31
        )
    )
"""

day_pattern = re.compile(day, re.X)
