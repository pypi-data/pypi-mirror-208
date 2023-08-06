import logging
from enum import Enum

from django.db.models import Q

from calendarweek import CalendarWeek
from tqdm import tqdm

from aleksis.apps.chronos import models as chronos_models
from aleksis.apps.chronos.models import ValidityRange
from aleksis.core.util.core_helpers import get_site_preferences

from .... import models as mysql_models
from ..util import (
    TQDM_DEFAULTS,
    date_to_untis_date,
    run_default_filter,
    untis_date_to_date,
    untis_split_first,
)

logger = logging.getLogger(__name__)


class SubstitutionFlag(Enum):
    CANCELLED = "E"
    CANCELLED_FOR_TEACHERS = "F"


def import_substitutions(
    validity_range: ValidityRange,
    teachers_ref,
    subjects_ref,
    rooms_ref,
    classes_ref,
    supervision_areas_ref,
    time_periods_ref,
    absence_substitutions=None,
):
    """Import substitutions."""
    if not absence_substitutions:
        absence_substitutions = []
    absence_substitutions = [sub.absence_ref_untis for sub in absence_substitutions]

    subs = (
        run_default_filter(validity_range, mysql_models.Substitution.objects, filter_term=False)
        .filter(
            date__gte=date_to_untis_date(validity_range.date_start),
            date__lte=date_to_untis_date(validity_range.date_end),
        )
        .exclude(
            Q(flags__contains="N")
            | Q(flags__contains="b")
            | Q(flags__contains="F")
            | Q(flags__exact="g")
        )
        .order_by("substitution_id")
    )

    existing_subs = []
    for sub in tqdm(subs, desc="Import substitutions", **TQDM_DEFAULTS):
        # IDs
        sub_id = sub.substitution_id
        existing_subs.append(sub_id)

        lesson_id = sub.lesson_idsubst

        logger.info("Import substitution {}".format(sub_id))

        # Time
        date = untis_date_to_date(sub.date)
        weekday = date.weekday()
        week = CalendarWeek.from_date(date)
        period = sub.lesson

        # Supervision substitution?
        is_supervision_substitution = sub.corridor_id != 0

        # Cancellation?
        cancelled, cancelled_for_teachers = False, False
        if SubstitutionFlag.CANCELLED.value in sub.flags:
            cancelled = True
        elif SubstitutionFlag.CANCELLED_FOR_TEACHERS.value in sub.flags:
            cancelled_for_teachers = True

        # Comment
        comment = sub.text

        # Teacher
        if sub.teacher_idlessn != 0:
            teacher_old = teachers_ref[sub.teacher_idlessn]
        else:
            teacher_old = None

        teachers = []
        teacher_new = None
        if sub.teacher_idsubst != 0:
            teacher_new = teachers_ref[sub.teacher_idsubst]
            teachers = [teacher_new]

            if teacher_old is not None and teacher_new.id == teacher_old.id:
                teachers = []

        if not is_supervision_substitution:
            lesson_periods = chronos_models.LessonPeriod.objects.filter(
                lesson__validity=validity_range,
                lesson__lesson_id_untis=lesson_id,
                lesson__teachers=teacher_old,
                period__period=period,
                period__weekday=weekday,
            ).on_day(date)

            if lesson_periods.exists():
                lesson_period = lesson_periods[0]
                logger.info("  Matching lesson period found ({})".format(lesson_period))
            else:
                lesson_period = None

            # Subject
            subject_old = lesson_period.lesson.subject if lesson_period else None
            subject_new = None
            if sub.subject_idsubst != 0:
                subject_new = subjects_ref[sub.subject_idsubst]

                if subject_old and subject_old.id == subject_new.id:
                    subject_new = None

            if cancelled:
                subject_new = None

            # Room
            room_old = lesson_period.room if lesson_period else None
            room_new = None
            if sub.room_idsubst != 0:
                room_new = rooms_ref[sub.room_idsubst]

                if room_old is not None and room_old.id == room_new.id:
                    room_new = None

            # Classes
            classes = []
            class_ids = untis_split_first(sub.classids, conv=int)

            for id_ in class_ids:
                classes.append(classes_ref[id_])

            if get_site_preferences()["untis_mysql__ignore_incomplete_substitutions"]:
                # Skip incomplete substitutions
                if (
                    not room_new
                    and not subject_new
                    and not teachers
                    and not cancelled
                    and not cancelled_for_teachers
                    and not comment
                ):
                    continue

            if lesson_period:
                (
                    substitution,
                    created,
                ) = chronos_models.LessonSubstitution.objects.get_or_create(
                    lesson_period=lesson_period, week=week.week, year=week.year
                )

                if created:
                    logger.info("  Substitution created")

                # Sync teachers
                substitution.teachers.set(teachers)
                logger.info("   Substitution teachers set")

                # Update values
                if (
                    substitution.subject != subject_new
                    or substitution.room != room_new
                    or substitution.cancelled != cancelled
                    or substitution.cancelled_for_teachers != cancelled_for_teachers
                    or substitution.comment != comment
                    or substitution.import_ref_untis != sub_id
                ):
                    substitution.subject = subject_new
                    substitution.room = room_new
                    substitution.cancelled = cancelled
                    substitution.cancelled_for_teachers = cancelled_for_teachers
                    substitution.comment = comment
                    substitution.import_ref_untis = sub_id
                    substitution.save()
                    logger.info("  Substitution updated")

            else:
                logger.info("  Extra lesson detected")
                time_period = time_periods_ref[date.weekday()][period]

                groups = [classes_ref[pk] for pk in untis_split_first(sub.classids, int)]

                room = room_old if not room_new and room_old else room_new
                subject = subject_old if not subject_new else subject_new
                teachers = [teacher_old] if not teacher_new else [teacher_new]
                if not teacher_new and not teacher_old:
                    teachers = []

                if not subject:
                    logger.warning("  Skip because missing subject")
                    continue

                (
                    extra_lesson,
                    created,
                ) = (
                    chronos_models.ExtraLesson.objects.select_related(None)
                    .prefetch_related(None)
                    .update_or_create(
                        import_ref_untis=sub_id,
                        defaults={
                            "week": week.week,
                            "year": week.year,
                            "period": time_period,
                            "subject": subject,
                            "room": room,
                            "comment": comment,
                            "school_term": validity_range.school_term,
                        },
                    )
                )

                if created:
                    logger.info("  Extra lesson created")

                extra_lesson.teachers.set(teachers)
                extra_lesson.groups.set(groups)
        else:
            if teacher_new:
                logger.info("  Supervision substitution detected")

                # Supervision
                area_ref = supervision_areas_ref[sub.corridor_id]
                possible_supervisions = area_ref["supervisions"][weekday][period]

                supervision = None
                for possible_supervision in possible_supervisions:
                    if possible_supervision.teacher == teacher_old:
                        supervision = possible_supervision

                if supervision:
                    (
                        substitution,
                        created,
                    ) = chronos_models.SupervisionSubstitution.objects.get_or_create(
                        supervision=supervision,
                        date=date,
                        defaults={"teacher": teacher_new},
                    )

                    if created:
                        logger.info("  Supervision substitution created")

                    if (
                        substitution.teacher != teacher_new
                        or substitution.import_ref_untis != sub_id
                    ):
                        substitution.teacher = teacher_new
                        substitution.import_ref_untis = sub_id
                        substitution.save()
                        logger.info("  Supervision substitution updated")

    # Delete all no longer existing substitutions
    lesson_substitutions_in_range = chronos_models.LessonSubstitution.objects.within_dates(
        validity_range.date_start, validity_range.date_end
    )
    for s in lesson_substitutions_in_range:
        if (s.import_ref_untis and s.import_ref_untis not in existing_subs) or (
            s.absence_ref_untis and s.absence_ref_untis not in absence_substitutions
        ):
            logger.info("Substitution {} deleted".format(s.id))
            s.delete()

    lesson_substitutions_in_range.exclude(lesson_period__lesson__validity=validity_range).delete()

    # Delete all no longer existing extra lessons
    for s in chronos_models.ExtraLesson.objects.within_dates(
        validity_range.date_start, validity_range.date_end
    ):
        if s.import_ref_untis and s.import_ref_untis not in existing_subs:
            logger.info("Extra lesson {} deleted".format(s.id))
            s.delete()

    # Delete all no longer existing supervision substitutions
    supervision_substitutions_in_range = chronos_models.SupervisionSubstitution.objects.filter(
        date__gte=validity_range.date_start, date__lte=validity_range.date_end
    )
    for s in supervision_substitutions_in_range:
        if s.import_ref_untis and s.import_ref_untis not in existing_subs:
            logger.info("Supervision substitution {} deleted".format(s.id))
            s.delete()

    supervision_substitutions_in_range.exclude(supervision__validity=validity_range).delete()
