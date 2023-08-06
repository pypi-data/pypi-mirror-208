import logging
import re
from datetime import time
from enum import Enum
from typing import Dict

from tqdm import tqdm

from aleksis.apps.chronos import models as chronos_models
from aleksis.apps.chronos.models import ValidityRange
from aleksis.core import models as core_models
from aleksis.core.util.core_helpers import get_site_preferences

from .... import models as mysql_models
from ..util import (
    TQDM_DEFAULTS,
    connect_untis_fields,
    run_default_filter,
    untis_colour_to_hex,
    untis_split_first,
    untis_split_second,
)

logger = logging.getLogger(__name__)


class CommonDataId(Enum):
    PERIOD = 40


def import_subjects(validity_range: ValidityRange) -> Dict[int, chronos_models.Subject]:
    """Import subjects."""
    subjects_ref = {}

    # Get subjects
    subjects = run_default_filter(validity_range, mysql_models.Subjects.objects, filter_term=False)

    for subject in tqdm(subjects, desc="Import subjects", **TQDM_DEFAULTS):
        # Check if needed data are provided
        if not subject.name:
            raise RuntimeError(
                "Subject ID {}: Cannot import subject without short name.".format(
                    subject.subject_id
                )
            )

        # Build values
        short_name = subject.name[:10]
        name = subject.longname if subject.longname else short_name
        colour_fg = untis_colour_to_hex(subject.forecolor)
        colour_bg = untis_colour_to_hex(subject.backcolor)
        import_ref = subject.subject_id

        logger.info("Import subject {} …".format(short_name))

        # Get or create subject object by short name
        new_subject, created = chronos_models.Subject.objects.get_or_create(
            short_name=short_name,
            defaults={
                "name": name,
                "colour_fg": colour_fg,
                "colour_bg": colour_bg,
                "import_ref_untis": import_ref,
            },
        )

        if created:
            logger.info("  New subject created")

        # Force sync
        changed = False
        if get_site_preferences()["untis_mysql__update_subjects"] and (
            new_subject.name != name
            or new_subject.colour_fg != colour_fg
            or new_subject.colour_bg != colour_bg
        ):
            new_subject.name = name
            new_subject.colour_fg = untis_colour_to_hex(subject.forecolor)
            new_subject.colour_bg = untis_colour_to_hex(subject.backcolor)
            changed = True

            logger.info("  Name, foreground and background colour updated")

        if new_subject.import_ref_untis != import_ref:
            new_subject.import_ref_untis = import_ref
            changed = True

            logger.info("  Import reference updated")

        if changed:
            new_subject.save()

        subjects_ref[import_ref] = new_subject

    return subjects_ref


def import_teachers(validity_range: ValidityRange) -> Dict[int, core_models.Person]:
    """Import teachers."""
    teachers_ref = {}

    # Get teachers
    teachers = run_default_filter(validity_range, mysql_models.Teacher.objects)

    for teacher in tqdm(teachers, desc="Import teachers", **TQDM_DEFAULTS):
        # Check if needed data are provided
        if not teacher.name:
            raise RuntimeError(
                "Teacher ID {}: Cannot import teacher without short name.".format(
                    teacher.teacher_id
                )
            )

        # Build values
        short_name = teacher.name
        first_name = teacher.firstname if teacher.firstname else "?"
        last_name = teacher.longname if teacher.longname else teacher.name
        import_ref = teacher.teacher_id

        logger.info("Import teacher {} (as person) …".format(short_name))

        try:
            new_teacher = core_models.Person.objects.get(short_name__iexact=short_name)
        except core_models.Person.DoesNotExist:
            new_teacher = core_models.Person.objects.create(
                short_name=short_name,
                first_name=first_name,
                last_name=last_name,
                import_ref_untis=import_ref,
            )
            logger.info("  New person created")

        changed = False
        if get_site_preferences()["untis_mysql__update_persons_name"] and (
            new_teacher.first_name != first_name or new_teacher.last_name != last_name
        ):
            new_teacher.first_name = first_name
            new_teacher.last_name = last_name
            changed = True
            logger.info("  First and last name updated")

        if (
            get_site_preferences()["untis_mysql__update_persons_short_name"]
            and new_teacher.short_name != short_name
        ):
            new_teacher.short_name = short_name
            changed = True
            logger.info("  Short name updated")

        if new_teacher.import_ref_untis != import_ref:
            new_teacher.import_ref_untis = import_ref
            changed = True
            logger.info("  Import reference updated")

        if changed:
            new_teacher.save()

        teachers_ref[teacher.teacher_id] = new_teacher

    return teachers_ref


