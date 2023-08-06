import logging

from django.db.models import Q
from django.utils.translation import gettext as _

import reversion
from reversion import set_comment
from tqdm import tqdm

from aleksis.apps.chronos import models as chronos_models
from aleksis.apps.chronos.models import ValidityRange
from aleksis.core import models as core_models
from aleksis.core.util.core_helpers import get_site_preferences

from .... import models as mysql_models
from ....data_checks import CourseGroupNotFoundAndCreated, CourseGroupNotFoundAndNotCreated
from ..util import (
    TQDM_DEFAULTS,
    compare_m2m,
    connect_untis_fields,
    run_default_filter,
    untis_split_first,
    untis_split_second,
    untis_split_third,
)

logger = logging.getLogger(__name__)


def import_lessons(
    validity_range: ValidityRange,
    time_periods_ref,
    rooms_ref,
    subjects_ref,
    teachers_ref,
    classes_ref,
):
    """Import lessons."""
    # Lessons
    lessons = run_default_filter(validity_range, mysql_models.Lesson.objects)

    existing_lessons = []
    for lesson in tqdm(lessons, desc="Import lessons", **TQDM_DEFAULTS):
        lesson_id = lesson.lesson_id

        logger.info(_("Import lesson {}").format(lesson_id))

        if not lesson.lesson_tt:
            logger.warning(_("  Skip because missing times").format(lesson_id))
            continue

        existing_lessons.append(lesson_id)

        # Split data (,)
        raw_lesson_data = connect_untis_fields(lesson, "lessonelement", 10)
        raw_time_data = untis_split_first(lesson.lesson_tt, remove_empty=False)

        raw_time_data_2 = []
        for el in raw_time_data:
            # Split data (~)
            raw_time_data_2.append(untis_split_second(el, remove_empty=False))

        # Get time periods and rooms
        time_periods = []
        rooms_per_periods = []
        for el in raw_time_data_2:
            weekday = int(el[1]) - 1
            hour = int(el[2])
            room_ids = untis_split_third(el[3], conv=int)

            # Get rooms
            rooms = []
            for room_id in room_ids:
                r = rooms_ref[room_id]
                rooms.append(r)

            # Get time period
            time_period = time_periods_ref[weekday][hour]
            time_periods.append(time_period)
            rooms_per_periods.append(rooms)

        # Split data more (~)
        raw_lesson_data_2 = []
        for el in raw_lesson_data:
            raw_lesson_data_2.append(untis_split_second(el, remove_empty=False))

        use_room_idx = 0
        current_teacher_id = None
        # All part lessons (courses)
        for i, el in enumerate(raw_lesson_data_2):
            logger.info("  Lesson part {}".format(i))

            # Get plain ids
            teacher_id = int(el[0]) if el[0] else 0
            subject_id = int(el[2])
            class_ids = untis_split_third(el[17], conv=int)

            # Get teacher
            if teacher_id != 0:
                teacher = teachers_ref[teacher_id]
            else:
                teacher = None

            teachers = [teacher] if teacher else []

            # Get subject
            if subject_id != 0:
                subject = subjects_ref[subject_id]
            else:
                logger.warning(_("    Skip because missing subject"))
                continue

            if current_teacher_id and current_teacher_id != teacher_id:
                use_room_idx += 1

            # Get classes
            course_classes = []
            for class_id in class_ids:
                c = classes_ref[class_id]
                course_classes.append(c)

            logger.debug(
                f"    Teacher: {teacher} #{teacher_id}; Subject: {subject} #{subject_id}; "
                f"Classes: {course_classes} #{class_ids}"
            )

            course_group_not_found_and_not_created = False
            if get_site_preferences()["untis_mysql__use_course_groups"]:
                # Negative import_ref denotes a course group
                group_import_ref = -int("{}{}".format(lesson_id, i))

                # Search by parent groups, teachers/owners and subject
                qs = (
                    core_models.Group.objects.filter(
                        parent_groups__in=[c.id for c in course_classes],
                        subject_id=subject.id,
                    )
                    .filter(Q(school_term__isnull=True) | Q(school_term=validity_range.school_term))
                    .distinct()
                )

                if not qs.exists():
                    logger.warning("    No matching course group found")
                else:
                    logger.debug(f"{qs.count()} possibly matching course groups found: {qs}")

                # Check if found groups match
                possible_groups = []
                course_group = None
                for found_group in qs:
                    if compare_m2m(course_classes, found_group.parent_groups.all()):
                        possible_groups.append(found_group)

                logger.debug(
                    f"    {len(possible_groups)} possible groups found "
                    f"by searching by parent groups: {possible_groups}"
                )

                if len(possible_groups) == 1:
                    course_group = possible_groups[0]
                    logger.info(
                        "    Course group found by searching "
                        f"by parent groups, and subject: {course_group}"
                    )
                else:
                    for found_group in possible_groups:
                        if compare_m2m(teachers, found_group.owners.all()):
                            course_group = found_group
                            logger.info(
                                "    Course group found by searching by parent groups, "
                                "teachers (owners) and subject"
                            )

                    if not course_group:
                        logger.debug(
                            "    No course group found by searching "
                            "by parent groups, teachers (owners) and subject"
                        )

                if (
                    not course_group
                    and get_site_preferences()["untis_mysql__course_groups_fuzzy_matching"]
                ):
                    logger.debug("    Fuzzy matching mode used")
                    qs = qs.filter(owners__in=[t.id for t in teachers])
                    if qs.count() != 1:
                        logger.warning(
                            "    Course group not found or more than one found "
                            f"({qs.count()} groups found: {qs}) by searching by parent groups, "
                            "teachers (owners) and subject (fuzzy matching mode)"
                        )
                    else:
                        course_group = qs.first()
                        logger.info(
                            "    Course group found by searching by parent groups, "
                            f"teachers (owners) and subject (fuzzy matching mode): {course_group}"
                        )

                changed = False
                register_data_check = get_site_preferences()[
                    "untis_mysql__data_check_for_not_found_course_groups"
                ]
                if not course_group and get_site_preferences()["untis_mysql__create_course_groups"]:
                    # No matching group found
                    logger.info("    No matching course group found, generate one")

                    # Build names and refs for course groups
                    group_short_name = "{}-{}".format(
                        "".join([c.short_name for c in course_classes]),
                        subject.short_name,
                    )
                    group_name = "{}: {}".format(
                        ", ".join([c.short_name for c in course_classes]),
                        subject.short_name,
                    )

                    # Get or create course group
                    course_group, created = core_models.Group.objects.get_or_create(
                        short_name=group_short_name, defaults={"name": group_name}
                    )

                    # Log
                    if created:
                        logger.info("    Course group created")
                    else:
                        logger.info("    Existing course group found")

                    # Update parent groups
                    course_group.parent_groups.set(course_classes)

                    # Update name
                    if course_group.name != group_name:
                        course_group.name = group_name
                        logger.info("    Name of course group updated")

                        changed = True

                    if created and register_data_check:
                        # No match, new course group created, so create a data problem if activated
                        CourseGroupNotFoundAndCreated.register_result(course_group)
                elif register_data_check:
                    # No match, create deactivated, so create a data problem later if activated
                    course_group_not_found_and_not_created = True

                if course_group:
                    # Update owners
                    course_group.owners.set(teachers)

                    # Update import ref
                    if course_group.import_ref_untis != group_import_ref:
                        course_group.import_ref_untis = group_import_ref
                        logger.info("    Import reference of course group updated")
                        changed = True

                    if course_group.subject != subject:
                        course_group.subject = subject
                        logger.info("    Subject reference of course group updated")
                        changed = True

                    if course_group.school_term != validity_range.school_term:
                        course_group.school_term = validity_range.school_term
                        logger.info("    School term reference of course group updated")
                        changed = True

                    if changed:
                        course_group.save()

                    groups = [course_group]

                else:
                    groups = []
            else:
                groups = course_classes

            # Get old lesson
            old_lesson_qs = chronos_models.Lesson.objects.filter(
                lesson_id_untis=lesson_id, element_id_untis=i, validity=validity_range
            )

            if old_lesson_qs.exists():
                # Update existing lesson
                logger.info("    Existing lesson found")

                old_lesson = old_lesson_qs[0]

                if old_lesson.subject != subject:
                    old_lesson.subject = subject
                    old_lesson.save()
                    logger.info("    Subject updated")
                lesson = old_lesson
            else:
                # Create new lesson

                lesson = chronos_models.Lesson.objects.create(
                    subject=subject,
                    lesson_id_untis=lesson_id,
                    element_id_untis=i,
                    validity=validity_range,
                )
                logger.info("    New lesson created")

            if course_group_not_found_and_not_created:
                # Register data problem here because before the lesson object is unknown
                CourseGroupNotFoundAndNotCreated.register_result(lesson)

            # Sync groups
            if groups:
                lesson.groups.set(groups)

            # Sync teachers
            lesson.teachers.set(teachers)

            # All times for this course
            old_lesson_periods_qs = chronos_models.LessonPeriod.objects.filter(lesson=lesson)

            existing_lesson_period_pks = []

            # Sync time periods
            for j, time_period in enumerate(time_periods):
                logger.info("    Import lesson period {}".format(time_period))

                # Get room if provided
                rooms = rooms_per_periods[j]
                if use_room_idx < len(rooms):
                    room = rooms[use_room_idx]
                else:
                    room = None

                # Check if an old lesson period is provided
                old_lesson_period_qs = old_lesson_periods_qs.filter(period=time_period)
                if old_lesson_period_qs.exists():
                    # Update old lesson period

                    lesson_period = old_lesson_period_qs[0]
                    if lesson_period.room != room or lesson_period.element_id_untis != j:
                        lesson_period.element_id_untis = j
                        lesson_period.room = room
                        lesson_period.save()
                        logger.info("      Untis reference and room updated")
                else:
                    # Create new lesson period

                    lesson_period = chronos_models.LessonPeriod.objects.create(
                        lesson=lesson, period=time_period, room=room, element_id_untis=j
                    )
                    logger.info("      New lesson period added")

                existing_lesson_period_pks.append(lesson_period.pk)

            # delete all no-longer existing lesson periods
            old_lesson_periods_qs.exclude(pk__in=existing_lesson_period_pks).delete()
            logger.info("    Old lesson periods deleted")
            current_teacher_id = teacher_id

    for lesson in chronos_models.Lesson.objects.filter(validity=validity_range):
        if lesson.lesson_id_untis and lesson.lesson_id_untis not in existing_lessons:
            logger.info("Lesson {} deleted".format(lesson.id))
            with reversion.create_revision():
                set_comment(_("Deleted by Untis import"))
                lesson.save()
