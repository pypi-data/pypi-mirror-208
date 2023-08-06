import logging
from datetime import date, timedelta
from typing import Dict, Optional

from django.db.models import Max, OuterRef, Q, QuerySet, Subquery
from django.utils import timezone

from tqdm import tqdm

from aleksis.apps.chronos import models as chronos_models
from aleksis.apps.untis.util.mysql.util import (
    TQDM_DEFAULTS,
    date_to_untis_date,
    run_using,
    untis_date_to_date,
)
from aleksis.core import models as core_models
from aleksis.core.util.core_helpers import get_site_preferences

from .... import models as mysql_models


def get_terms() -> QuerySet:
    """Get all terms."""
    return run_using(mysql_models.Terms.objects).order_by("datefrom")


def get_terms_for_date_query(for_date: Optional[date] = None) -> QuerySet:
    """Get term query object with term valid for the provided date."""
    if not for_date:
        for_date = timezone.now().date()

    return Q(datefrom__lte=date_to_untis_date(for_date), dateto__gte=date_to_untis_date(for_date))


def get_terms_for_date(for_date: Optional[date] = None) -> QuerySet:
    """Get term queryset with term valid for the provided date."""
    qs = get_terms().filter(get_terms_for_date_query(for_date))

    return qs


def get_future_terms_for_date_query(for_date: Optional[date] = None) -> QuerySet:
    """Get term query object with all future terms."""
    if not for_date:
        for_date = timezone.now().date()

    return Q(datefrom__gt=date_to_untis_date(for_date))


def get_future_terms_for_date(for_date: Optional[date] = None) -> QuerySet:
    """Get all future terms (after the current term)."""
    qs = get_terms().filter(get_future_terms_for_date_query(for_date))

    return qs


logger = logging.getLogger(__name__)


def import_terms(
    qs: Optional[QuerySet] = None,
    school_id: Optional[int] = None,
    version: Optional[int] = None,
) -> Dict[int, chronos_models.ValidityRange]:
    """Import terms and school years as validity ranges and school terms."""
    ranges_ref = {}

    if not isinstance(qs, QuerySet):
        qs = run_using(mysql_models.Terms.objects)

    if school_id is None:
        school_id = get_site_preferences()["untis_mysql__school_id"]
    qs = qs.filter(school_id=school_id).order_by("datefrom")

    if version is None:
        # Select newest version per term / validity range
        sub_qs = (
            run_using(mysql_models.Terms.objects)
            .filter(
                school_id=OuterRef("school_id"),
                schoolyear_id=OuterRef("schoolyear_id"),
                term_id=OuterRef("term_id"),
            )
            .values("school_id", "schoolyear_id", "term_id")
            .annotate(max_version=Max("version_id"))
            .values("max_version")
        )
        qs = qs.filter(version_id=Subquery(sub_qs))
    else:
        # Select passed version
        qs = qs.filter(version_id=version)

    school_terms = {}
    for term in tqdm(qs, desc="Import terms (as validity ranges)", **TQDM_DEFAULTS):
        if not term.name:
            raise RuntimeError(
                "Term ID {}: Cannot import term without short name.".format(term.term_id)
            )
        term_id = term.term_id
        name = term.longname if term.longname else term.name
        date_start = untis_date_to_date(term.datefrom)
        date_end = untis_date_to_date(term.dateto)

        logger.info(f"Import term {term_id} ({date_start}–{date_end})")

        school_year_id = term.schoolyear_id
        try:
            school_term = core_models.SchoolTerm.objects.within_dates(date_start, date_end).get()
            logger.info("    School term found by time.")
        except core_models.SchoolTerm.DoesNotExist:
            if school_year_id in school_terms:
                school_term = school_terms[school_year_id]
                logger.info(f"  School year {school_year_id} already there.")
            else:
                school_year = run_using(mysql_models.Schoolyear.objects).get(
                    schoolyear_id=school_year_id
                )
                school_term_name = (
                    school_year.text if school_year.text else school_year.schoolyearzoned
                )

                logger.info(f"  Import school year {school_year_id} ...")

                try:
                    school_term = core_models.SchoolTerm.objects.get(
                        import_ref_untis=school_year_id
                    )
                    logger.info("    School year found by import reference.")
                except core_models.SchoolTerm.DoesNotExist:
                    school_term = core_models.SchoolTerm(
                        date_start=date_start, date_end=date_end, name=school_term_name
                    )
                    logger.info("    School year created newly.")

            school_term.import_ref_untis = school_year_id

        if school_term.date_end < date_end:
            school_term.date_end = date_end

        if school_term.date_start > date_start:
            school_term.date_start = date_start

        school_term.save()
        school_terms[school_year_id] = school_term

        try:
            validity_range = chronos_models.ValidityRange.objects.get(
                import_ref_untis=term_id, school_term=school_term
            )
            logger.info("  Validity range found by import reference.")
        except chronos_models.ValidityRange.DoesNotExist:
            try:
                validity_range = chronos_models.ValidityRange.objects.within_dates(
                    date_start__gte=date_start, date_end__lte=date_end
                ).get()
                logger.info("  Validity range found by time.")
            except chronos_models.ValidityRange.DoesNotExist:
                validity_range = chronos_models.ValidityRange()
                logger.info("  Validity range created newly.")

        # In Untis, you can set all the end dates of the terms to the same date
        # and despite that, the terms still end if a new one starts.
        # If this case occurs, we have to set the end date of the previous term
        # to the start date of the next one.
        validity_range_with_possible_intersection = chronos_models.ValidityRange.objects.filter(
            date_end__gte=date_start, date_start__lt=date_start
        ).first()
        if validity_range_with_possible_intersection:
            validity_range_with_possible_intersection.date_end = date_start - timedelta(days=1)
            validity_range_with_possible_intersection.save()

        validity_range.import_ref_untis = term_id
        validity_range.date_start = date_start
        validity_range.date_end = date_end
        validity_range.name = name
        validity_range.school_term = school_term
        validity_range.school_year_untis = school_year_id
        validity_range.school_id_untis = term.school_id
        validity_range.version_id_untis = term.version_id

        validity_range.save()

        ranges_ref[validity_range] = validity_range

    return ranges_ref