def import_classes(
    validity_range: ValidityRange, teachers_ref: Dict[int, core_models.Person]
) -> Dict[int, core_models.Group]:
    """Import classes."""
    classes_ref = {}

    # Get classes
    course_classes = run_default_filter(
        validity_range, mysql_models.Class.objects, filter_term=True
    )

    for class_ in tqdm(course_classes, desc="Import classes", **TQDM_DEFAULTS):
        # Check if needed data are provided
        if not class_.name:
            raise RuntimeError(
                "Class ID {}: Cannot import class without short name.".format(class_.teacher_id)
            )

        # Build values
        short_name = class_.name[:16]
        name = class_.longname if class_.longname else short_name
        teacher_ids = untis_split_first(class_.teacherids, int) if class_.teacherids else []
        owners = [teachers_ref[t_id] for t_id in teacher_ids]
        import_ref = class_.class_id

        logger.info("Import class {} (as group) …".format(short_name))

        try:
            new_group = core_models.Group.objects.get(
                short_name__iexact=short_name,
                school_term__in=[None, validity_range.school_term],
            )
        except core_models.Group.DoesNotExist:
            # Determine collisions of long name
            while core_models.Group.objects.filter(
                name=name, school_term=validity_range.school_term
            ).exists():
                if not get_site_preferences()["untis_mysql__disambiguate_groups_name"]:
                    # Do not try to disambiguate it not enabled
                    break

                suffix = f" ({short_name})"
                if name.endswith(suffix):
                    # First try, add a counter
                    name = f"{name} (2)"
                else:
                    # Second or more tries, determine last counter, if any
                    match = re.match(r"^(.*)(\(\d+\))$", name)
                    if match:
                        # Counter found, increase
                        prefix = match.group(1)
                        counter = int(match.group(2)) + 1
                        name = f"{prefix}({counter})"
                    else:
                        # Counter not found, add one
                        name = f"{name} (2)"

            new_group = core_models.Group.objects.create(
                short_name=short_name,
                name=name,
                import_ref_untis=import_ref,
                school_term=validity_range.school_term,
            )
            logger.info("  New group created")

        changed = False

        if (
            get_site_preferences()["untis_mysql__update_groups_short_name"]
            and new_group.short_name != short_name
        ):
            new_group.short_name = short_name
            changed = True
            logger.info("  Short name updated")

        if get_site_preferences()["untis_mysql__update_groups_name"] and new_group.name != name:
            new_group.name = name
            changed = True
            logger.info("  Name updated")

        if new_group.import_ref_untis != import_ref:
            new_group.import_ref_untis = import_ref
            changed = True
            logger.info("  Import reference updated")

        if new_group.school_term != validity_range.school_term:
            new_group.school_term = validity_range.school_term
            changed = True
            logger.info("  School term updated")

        if changed:
            new_group.save()

        if get_site_preferences()["untis_mysql__overwrite_group_owners"]:
            new_group.owners.set(owners)
            logger.info("  Group owners set")
        else:
            new_group.owners.add(*owners)
            logger.info("  Group owners added")

        classes_ref[class_.class_id] = new_group

    return classes_ref


def import_rooms(validity_range: ValidityRange) -> Dict[int, core_models.Room]:
    """Import rooms."""
    ref = {}

    # Get rooms
    rooms = run_default_filter(validity_range, mysql_models.Room.objects)

    for room in tqdm(rooms, desc="Import rooms", **TQDM_DEFAULTS):
        if not room.name:
            raise RuntimeError(
                "Room ID {}: Cannot import room without short name.".format(room.room_id)
            )

        # Build values
        short_name = room.name[:10]
        name = room.longname[:30] if room.longname else short_name
        import_ref = room.room_id

        logger.info("Import room {} …".format(short_name))

        new_room, created = core_models.Room.objects.get_or_create(
            short_name=short_name,
            defaults={"name": name, "import_ref_untis": import_ref},
        )

        if created:
            logger.info("  New room created")

        changed = False

        if get_site_preferences()["untis_mysql__update_rooms_name"] and new_room.name != name:
            new_room.name = name
            changed = True
            logger.info("  Name updated")

        if new_room.import_ref_untis != import_ref:
            new_room.import_ref_untis = import_ref
            changed = True
            logger.info("  Import reference updated")

        if changed:
            new_room.save()

        ref[import_ref] = new_room

    return ref


