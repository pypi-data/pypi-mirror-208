import logging
from datetime import timedelta
from enum import Enum

from calendarweek import CalendarWeek
from tqdm import tqdm

from aleksis.apps.chronos import models as chronos_models
from aleksis.apps.chronos.models import TimePeriod, ValidityRange

from .... import models as mysql_models
from ..util import (
    TQDM_DEFAULTS,
    date_to_untis_date,
    get_first_period,
    get_last_period,
    move_weekday_to_range,
    run_default_filter,
    untis_date_to_date,
)

logger = logging.getLogger(__name__)
unknown_reason, _ = chronos_models.AbsenceReason.objects.get_or_create(short_name="?")


class AbsenceType(Enum):
    GROUP = 100
    TEACHER = 101
    ROOM = 102


def import_absences(
    validity_range: ValidityRange,
    absence_reasons_ref,
    time_periods_ref,
    teachers_ref,
    classes_ref,
    rooms_ref,
):
    ref = {}

    untis_term_start = date_to_untis_date(validity_range.date_start)
    untis_term_end = date_to_untis_date(validity_range.date_end)

    created_substitutions = []

    # Get absences
    absences = (
        run_default_filter(validity_range, mysql_models.Absence.objects, filter_term=False)
        .filter(datefrom__lte=untis_term_end, dateto__gte=untis_term_start)
        .order_by("absence_id")
    )

    existing_absences = []
    for absence in tqdm(absences, desc="Import absences", **TQDM_DEFAULTS):
        import_ref = absence.absence_id

        logger.info("Import absence {}".format(import_ref))

        if absence.absence_reason_id == 0:
            reason = unknown_reason
        else:
            reason = absence_reasons_ref[absence.absence_reason_id]

        # Build values
        type_ = absence.typea
        date_from = untis_date_to_date(absence.datefrom)
        date_to = untis_date_to_date(absence.dateto)
        period_from = absence.lessonfrom
        period_to = absence.lessonto
        weekday_from = date_from.weekday()
        weekday_to = date_to.weekday()

        # Check min/max weekdays
        weekday_from = move_weekday_to_range(time_periods_ref, weekday_from)
        weekday_to = move_weekday_to_range(time_periods_ref, weekday_to)

        # Check min/max periods
        first_period = get_first_period(time_periods_ref, weekday_from)
        last_period = get_last_period(time_periods_ref, weekday_from)

        if period_from == 0:
            period_from = first_period
        if period_to == 0:
            period_to = last_period

        time_period_from = time_periods_ref[weekday_from][period_from]
        time_period_to = time_periods_ref[weekday_to][period_to]
        comment = absence.text

        group = None
        teacher = None
        room = None

        if type_ == AbsenceType.GROUP.value:
            group = classes_ref[absence.ida]
        elif type_ == AbsenceType.TEACHER.value:
            teacher = teachers_ref[absence.ida]
        elif type_ == AbsenceType.ROOM.value:
            room = rooms_ref[absence.ida]

        new_absence, created = chronos_models.Absence.objects.get_or_create(
            import_ref_untis=import_ref,
            defaults={
                "reason": reason,
                "group": group,
                "teacher": teacher,
                "room": room,
                "date_start": date_from,
                "date_end": date_to,
                "period_from": time_period_from,
                "period_to": time_period_to,
                "comment": absence.text,
                "school_term": validity_range.school_term,
            },
        )

        if created:
            logger.info("  New absence created")

        if (
            new_absence.reason != reason
            or new_absence.group != group
            or new_absence.teacher != teacher
            or new_absence.room != room
            or new_absence.date_start != date_from
            or new_absence.date_end != date_to
            or new_absence.period_from != time_period_from
            or new_absence.period_to != time_period_to
            or new_absence.comment != comment
            or new_absence.school_term != validity_range.school_term
        ):
            new_absence.reason = reason
            new_absence.group = group
            new_absence.teacher = teacher
            new_absence.room = room
            new_absence.date_start = date_from
            new_absence.date_end = date_to
            new_absence.period_from = time_period_from
            new_absence.period_to = time_period_to
            new_absence.comment = comment
            new_absence.school_term = validity_range.school_term
            new_absence.save()
            logger.info("  Absence updated")

        existing_absences.append(import_ref)
        ref[import_ref] = new_absence

        if group:
            # If a group is absent, all lessons of this group are cancelled.
            current_date = date_from
            while current_date <= date_to:
                current_period_from = (
                    period_from if current_date == date_from else TimePeriod.period_min
                )
                current_period_to = period_to if current_date == date_to else TimePeriod.period_max

                lesson_periods = (
                    chronos_models.LessonPeriod.objects.filter_group(group)
                    .on_day(current_date)
                    .filter(
                        period__period__gte=current_period_from,
                        period__period__lte=current_period_to,
                    )
                )

                for lesson_period in lesson_periods:
                    week = CalendarWeek.from_date(current_date)
                    sub, __ = chronos_models.LessonSubstitution.objects.get_or_create(
                        lesson_period=lesson_period,
                        week=week.week,
                        year=week.year,
                        defaults=dict(cancelled=True, absence_ref_untis=import_ref),
                    )
                    created_substitutions.append(sub)

                current_date += timedelta(days=1)

    # Delete all no longer existing absences
    for a in chronos_models.Absence.objects.filter(
        date_start__lte=validity_range.date_end, date_end__gte=validity_range.date_start
    ):
        if a.import_ref_untis and a.import_ref_untis not in existing_absences:
            logger.info("Absence {} deleted".format(a.id))
            a.delete()

    return ref, created_substitutions
