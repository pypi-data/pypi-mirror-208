import re

year = r"""
    (
        19[0-9][0-9]| # 1900 to 1999
        2[0-2][0-9][0-9] # 2000 to 2299
    )
    \b # ends with the last digit of the year
"""


year_pattern = re.compile(year, re.X)

p_year = rf""" # parenthesis year (1991)
    \(
    {year}
    \)
"""

b_year = rf""" # bracket year [1991]
    \[
    {year}
    \]
"""

covered_year = rf""" # either a bracket year or a parenthesis year
    (?P<covered_year>
        {p_year}|
        {b_year}
    )
"""