def import_supervision_areas(
    validity_range: ValidityRange, breaks_ref, teachers_ref
) -> Dict[int, chronos_models.SupervisionArea]:
    """Import supervision areas."""
    ref = {}

    # Get supervision areas
    areas = run_default_filter(validity_range, mysql_models.Corridor.objects, filter_term=False)

    for area in tqdm(areas, desc="Import supervision areas", **TQDM_DEFAULTS):
        if not area.name:
            raise RuntimeError(
                "Supervision area ID {}: Cannot import supervision area without short name.".format(
                    area.corridor_id
                )
            )

        short_name = area.name[:10]
        name = area.longname[:50] if area.longname else short_name
        colour_fg = untis_colour_to_hex(area.forecolor)
        colour_bg = untis_colour_to_hex(area.backcolor)
        import_ref = area.corridor_id

        logger.info("Import supervision area {} …".format(short_name))

        new_area, created = chronos_models.SupervisionArea.objects.get_or_create(
            short_name=short_name,
            defaults={
                "name": name,
                "colour_fg": colour_fg,
                "colour_bg": colour_bg,
                "import_ref_untis": import_ref,
            },
        )

        if created:
            logger.info("  New supervision area created")

        changed = False

        if get_site_preferences()["untis_mysql__update_supervision_areas"] and (
            new_area.name != new_area.name
            or new_area.colour_fg != colour_fg
            or new_area.colour_bg != colour_bg
        ):
            new_area.name = name
            new_area.colour_fg = colour_fg
            new_area.colour_bg = colour_bg
            changed = True

            logger.info("  Name, foreground and background colour updated")

        if new_area.import_ref_untis != import_ref:
            new_area.import_ref_untis = import_ref
            changed = True
            logger.info("  Import reference updated")

        if changed:
            new_area.save()

        logger.info("  Import supervisions for this area")

        # Parse raw data
        raw_supervisions = connect_untis_fields(area, "breaksupervision", 16)

        supervisions_ref = {}
        for raw_supervision in raw_supervisions:
            # Split more and get teacher id
            raw_supervision_2 = untis_split_second(raw_supervision, remove_empty=False)
            teacher_id = int(raw_supervision_2[1])
            term_id = int(raw_supervision_2[0])

            if term_id != validity_range.import_ref_untis:
                continue

            if teacher_id in teachers_ref:
                # Get weekday, period after break and teacher
                weekday = int(raw_supervision_2[2]) - 1
                period_after_break = int(raw_supervision_2[3])
                teacher = teachers_ref[teacher_id]

                logger.info(
                    "Import supervision on weekday {} before the {}. period (teacher {})".format(
                        weekday, period_after_break, teacher
                    )
                )

                # Get or create
                new_supervision, created = new_area.supervisions.get_or_create(
                    validity=validity_range,
                    break_item=breaks_ref[weekday][period_after_break],
                    teacher=teacher,
                )

                # Log
                if created:
                    logger.info("      New supervision created")

                # Save supervisions in reference dict
                if weekday not in supervisions_ref:
                    supervisions_ref[weekday] = {}
                if period_after_break not in supervisions_ref[weekday]:
                    supervisions_ref[weekday][period_after_break] = []
                supervisions_ref[weekday][period_after_break].append(new_supervision)

        for supervision in new_area.supervisions.filter(validity=validity_range):
            delete = True

            # Get weekday and period after break
            weekday = supervision.break_item.weekday
            period_after_break = supervision.break_item.before_period_number

            # Delete supervision if no longer existing
            if weekday in supervisions_ref:
                if period_after_break in supervisions_ref[weekday]:
                    if supervision in supervisions_ref[weekday][period_after_break]:
                        delete = False

            if delete:
                supervision.delete()
                logger.info("    Supervision {} deleted".format(supervision))

        ref[import_ref] = {"area": new_area, "supervisions": supervisions_ref}

    return ref


