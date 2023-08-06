import re
from re import Match, Pattern

from pydantic import BaseModel, Field

separator = r"[\.,\s]*"


class PublisherStyle(BaseModel):
    """Each publisher is represented by a regex expression `regex`.
    The `group_name` should be present in the `regex`.
    """

    label: str = Field(
        ...,
        title="Report style",
        description="Use for uniformity",
    )
    group_name: str = Field(
        ...,
        title="Regex group name",
        description="Custom regex group that identifies the publisher",
    )
    regex: str = Field(
        ...,
        title="Regular expression",
        description=(
            "The regex expression that can be used to extract the various"
            " publisher styles, e.g. 'Phil.' or 'Phil. Report', 'SCRA' or"
            " 'S.C.R.A. Note that all expressions are eventually combined in"
            " `REPORT_PATTERN`."
        ),
    )

    @property
    def pattern(self) -> Pattern:
        return re.compile(self.regex, re.I | re.X)


PHIL = PublisherStyle(
    label="Phil.",
    group_name="PHIL_PUB",
    regex=rf"(?P<PHIL_PUB>phil{separator}(rep)?{separator})",
)  # e.g .4 Phil. Rep., 545

SCRA = PublisherStyle(
    label="SCRA",
    group_name="SCRA_PUB",
    regex=r"(?P<SCRA_PUB>SCRA)",
)

OFFG = PublisherStyle(
    label="O.G.",
    group_name="OG_PUB",
    regex=rf"""(?P<OG_PUB>
                (
                    (
                        o
                        {separator}
                        g
                        {separator}
                    )|
                    (
                        off
                        {separator}
                        gaz(ette)?
                        {separator}
                    )
                )
                (
                    (
                        suppl? # Supp. vs. Suppl.; 47 Off. Gaz. Suppl. 12
                        {separator}
                    )|
                    (
                        \(? # 56 OG (No. 4) 1068
                        no # 49 O.G. No. 7, 2740 (1953),
                        {separator} # 46 O.G. No. 11, 90
                        \d{{1,4}}  # note enclosing brackets
                        \)?
                        {separator}
                    )
                )?
            )
        """,
)


def get_publisher_label(match: Match) -> str | None:
    """Given a regex match object from [Report Pattern][report-pattern],
    determine if it contains a group name representing a Report publisher.

    Examples:
        >>> from citation_report import REPORT_PATTERN, get_publisher_label
        >>> assert REPORT_PATTERN.search("124Phil.1241 statement") is None
        >>> sample = "This is an example 124 Phil. 1241 statement"
        >>> m = REPORT_PATTERN.search(sample)
        >>> m
        <re.Match object; span=(19, 33), match='124 Phil. 1241'>
        >>> label = get_publisher_label(m)
        >>> label
        'Phil.'

    Args:
        match (Match): Based on a prior `re.search` or `re.finditer`
            result on text

    Returns:
        str | None: The first matching publisher found
    """
    for src in [PHIL, SCRA, OFFG]:
        if match.group(src.group_name):
            return src.label
