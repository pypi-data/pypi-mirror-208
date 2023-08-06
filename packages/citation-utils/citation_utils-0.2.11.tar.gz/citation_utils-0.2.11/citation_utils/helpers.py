from collections.abc import Iterator

from citation_docket import DocketReportCitationType
from citation_report import Report


def help_remove_docketed(
    dockets: list[DocketReportCitationType],
    volpubpage_texts: list[str],
) -> list[str]:
    """Since Dockets contain `Report`s and each `Report` has a volpubpage; edit list of
    volpubpages to exclude volpubpages which are already included in dockets"""
    for docket in dockets:
        if docket.volpubpage:
            if docket.volpubpage in volpubpage_texts:
                volpubpage_texts.remove(docket.volpubpage)
    return volpubpage_texts


def help_clear_docket_reports(
    unique_texts: list[str],
    docketed_reports: list[DocketReportCitationType],
    just_reports: list[Report],
) -> Iterator[Report]:
    """Given text get unique reports (through `volpubpages`) that are not contained
    in the existing list of dockets `ds`"""
    if volpubpages := help_remove_docketed(docketed_reports, unique_texts):
        for v in volpubpages:
            for report in just_reports:
                if report.volpubpage == v:
                    yield report


def filtered_reports(
    raw: str,
    dockets: list[DocketReportCitationType],
    just_reports: list[Report],
) -> list[Report] | None:
    """If separate `Report`s are found; but these are already included in Docket models,
    remove/filter out these redundant `Report`s"""
    if u := Report.get_unique(raw):
        if x_reports := help_clear_docket_reports(u, dockets, just_reports):
            return list(x_reports)
    return None
