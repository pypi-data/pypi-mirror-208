from typing import Optional

from django.db.models import QuerySet

import reversion
from tqdm import tqdm

from aleksis.apps.chronos.util.change_tracker import TimetableDataChangeTracker
from aleksis.apps.untis.util.mysql.importers.terms import import_terms
from aleksis.apps.untis.util.mysql.util import TQDM_DEFAULTS

from .importers.absences import import_absences
from .importers.common_data import (
    import_absence_reasons,
    import_breaks,
    import_classes,
    import_rooms,
    import_subjects,
    import_supervision_areas,
    import_teachers,
    import_time_periods,
)
from .importers.events import import_events
from .importers.exams import import_exams
from .importers.holidays import import_holidays
from .importers.lessons import import_lessons
from .importers.substitutions import import_substitutions


def untis_import_mysql(
    terms: Optional[QuerySet] = None, school_id: Optional[int] = None, version: Optional[int] = None
):
    # School terms and validity ranges
    validity_ref = import_terms(terms, school_id=school_id, version=version)

    for validity_range in tqdm(
        validity_ref.values(), desc="Import data for terms", **TQDM_DEFAULTS
    ):
        with reversion.create_revision(atomic=True):
            reversion.set_comment(f"Untis import for validity range {validity_range}")

            tracker = TimetableDataChangeTracker()

            # Common data for Chronos
            subjects_ref = import_subjects(validity_range)
            rooms_ref = import_rooms(validity_range)
            absence_reasons_ref = import_absence_reasons(validity_range)

            # Common data for core
            teachers_ref = import_teachers(validity_range)
            classes_ref = import_classes(validity_range, teachers_ref)

            # Time periods
            time_periods_ref = import_time_periods(validity_range)
            breaks_ref = import_breaks(validity_range, time_periods_ref)

            # Holidays
            holidays_ref = import_holidays(validity_range)

            # Supervisions
            supervision_areas_ref = import_supervision_areas(
                validity_range, breaks_ref, teachers_ref
            )

            # Lessons
            import_lessons(
                validity_range,
                time_periods_ref,
                rooms_ref,
                subjects_ref,
                teachers_ref,
                classes_ref,
            )

            # Substitutions
            __, created_substitutions = import_absences(
                validity_range,
                absence_reasons_ref,
                time_periods_ref,
                teachers_ref,
                classes_ref,
                rooms_ref,
            )
            import_substitutions(
                validity_range,
                teachers_ref,
                subjects_ref,
                rooms_ref,
                classes_ref,
                supervision_areas_ref,
                time_periods_ref,
                created_substitutions,
            )

            # Events
            import_events(validity_range, time_periods_ref, teachers_ref, classes_ref, rooms_ref)

            # Exams
            import_exams(validity_range, time_periods_ref, subjects_ref, teachers_ref, rooms_ref)
