import csv
import logging
import re
from datetime import date, datetime
from typing import Any, Callable, Optional, Sequence, Type, Union

from django.db.models import Model, QuerySet

from aleksis.apps.chronos.models import ValidityRange

DB_NAME = "untis"
UNTIS_DATE_FORMAT = "%Y%m%d"

TQDM_DEFAULTS = {
    "disable": None,
    "unit": "obj",
    "dynamic_ncols": True,
}

logger = logging.getLogger(__name__)


def run_using(obj: QuerySet) -> QuerySet:
    """Seed QuerySet with using() database from global DB_NAME."""
    return obj.using(DB_NAME)


def run_default_filter(
    validity_range: ValidityRange,
    qs: QuerySet,
    for_date: Optional[date] = None,
    filter_term: bool = True,
    filter_deleted: bool = True,
) -> QuerySet:
    """Add a default filter in order to select the correct term."""
    term_id, schoolyear_id, school_id, version_id = (
        validity_range.import_ref_untis,
        validity_range.school_year_untis,
        validity_range.school_id_untis,
        validity_range.version_id_untis,
    )

    qs = run_using(qs).filter(
        school_id=school_id,
        schoolyear_id=schoolyear_id,
        version_id=version_id,
    )

    if filter_term:
        qs = qs.filter(term_id=term_id)

    if filter_deleted:
        qs = qs.filter(deleted=0)

    return qs


def clean_array(
    seq: Sequence, conv: Callable[[Any], Any] = lambda el: el, remove_empty: bool = True
) -> Sequence:
    """Clean array.

    Convert a sequence using a converter function, stripping all
    elements that are boolean False after conversion.

    >>> clean_array(["a", "", "b"])
    ['a', 'b']

    >>> clean_array(["8", "", "12", "0"], int)
    [8, 12]
    """
    filtered = filter(
        lambda el: bool(el) or not remove_empty, map(lambda el: conv(el) if el else None, seq)
    )
    return type(seq)(filtered)


class UntisDialect(csv.Dialect):
    """Custom CSV dialect for Untis."""

    quoting = csv.QUOTE_MINIMAL
    quotechar = '"'
    doublequote = True
    lineterminator = "\r\n"


class UntisCommaDialect(UntisDialect):
    """Custom CSV dialect for Untis with comma as delimiter."""

    delimiter = ","


class UntisTildeDialect(UntisDialect):
    """Custom CSV dialect for Untis with tilde as delimiter."""

    delimiter = "~"


class UntisSemicolonDialect(UntisDialect):
    """Custom CSV dialect for Untis with semicolon as delimiter."""

    delimiter = ";"


def split_with_csv_parser(s: str, dialect: Type[csv.Dialect]) -> Sequence:
    """Split string with CSV parser."""
    parsed = csv.reader([s], dialect=dialect)
    return next(parsed)


def untis_split_first(
    s: str, conv: Callable[[Any], Any] = lambda el: el, remove_empty: bool = True
) -> Sequence:
    return clean_array(
        re.findall(r"((?:\"[^\"]+\"|[^,\"]+)*),?", s)[:-1], conv=conv, remove_empty=remove_empty
    )


def untis_split_second(
    s: str, conv: Callable[[Any], Any] = lambda el: el, remove_empty: bool = True
) -> Sequence:
    return clean_array(
        split_with_csv_parser(s, dialect=UntisTildeDialect), conv=conv, remove_empty=remove_empty
    )


def untis_split_third(
    s: str, conv: Callable[[Any], Any] = lambda el: el, remove_empty: bool = True
) -> Sequence:
    return clean_array(
        split_with_csv_parser(s, dialect=UntisSemicolonDialect),
        conv=conv,
        remove_empty=remove_empty,
    )


def untis_date_to_date(untis: int) -> date:
    """Convert a Untis date to a python date."""
    return datetime.strptime(str(untis), UNTIS_DATE_FORMAT).date()


def date_to_untis_date(from_date: date) -> int:
    """Convert a python date to a Untis date."""
    return int(from_date.strftime(UNTIS_DATE_FORMAT))


def untis_colour_to_hex(colour: int) -> str:
    """Convert a numerical colour in BGR order to a standard hex RGB string."""
    # Convert Untis number to HEX
    hex_bgr = str(hex(colour))[2:].zfill(6)

    # Change BGR to RGB
    hex_rgb = hex_bgr[4:6] + hex_bgr[2:4] + hex_bgr[0:2]

    # Add html #
    return "#" + hex_rgb


def compare_m2m(a: Union[Sequence[Model], QuerySet], b: Union[Sequence[Model], QuerySet]) -> bool:
    """Compare if content of two m2m fields is equal."""
    return set(a) == set(b)


def connect_untis_fields(obj: Model, attr: str, limit: int) -> Sequence[str]:
    """Connect data from multiple DB fields.

    Untis splits structured data, like lists, as comma-separated string into
    multiple, numbered database fields, like:

      field1 = "This,is,a,nice"
      field2 = "list,of,words"

    This function joins these fields, then splits them into the original list.
    """
    all_data = []

    for i in range(1, limit + 1):
        attr_name = "{}{}".format(attr, i)
        raw_data = getattr(obj, attr_name, "")
        if raw_data:
            data = untis_split_first(raw_data)
            all_data += data

    return all_data


def get_first_weekday(time_periods_ref: dict) -> int:
    """Get first weekday from time periods reference."""
    return sorted(time_periods_ref.keys())[0]


def get_last_weekday(time_periods_ref: dict) -> int:
    """Get last weekday from time periods reference."""
    return sorted(time_periods_ref.keys())[-1]


def get_first_period(time_periods_ref: dict, weekday: int) -> int:
    """Get first period on a weekday from time periods reference."""
    return sorted(time_periods_ref[weekday].keys())[0]


def get_last_period(time_periods_ref: dict, weekday: int) -> int:
    """Get last period an a weekday from time periods reference."""
    return sorted(time_periods_ref[weekday].keys())[-1]


def move_weekday_to_range(time_periods_ref: dict, weekday: int) -> int:
    """Move weekday values into school week (e. g. saturday to friday)."""
    first_weekday = get_first_weekday(time_periods_ref)
    last_weekday = get_last_weekday(time_periods_ref)

    if weekday < first_weekday:
        weekday = first_weekday
    if weekday > last_weekday:
        weekday = last_weekday

    return weekday
