import re

from .us_uk import uk, us
from .year import covered_year

date = rf"{us}|{uk}"

report_date_variants = rf"""
    (?P<post_report_full_date>
        (?P<naked_date>
            {us}|{uk}
        )|
        (
            \[ # open bracket
            (?P<brackets_date>
                {us}|{uk}
            )
            \] # close bracket
        )|
        (
            \( # open parenthesis
            (?P<parents_date>
                {us}|{uk}
            )
            \) # close parenthesis
        )
    )
    """
"""
US / UK regex cannot contain group names since these
will be used as alternative patterns, i.e. as bracketed us / uk dates,
parenthesis etc.
"""

dates_pattern = re.compile(report_date_variants, re.X | re.I)

REPORT_DATE_REGEX = rf"""
    (?P<report_date>
        {covered_year}|
        {report_date_variants}
    )
"""
"""An example of a `Report` (referring to a reporter / publisher citation)
containing a date is "1 SCRA 200 `<date>`". See `citation-report` library on
how the `report_date` group name of a matched regex expression can be extracted
from a piece of text.

Examples:
    >>> from citation_date import REPORT_DATE_REGEX, decode_date
    >>> import re
    >>> pattern = re.compile(REPORT_DATE_REGEX, re.I | re.X)  # note flags
    >>> text = "1 SCRA 200 (1Dec.  2000)" # this is what a report looks like
    >>> sample_match = pattern.search(text)
    >>> sample_match.group("report_date")
    "(1Dec.  2000)"
    >>> decode_date(sample_match.group("report_date")) # use the regex group name
    "2000-12-01"
"""
