import datetime
from collections.abc import Iterator
from typing import Self

from dateutil.parser import parse
from pydantic import BaseModel, Field

from .published_report import REPORT_PATTERN
from .publisher import OFFG, PHIL, SCRA, get_publisher_label


class Report(BaseModel):
    """The [REPORT_PATTERN][report-pattern] is a `re.Pattern` object that
    contains pre-defined regex group names. These group names can be mapped
    to the `Report` model's fields:

    Field | Type | Description
    --:|:--:|:--
    `publisher` | optional (str) | Type of the publisher.
    `volume` | optional (str) | Publisher volume number.
    `page` | optional (str) | Publisher volume page.
    `volpubpage` | optional (str) | Combined fields: <volume> <publisher> <page>
    `report_date` | optional (date) | Optional date associated with the report citation

    It's important that each field be **optional**. The `Report` will be joined
    to another `BaseModel` object, i.e. the `Docket`, in a third-party library.
    It must be stressed that the `Report` object is only one part of
    the eventual `DockerReportCitation` object. It can:

    1. have both a `Docket` and a `Report`,
    2. have just a `Docket`;
    3. have just a `Report`.

    If the value of the property exists, it represents whole `volpubpage` value.

    1. `@phil`
    2. `@scra`
    3. `@offg`
    """

    publisher: str | None = Field(
        None,
        title="Report Publisher",
        description=(
            "Shorthand label of the publisher involved, e.g. SCRA, Phil. Offg"
        ),
        max_length=5,
    )
    volume: str | None = Field(
        None,
        title="Volume Number",
        description=(
            "Publisher volume number - may not be a full digit since it can"
            " exceptionally include letters."
        ),
        max_length=10,
    )
    page: str | None = Field(
        None,
        title="Page Number",
        description="The page number of the publisher volume involved",
        max_length=5,
    )
    volpubpage: str | None = Field(
        None,
        title="Volume Publisher Page",
        description="Full expression of the report citation",
        max_length=20,
    )
    report_date: datetime.date | None = Field(
        None,
        title="Report Date",
        description="Exceptionally, report citations reference dates.",
    )

    def __str__(self) -> str:
        return self.volpubpage or ""

    @property
    def phil(self):
        return self.volpubpage if self.publisher == PHIL.label else None

    @property
    def scra(self):
        return self.volpubpage if self.publisher == SCRA.label else None

    @property
    def offg(self):
        return self.volpubpage if self.publisher == OFFG.label else None

    @classmethod
    def extract_report(cls, text: str) -> Iterator[Self]:
        """Given sample legalese `text`, extract all Supreme Court `Report` patterns.

        Examples:
            >>> sample = "250 Phil. 271, 271-272, Jan. 1, 2019"
            >>> report = next(Report.extract(sample))
            >>> type(report)
            citation_report.__main__.Report
            >>> report.volpubpage
            '250 Phil. 271'

        Args:
            text (str): Text containing report citations.

        Yields:
            Iterator[Self]: Iterator of `Report` instances
        """
        for match in REPORT_PATTERN.finditer(text):
            report_date = None
            if text := match.group("report_date"):
                try:
                    report_date = parse(text).date()
                except Exception:
                    report_date = None

            publisher = get_publisher_label(match)
            volume = match.group("volume")
            page = match.group("page")

            if publisher and volume and page:
                yield Report(
                    publisher=publisher,
                    volume=volume,
                    page=page,
                    volpubpage=match.group("volpubpage"),
                    report_date=report_date,
                )

    @classmethod
    def extract_from_dict(cls, data: dict, report_type: str) -> str | None:
        """Assuming a dictionary with any of the following report_type keys
        `scra`, `phil` or `offg`, get the value of the Report property.

        Examples:
            >>> sample_data = {"scra": "14 SCRA 314"} # dict
            >>> Report.extract_from_dict(sample_data, "scra")
            '14 SCRA 314'

        Args:
            data (dict): A `dict` containing a possible report `{key: value}`
            report_type (str): Must be either "scra", "phil", or "offg"

        Returns:
            str | None: The value of the key `report_type` in the `data` dict.
        """
        if report_type.lower() in ["scra", "phil", "offg"]:
            if candidate := data.get(report_type):
                try:
                    obj = next(cls.extract_report(candidate))
                    # will get the @property of the Report with the same name
                    if hasattr(obj, report_type):
                        return obj.__getattribute__(report_type)
                except StopIteration:
                    return None
        return None

    @classmethod
    def get_unique(cls, text: str) -> list[str]:
        """Will only get `Report` volpubpages (string) from the text. This
        is used later in `citation_utils` to prevent duplicate citations.

        Examples:
            >>> text = "(22 Phil. 303; 22 Phil. 303; 176 SCRA 240; Peñalosa v. Tuason, 22 Phil. 303, 313 (1912); Heirs of Roxas v. Galido, 108 Phil. 582 (1960)); Valmonte v. PCSO, supra; Bugnay Const. and Dev. Corp. v. Laron, 176 SCRA 240 (1989)"
            >>> Report.get_unique(text)
            ['22 Phil. 303', '108 Phil. 582', '176 SCRA 240']

        Args:
            text (str): Text to search for report patterns

        Returns:
            list[str]: Unique report `volpubpage` strings found in the text
        """  # noqa: E501
        return list(
            {r.volpubpage for r in cls.extract_report(text) if r.volpubpage}
        )
