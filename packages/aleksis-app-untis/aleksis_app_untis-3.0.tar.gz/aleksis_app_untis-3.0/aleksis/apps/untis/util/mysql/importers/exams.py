import logging

from django.utils.translation import gettext as _

from calendarweek import CalendarWeek
from tqdm import tqdm

from aleksis.apps.chronos import models as chronos_models
from aleksis.apps.chronos.models import ExtraLesson, Lesson, ValidityRange

from .... import models as mysql_models
from ..util import (
    TQDM_DEFAULTS,
    connect_untis_fields,
    date_to_untis_date,
    get_first_period,
    get_last_period,
    move_weekday_to_range,
    run_default_filter,
    untis_date_to_date,
    untis_split_second,
)

logger = logging.getLogger(__name__)


def import_exams(
    validity_range: ValidityRange,
    time_periods_ref,
    subjects_ref,
    teachers_ref,
    rooms_ref,
):
    ref = {}

    # Get absences
    exams = (
        run_default_filter(validity_range, mysql_models.Exam.objects, filter_term=False)
        .filter(
            date__lte=date_to_untis_date(validity_range.date_end),
            date__gte=date_to_untis_date(validity_range.date_start),
        )
        .order_by("exam_id")
    )

    existing_exams = []
    for exam in tqdm(exams, desc="Import exams", **TQDM_DEFAULTS):
        import_ref = exam.exam_id

        logger.info("Import exam {}".format(import_ref))

        # Build values
        title = exam.name or ""
        comment = exam.text or ""

        day = untis_date_to_date(exam.date)
        period_from = exam.lessonfrom
        period_to = exam.lessonto

        weekday = day.weekday()
        week = CalendarWeek.from_date(day)

        # Check min/max weekdays
        weekday = move_weekday_to_range(time_periods_ref, weekday)

        # Check min/max periods
        first_period = get_first_period(time_periods_ref, weekday)
        last_period = get_last_period(time_periods_ref, weekday)

        if period_from == 0:
            period_from = first_period
        if period_to == 0:
            period_to = last_period

        time_period_from = time_periods_ref[weekday][period_from]
        time_period_to = time_periods_ref[weekday][period_to]

        # Get groups, teachers and rooms
        raw_exams = connect_untis_fields(exam, "examelement", 10)
        first = True
        lesson = None
        subject = None
        exams = []
        for raw_exam in raw_exams:
            el = untis_split_second(raw_exam, remove_empty=False)
            if first:
                lesson_id = int(el[0])
                subject_id = int(el[1])
                lesson = Lesson.objects.get(validity=validity_range, lesson_id_untis=lesson_id)
                subject = subjects_ref[subject_id] if subject_id in subjects_ref else None
            first = False
            period = int(el[4])
            if not period:
                logger.warning("  Skip incomplete exam element")
                continue
            period = time_periods_ref[weekday][period]
            teacher_id = int(el[5])
            room_id = int(el[6])
            teacher = teachers_ref[teacher_id] if teacher_id in teachers_ref else None
            room = rooms_ref[room_id] if room_id in rooms_ref else None
            exams.append((period, teacher, room))

        if not lesson or not subject or not exams:
            logger.warning("  Skip exam due to missing data.")
            continue

        new_exam, created = chronos_models.Exam.objects.update_or_create(
            import_ref_untis=import_ref,
            defaults={
                "date": day,
                "lesson": lesson,
                "period_from": time_period_from,
                "period_to": time_period_to,
                "title": title,
                "comment": comment,
                "school_term": validity_range.school_term,
            },
        )

        if created:
            logger.info("  New exam created")

        extra_lesson_pks = []
        for exam in exams:
            period, teacher, room = exam
            comment = new_exam.title or _("Exam")
            extra_lesson, __ = ExtraLesson.objects.get_or_create(
                exam=new_exam,
                period=period,
                defaults={
                    "room": room,
                    "week": week.week,
                    "year": week.year,
                    "comment": comment,
                    "subject": subject,
                },
            )
            if (
                extra_lesson.room != room
                or extra_lesson.week != week.week
                or extra_lesson.year != week.year
                or extra_lesson.comment != comment
                or extra_lesson.subject != subject
            ):
                extra_lesson.room = room
                extra_lesson.week = week.week
                extra_lesson.year = week.year
                extra_lesson.comment = comment
                extra_lesson.subject = subject
                extra_lesson.save()

            extra_lesson.groups.set(lesson.groups.all())
            extra_lesson.teachers.set([teacher])

            extra_lesson_pks.append(extra_lesson.pk)

        # Delete no-longer necessary extra lessons
        ExtraLesson.objects.filter(exam=new_exam).exclude(pk__in=extra_lesson_pks).delete()

        existing_exams.append(import_ref)
        ref[import_ref] = new_exam

        # Delete all no longer existing exams
        for e in chronos_models.Exam.objects.within_dates(
            validity_range.date_start, validity_range.date_end
        ):
            if e.import_ref_untis and e.import_ref_untis not in existing_exams:
                logger.info(f"  Exam {e.id} deleted")
                e.delete()