def import_time_periods(
    validity_range: ValidityRange,
) -> Dict[int, Dict[int, chronos_models.TimePeriod]]:
    """Import time periods an breaks."""
    times = (
        run_default_filter(validity_range, mysql_models.Commondata.objects, filter_term=False)
        .filter(id=30)
        .order_by("number")
    )

    times_ref = {}
    for time_ in tqdm(times, desc="Import times", **TQDM_DEFAULTS):
        period = time_.number

        # Extract time
        start_time = time(time_.fieldbyte1, time_.fieldbyte2)
        end_time = time(time_.fieldbyte3, time_.fieldbyte4)

        times_ref[period] = (start_time, end_time)

    periods = (
        run_default_filter(validity_range, mysql_models.Commondata.objects, filter_term=False)
        .filter(id=CommonDataId.PERIOD.value)
        .order_by("number", "number1")
    )

    time_periods_ref = {}
    for time_period in tqdm(periods, desc="Import time periods", **TQDM_DEFAULTS):
        weekday = time_period.number - 1
        period = time_period.number1
        start_time = times_ref[period][0]
        end_time = times_ref[period][1]

        logger.info("Import time period on weekday {} in the {}. period".format(weekday, period))

        new_time_period, created = chronos_models.TimePeriod.objects.get_or_create(
            weekday=weekday,
            period=period,
            validity=validity_range,
            defaults={"time_start": start_time, "time_end": end_time},
        )

        if created:
            logger.info("  New time period created")

        if new_time_period.time_start != start_time or new_time_period.time_end != end_time:
            new_time_period.time_start = start_time
            new_time_period.time_end = end_time
            new_time_period.save()
            logger.info("  Time period updated")

        # Build index with time periods
        if weekday not in time_periods_ref:
            time_periods_ref[weekday] = {}
        time_periods_ref[weekday][period] = new_time_period

    return time_periods_ref


def import_breaks(
    validity_range: ValidityRange,
    time_periods_ref: Dict[int, Dict[int, chronos_models.TimePeriod]],
) -> Dict[int, Dict[int, chronos_models.Break]]:
    # Build breaks for all weekdays
    breaks_ref = {}
    for weekday, time_periods in tqdm(
        time_periods_ref.items(), desc="Import breaks (weekday)", **TQDM_DEFAULTS
    ):
        breaks_ref[weekday] = {}

        # Add None two times in order to create breaks before first lesson and after last lesson
        time_periods_for_breaks = [None] + list(time_periods.values()) + [None]
        for i, time_period in tqdm(
            enumerate(time_periods_for_breaks), desc="Import breaks (period)", **TQDM_DEFAULTS
        ):
            # If last item (None) is reached, no further break must be created
            if i + 1 == len(time_periods_for_breaks):
                break

            after_period = time_period
            before_period = time_periods_for_breaks[i + 1]

            short_name = "{}: {}./{}.".format(
                weekday,
                after_period.period if after_period else "-",
                before_period.period if before_period else "-",
            )

            logger.info("Generate break {}".format(short_name))

            new_break, created = chronos_models.Break.objects.get_or_create(
                after_period=after_period,
                before_period=before_period,
                validity=validity_range,
                defaults={"short_name": short_name, "name": short_name},
            )

            if created:
                logger.info("  New break created")

            # Save index with lesson after break
            next_period = new_break.before_period_number
            breaks_ref[weekday][next_period] = new_break

    return breaks_ref


def import_absence_reasons(
    validity_range: ValidityRange,
) -> Dict[int, chronos_models.AbsenceReason]:
    """Import absence reasons."""
    ref = {}

    # Get reasons
    reasons = run_default_filter(
        validity_range, mysql_models.Absencereason.objects, filter_term=False
    )

    for reason in tqdm(reasons, desc="Import absence reasons", **TQDM_DEFAULTS):
        if not reason.name:
            raise RuntimeError(
                "Absence reason ID {}: Cannot import absence reason without short name.".format(
                    reason.absence_reason_id
                )
            )

        # Build values
        short_name = reason.name
        name = reason.longname if reason.longname else short_name
        import_ref = reason.absence_reason_id

        logger.info("Import absence reason {} …".format(short_name))

        new_reason, created = chronos_models.AbsenceReason.objects.get_or_create(
            import_ref_untis=import_ref,
            defaults={"short_name": short_name, "name": name},
        )

        if created:
            logger.info("  New absence reason created")

        changed = False

        if new_reason.short_name != short_name or new_reason.name != name:
            new_reason.short_name = short_name
            new_reason.name = name
            changed = True
            logger.info("  Short name and name updated")

        if changed:
            new_reason.save()

        ref[import_ref] = new_reason

    return ref
