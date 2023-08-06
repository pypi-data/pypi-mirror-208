import datetime
import re
from collections.abc import Iterator
from enum import Enum
from re import Pattern
from typing import Self

from citation_docket import (
    CitationAC,
    CitationAM,
    CitationBM,
    CitationGR,
    CitationOCA,
    CitationPET,
    ShortDocketCategory,
    extract_docket_from_data,
    extract_dockets,
)
from citation_report import Report
from loguru import logger
from pydantic import BaseModel, Field
from slugify import slugify


class Citation(BaseModel):
    """
    A Philippine Supreme Court `Citation` includes fields sourced from:

    1. `Docket` - as defined in [citation-docket](https://github.com/justmars/citation-docket) - includes:
        1. _category_,
        2. _serial number_, and
        3. _date_.
    2. `Report` - as defined in [citation-report](https://github.com/justmars/citation-report) - includes:
        1. _volume number_,
        2. _identifying acronym of the reporter/publisher_,
        3. _page of the reported volume_.

    It is typical to see a `Docket` combined with a `Report`:

    > _Bagong Alyansang Makabayan v. Zamora, G.R. Nos. 138570, 138572, 138587, 138680, 138698, October 10, 2000, 342 SCRA 449_

    Taken together (and using _Bagong Alyansang Makabayan_ as an example) the text above can be extracted into fields:

    Example | Field | Type | Description
    --:|:--:|:--|--:
    GR | `docket_category` | optional (`ShortDocketCategory`) | See shorthand
    138570 |`docket_serial` | optional (str) | See serialized identifier
    datetime.date(2000, 10, 10) | `docket_date` | optional (date) | When docket serial issued
    GR 138570, Oct. 10, 2000 | `docket` | optional (str) | Combined `docket_category` `docket_serial` `docket_date`
    None | `phil` | optional (str) | combined `volume` Phil. `page`
    342 SCRA 449 | `scra` | optional (str) | combined `volume` SCRA `page`
    None | `offg` | optional (str) | combined `volume` O.G. `page`

    Examples:
        >>> text1 = "GR Nos. L-15756; L-15818;  L-16200 and L-16201, Dec. 29, 1962"
        >>> cite1 = next(Citation.extract_citations(text1))
        >>> cite1 == Citation(docket_category='GR', docket_serial='L-15756', docket_date=datetime.date(1962, 12, 29), docket='GR L-15756, Dec. 29, 1962', phil=None, scra=None, offg=None)
        True
        >>> cite1.storage_prefix
        'gr/l-15756/1962/12/29'

    Note that the fields contain a `col` and `index`. These are populated as extra
    Pydantic fields in anticipation of [sqlpyd](https://github.com/justmars/sqlpyd) for
    database processing. Relatedly, the `@slug` can be used as primary key based on
    the consolidated fields.
    """  # noqa: E501

    docket_category: ShortDocketCategory | None = Field(
        None,
        title="Docket Category",
        description="Common categories of PH Supreme Court decisions.",
        col=str,
        index=True,
    )
    docket_serial: str | None = Field(
        None,
        title="Docket Serial Number",
        description="Serialized identifier of docket category.",
        col=str,
        index=True,
    )
    docket_date: datetime.date | None = Field(
        None,
        title="Docket Date",
        description="Distinguishes same category and serial decisions by issuance.",
        col=datetime.date,
        index=True,
    )
    docket: str | None = Field(
        None,
        title="Docket Reference",
        description="Clean parts: category, a single serial id, and date.",
        col=str,
        index=True,
    )
    phil: str | None = Field(
        None,
        title="Philippine Reports",
        description="Combine `volume` Phil. `page` from `citation-report`.",
        col=str,
        index=True,
    )
    scra: str | None = Field(
        None,
        title="Supreme Court Reports Annotated",
        description="Combine `volume` SCRA `page` from `citation-report`.",
        col=str,
        index=True,
    )
    offg: str | None = Field(
        None,
        title="Official Gazette",
        description="Combine `volume` O.G. `page` from `citation-report`.",
        col=str,
        index=True,
    )

    class Config:
        use_enum_values = True
        anystr_strip_whitespace = True

    @property
    def is_statute(self) -> bool:
        """This flag is a special rule to determine whether a combination of category
        and serial number would qualify the citation instance as a statutory pattern
        rather than a decision pattern."""
        if self.docket_category:
            if self.docket_category == ShortDocketCategory.BM:
                if bm_text := self.docket_serial:
                    if CitationBasedStatutes.BAR.pattern.search(bm_text):
                        return True
        return False

    @property
    def has_citation(self):
        """Since each field may be null, check if at least one is not null for it be
        considered a valid citation object.

        Examples:
            >>> text = "AM 07-115-CA-J and CA-08-46-J, Aug. 19, 2008"
            >>> cite = next(Citation.extract_citations(text))
            >>> cite.has_citation
            ['AM 07-115-CA-J, Aug. 19, 2008']

        """
        els = [self.docket, self.scra, self.phil, self.offg]
        values = [el for el in els if el is not None]
        return values

    @property
    def display(self):
        """Combine citation strings into a descriptive string.

        Examples:
            >>> text = "AM 07-115-CA-J and CA-08-46-J, Aug. 19, 2008"
            >>> cite = next(Citation.extract_citations(text))
            >>> cite.display
            'AM 07-115-CA-J, Aug. 19, 2008'
        """
        if self.has_citation:
            return ", ".join(self.has_citation)
        return "No citation detected."

    @property
    def slug(self) -> str | None:
        """If any possible values present, convert instance into slug.

        Examples:
            >>> text = "AM 07-115-CA-J and CA-08-46-J, Aug. 19, 2008"
            >>> cite = next(Citation.extract_citations(text))
            >>> cite.slug
            'am-07-115-ca-j-aug-19-2008'
            >>> data = {"date_prom": "1985-04-24", "docket": "General Register L-63915, April 24, 1985", "orig_idx": "GR No. L-63915", "phil": "220 Phil. 422", "scra": "136 SCRA 27", "offg": None}
            >>> other_cite = Citation.extract_citation_from_data(data)
            >>> other_cite == Citation(docket_category='GR', docket_serial='L-63915', docket_date=datetime.date(1985, 4, 24), docket='GR L-63915, Apr. 24, 1985', phil='220 Phil. 422', scra='136 SCRA 27', offg=None)
            True

        """  # noqa: E501
        if self.has_citation:
            return slugify(" ".join(self.has_citation)).strip()
        return None

    def join_elements(self, separator: str) -> str | None:
        """Results in a functional prefix format:

        Examples:
            >>> text = "AM 07-115-CA-J and CA-08-46-J, Aug. 19, 2008"
            >>> cite = next(Citation.extract_citations(text))
            >>> cite.join_elements("/")  # useful for storage prefixes
            'am/07-115-ca-j/2008/8/19'
            >>> cite.join_elements(".") # useful for primary key creation
            'am.07-115-ca-j.2008.8.19'

        Args:
            separator (str): Should either be a backslash or a period

        Returns:
            str | None: Should only work if the docket citation is available.
        """
        if not self.docket_serial:
            return None
        if not self.docket_category:
            return None
        if not self.docket_date:
            return None
        if separator not in ("/", "."):
            return None
        if "." in self.docket_serial:
            return None
        return separator.join(
            str(i).lower()
            for i in [
                self.docket_category,
                self.docket_serial,
                self.docket_date.year,
                self.docket_date.month,
                self.docket_date.day,
            ]
        )

    @property
    def storage_prefix(self) -> str | None:
        """Create unique identifier from fields only for use as a
        remote storage prefix. The difference between `storage_prefix`
        and `slug` is `storage_prefix` only relates to citations which
        have dockets.

        Examples:
            >>> text = "AM 07-115-CA-J and CA-08-46-J, Aug. 19, 2008"
            >>> cite = next(Citation.extract_citations(text))
            >>> cite.storage_prefix
            'am/07-115-ca-j/2008/8/19'

        Returns:
            str | None: Should only work if the docket citation is available.
        """
        return self.join_elements(separator="/")

    @property
    def prefix_db_key(self) -> str | None:
        """When identifying the statute in the database, need a way
        to combine fields which can be reverted to storage prefix form
        later.  The difference between `prefix_db_key`
        and `slug` is `prefix_db_key` only relates to citations which
        have dockets.

        Examples:
            >>> text = "AM 07-115-CA-J and CA-08-46-J, Aug. 19, 2008"
            >>> cite = next(Citation.extract_citations(text))
            >>> cite.storage_prefix
            'am/07-115-ca-j/2008/8/19'

        Returns:
            str | None: Should only work if the docket citation is available.

        """
        return self.join_elements(separator=".")

    @classmethod
    def extract_citation_from_data(cls, data: dict) -> Self:
        """Direct creation of Citation object based on a specific data dict.

        Examples:
            >>> data = {"date_prom": "1985-04-24", "docket": "General Register L-63915, April 24, 1985", "orig_idx": "GR No. L-63915", "phil": "220 Phil. 422", "scra": "136 SCRA 27", "offg": None}
            >>> Citation.extract_citation_from_data(data).dict()
            {'docket_category': 'GR', 'docket_serial': 'L-63915', 'docket_date': datetime.date(1985, 4, 24), 'docket': 'GR L-63915, Apr. 24, 1985', 'phil': '220 Phil. 422', 'scra': '136 SCRA 27', 'offg': None}

        Args:
            data (dict): See originally scraped `details.yaml` converted to dict

        Returns:
            Citation: A citation object
        """  # noqa: E501
        docket_data = {}
        if cite := extract_docket_from_data(data):  # Set docket, if present.
            docket_data = dict(
                docket=str(cite),  # see Docket __str__
                docket_category=ShortDocketCategory(cite.short_category),
                docket_serial=cite.serial_text,
                docket_date=cite.docket_date,
            )
        return Citation(
            **docket_data,  # type: ignore
            phil=Report.extract_from_dict(data, "phil"),
            scra=Report.extract_from_dict(data, "scra"),
            offg=Report.extract_from_dict(data, "offg"),
        )

    @classmethod
    def extract_id_prefix_citation_from_data(
        cls, data: dict
    ) -> tuple[str, str, Self] | None:
        """Shortcut to determine viability of unique identifiers for a decision
        based on the same dictionary passed to `extract_citation_from_data()`

        Examples:
            >>> data = {"date_prom": "1985-04-24", "docket": "General Register L-63915, April 24, 1985", "orig_idx": "GR No. L-63915", "phil": "220 Phil. 422", "scra": "136 SCRA 27", "offg": None}
            >>> Citation.extract_id_prefix_citation_from_data(data) == ('gr.l-63915.1985.4.24', 'gr/l-63915/1985/4/24', Citation(docket_category='GR', docket_serial='L-63915', docket_date=datetime.date(1985, 4, 24), docket='GR L-63915, Apr. 24, 1985', phil='220 Phil. 422', scra='136 SCRA 27', offg=None))
            True

        Args:
            data (dict): Dict loaded from a details.yaml file with relevant fields. See
                `extract_citation_from_data()`

        Returns:
            tuple[str, str, Self] | None: Docket-based identifiers of the decision based on data dict.
        """  # noqa: E501
        cite = cls.extract_citation_from_data(data)
        if not cite:
            logger.error(f"No citation: {data=}")
            return None

        decision_id = cite.prefix_db_key
        if not decision_id:
            logger.error(f"Bad decision_id in {cite=} {data=}")
            return None

        decision_prefix = cite.storage_prefix
        if not decision_prefix:
            logger.error(f"Bad decision_prefix in {cite=} {data=}")
            return None
        return decision_id, decision_prefix, cite

    @classmethod
    def extract_citations(cls, text: str) -> Iterator[Self]:
        """Combine `Docket`s (which have `Reports`), and filtered `Report` models,
        if they exist.

        Examples:
            >>> text = "<em>Gatchalian Promotions Talent Pool, Inc. v. Atty. Naldoza</em>, 374 Phil 1, 10-11 (1999), citing: <em>In re Almacen</em>, 31 SCRA 562, 600 (1970).; People v. Umayam, G.R. No. 147033, April 30, 2003; <i>Bagong Alyansang Makabayan v. Zamora,</i> G.R. Nos. 138570, 138572, 138587, 138680, 138698, October 10, 2000, 342 SCRA 449; Villegas <em>v.</em> Subido, G.R. No. 31711, Sept. 30, 1971, 41 SCRA 190;"
            >>> results = [c.dict(exclude_none=True) for c in Citation.extract_citations(text)]
            >>> results == [{'docket_category': 'GR', 'docket_serial': '147033', 'docket_date': datetime.date(2003, 4, 30), 'docket': 'GR 147033, Apr. 30, 2003'}, {'docket_category': 'GR', 'docket_serial': '138570', 'docket_date': datetime.date(2000, 10, 10), 'docket': 'GR 138570, Oct. 10, 2000', 'scra': '342 SCRA 449'}, {'docket_category': 'GR', 'docket_serial': '31711', 'docket_date': datetime.date(1971, 9, 30), 'docket': 'GR 31711, Sep. 30, 1971', 'scra': '41 SCRA 190'}, {'scra': '31 SCRA 562'}, {'phil': '374 Phil 1'}]
            True

        Yields:
            Iterator[Self]: Matching Citations found in the text.
        """  # noqa: E501
        from .helpers import filtered_reports

        def extract_report(obj):
            if isinstance(obj, Report):
                return cls(
                    docket=None,
                    docket_category=None,
                    docket_serial=None,
                    docket_date=None,
                    phil=obj.phil,
                    scra=obj.scra,
                    offg=obj.offg,
                )

        def extract_docket(obj):
            options = (
                CitationAC,
                CitationAM,
                CitationOCA,
                CitationBM,
                CitationGR,
                CitationPET,
            )
            if isinstance(obj, options) and obj.ids:
                return cls(
                    docket=str(obj),  # see Docket __str__
                    docket_category=ShortDocketCategory(obj.short_category),
                    docket_serial=obj.serial_text,
                    docket_date=obj.docket_date,
                    phil=obj.phil,
                    scra=obj.scra,
                    offg=obj.offg,
                )

        if dockets := list(extract_dockets(text)):
            if reports := list(Report.extract_report(text)):
                if undocketed := filtered_reports(text, dockets, reports):
                    for docket in dockets:
                        if obj := extract_docket(docket):
                            if not obj.is_statute:
                                yield obj
                    for report in undocketed:
                        if obj := extract_report(report):
                            yield obj
                else:
                    for docket in dockets:
                        if obj := extract_docket(docket):
                            if not obj.is_statute:
                                yield obj
                    for report in reports:
                        if obj := extract_report(report):
                            yield obj
            else:
                for docket in dockets:
                    if obj := extract_docket(docket):
                        if not obj.is_statute:
                            yield obj
        else:
            if reports := list(Report.extract_report(text)):
                for report in reports:
                    if obj := extract_report(report):
                        yield obj

    @classmethod
    def extract_citation(cls, text: str) -> Self | None:
        """Thin wrapper around `cls.extract_citations()`.

        Examples:
            >>> sample = "Gatchalian Promotions Talent Pool, Inc. v. Atty. Naldoza, 374 Phil 1, 10-11 (1999)"
            >>> Citation.extract_citation(sample)
            Citation(docket_category=None, docket_serial=None, docket_date=None, docket=None, phil='374 Phil 1', scra=None, offg=None)

        Args:
            text (str): Text to look for Citations

        Returns:
            Self | None: First matching Citation found in the text.
        """  # noqa: E501
        try:
            return next(cls.extract_citations(text))
        except StopIteration:
            return None


class CitationBasedStatutes(Enum):
    BAR = [
        803,
        1922,
        1645,
        850,
        287,
        1132,
        1755,
        1960,
        209,
        1153,
        411,
        356,
    ]
    ADMIN = [
        r"(?:\d{1,2}-){3}SC\b",
        r"99-10-05-0\b",
    ]

    @property
    def regex(self) -> str:
        return r"(?:" + "|".join(str(i) for i in self.value) + r")"

    @property
    def pattern(self) -> Pattern:
        return re.compile(self.regex)
