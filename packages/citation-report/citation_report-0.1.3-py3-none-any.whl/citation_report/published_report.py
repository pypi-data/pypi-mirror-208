import re
from re import Pattern

from citation_date import REPORT_DATE_REGEX

from .publisher import OFFG, PHIL, SCRA

PUBLISHERS_REGEX = rf"""
    (?P<publisher>
        {SCRA.regex}| # contains SCRA_PUB group name
        {PHIL.regex}| # contains PHIL_PUB group name
        {OFFG.regex} # contains OG_PUB group name
    )
"""
"""A partial regex string containing the Publisher options available."""


volume = r"""
    \b
    (?P<volume>
        [12]? # makes possible from 1000 to 2999
        \d{1,3}
        (
            \-A| # See Central Bank v. CA, 159-A Phil. 21, 34 (1975);
            a
        )?
    )
    \b
"""

page = r"""
    \b
    (?P<page>
        [12345]? # makes possible from 1000 to 5999
        \d{1,3}  # 49 Off. Gazette 4857
    )
    \b
"""

volpubpage = rf"""
    (?P<volpubpage>
        {volume}
        \s+
        {PUBLISHERS_REGEX}
        \s+
        {page}
    )
"""

filler = r"""
    (?P<filler>
        [\d\-\.]{1,10}
    )
"""

extra = rf"""
    (?:
        (?:
            [\,\s,\-]*
            {filler}
        )?
        [\,\s]*
        {REPORT_DATE_REGEX}
    )?
"""

REPORT_REGEX = rf"{volpubpage}{extra}"

REPORT_PATTERN: Pattern = re.compile(REPORT_REGEX, re.X | re.I)
"""A compiled regex expression that enables capturing the
parts of a report.

Examples:
    >>> from citation_report import REPORT_PATTERN
    >>> text = "42 SCRA 109, 117-118, October 29, 1971;"
    >>> sample_match = REPORT_PATTERN.search(text)
    >>> sample_match.group("volpubpage")
    '42 SCRA 109'
    >>> sample_match.group("volume")
    '42 SCRA 109'
    >>> sample_match.group("publisher")
    'SCRA'
    >>> sample_match.group("page")
    '109'
    >>> sample_match.group("REPORT_DATE_REGEX")
    'October 29, 1971'
"""
