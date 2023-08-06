import re

month = r"""(
    (?:
        Jan(?:uary)?|
        Feb(?:ruary)?|
        Mar(?:ch)?|
        Apr(?:il)?|
        May|
        Jun(?:e)?|
        Jul(?:y)?|
        Aug(?:ust)?|
        Sep(?:tember)?|
        Sept|
        Oct(?:ober)?|
        (Nov|Dec)(?:ember)?
    )
)
"""

month_pattern = re.compile(month, re.X | re.I)
