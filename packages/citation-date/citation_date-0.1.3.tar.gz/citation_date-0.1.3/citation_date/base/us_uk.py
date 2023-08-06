import re

from .day import day
from .month import month
from .year import year

separator = r"[,\.\s]*"

uk = rf"""
(
    {day}
    {separator}
    {month}
    {separator}
    {year}
)
"""

uk_pattern = re.compile(uk, re.X | re.I)

us = rf"""
(
    {month}
    {separator}
    {day}
    {separator}
    {year}
)
"""

us_pattern = re.compile(us, re.X | re.I)

DOCKET_DATE_REGEX = rf"""
    (?P<docket_date>
        {us}|{uk}
    )
"""
"""An example of a Docket number containing a date is "G.R. No. 12345, `<date>`".
See `citation-docket` library on how the `docket_date` group name
of a matched regex expression can be extracted from a piece of text.

Examples:
    >>> from citation_date import DOCKET_DATE_REGEX
    >>> import re
    >>> pattern = re.compile(DOCKET_DATE_REGEX, re.I | re.X)  # note flags
    >>> text = "G.R. No. 12345, Dec,1,  2000" # this is what a docket looks like
    >>> sample_match = pattern.search(text)
    >>> sample_match.group("docket_date")
    "Dec,1,  2000"
    >>> decode_date(sample_match.group("docket_date")) # use the regex group name
    "December 01, 2000"
"""

DOCKET_DATE_FORMAT = "%b. %d, %Y"
"""Utilizes a uniform docket format of `%b. %d, %Y`, e.g. Jan. 2, 1994, for dates to
be usable downstream."""
