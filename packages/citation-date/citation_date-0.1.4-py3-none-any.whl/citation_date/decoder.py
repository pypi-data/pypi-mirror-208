import re
from dataclasses import dataclass
from datetime import date
from re import Match, Pattern

from dateutil.parser import parse

from .base import day, month, year

separator = r"[,\.\s]*"

uk = rf"""
(
    (?P<uk_day>{day})
    {separator}
    (?P<uk_month>{month})
    {separator}
    (?P<uk_year>{year})
)
"""

us = rf"""
(
    (?P<us_month>{month})
    {separator}
    (?P<us_day>{day})
    {separator}
    (?P<us_year>{year})
)
"""

POSSIBLE_DATE: Pattern = re.compile(rf"{us}|{uk}", re.I | re.X)


@dataclass
class DatedText:
    """Uses custom regex for matching date-like objects to deal
    with common typos in citations."""

    raw: str
    match: Match | None = None
    text: str | None = None
    dated: date | None = None

    def __post_init__(self):
        self.match = POSSIBLE_DATE.search(self.raw)
        self.text = self.US or self.UK if self.match else None
        if self.text:
            try:
                self.as_date = parse(self.text).date()
                self.as_string = self.as_date.strftime("%B %d, %Y")
            except Exception:
                self.as_date = None
                self.as_string = None

    @property
    def US(self) -> str | None:
        """If the US variant is found, return the date string.

        Returns:
            str | None: Date in the format: `M D, Y`, if found.
        """
        if self.match and self.match.group("us_day"):
            day = self.match.group("us_day")
            month = self.match.group("us_month")
            year = self.match.group("us_year")
            return f"{month} {day}, {year}"
        return None

    @property
    def UK(self) -> str | None:
        """If the UK variant is found, return the date string.

        Returns:
            str | None: Date in the format: `M D, Y`, if found.
        """
        if self.match and self.match.group("uk_day"):
            day = self.match.group("uk_day")
            month = self.match.group("uk_month")
            year = self.match.group("uk_year")
            return f"{month} {day}, {year}"
        return None


def decode_date(
    text: str, is_output_date_object: bool = False
) -> str | date | None:
    """Given a piece of text, extract the date found using the specific
    constraints of Philippine citations.

    Examples:
        >>> text =  "G.R. No. 12345, Dec,1,  2000"
        >>> decode_date(text)
        'December 01, 2000'
        >>> text1 = "The date is (april29,2001)"
        >>> decode_date(text1)
        'April 29, 2001'
        >>> decode_date(text1, is_output_date_object=True)
        datetime.date(2001, 4, 29)

    Args:
        text (str): Presumably a date string
        is_output_date_object (bool, optional): If True, the return is a
            `datetime.date` object. Defaults to False.

    Returns:
        str | date | None: The decoded text as a date, if it exists.
    """
    obj = DatedText(text)
    if is_output_date_object:
        return obj.as_date
    return obj.as_string
