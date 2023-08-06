from typing import Optional

from django.db.models import Q, QuerySet
from django.utils.functional import classproperty

from aleksis.apps.untis.util.mysql.importers.terms import (
    get_future_terms_for_date,
    get_future_terms_for_date_query,
    get_terms,
    get_terms_for_date,
    get_terms_for_date_query,
)

from .util.mysql.main import untis_import_mysql as _untis_import_mysql


class ImportCommand:
    """A generic Untis import command."""

    name = None

    @classproperty
    def task_name(cls) -> str:  # noqa
        """Get the name for the related Celery task."""
        return f"untis_import_mysql_{cls.name}"

    @classmethod
    def get_terms(cls) -> Optional[QuerySet]:
        """Return which terms should be imported."""
        return None

    @classmethod
    def run(
        cls,
        background: bool = False,
        school_id: Optional[int] = None,
        version: Optional[int] = None,
    ):
        """Run the import command (foreground/background)."""
        if background:
            from .tasks import TASKS

            task = TASKS[cls.task_name]
            task.delay(version=version)
        else:
            _untis_import_mysql(cls.get_terms(), school_id=school_id, version=version)


class CurrentImportCommand(ImportCommand):
    """Import data of current term from Untis."""

    name = "current"

    @classmethod
    def get_terms(cls) -> Optional[QuerySet]:
        return get_terms_for_date()


class FutureImportCommand(ImportCommand):
    """Import data of future terms from Untis."""

    name = "future"

    @classmethod
    def get_terms(cls) -> Optional[QuerySet]:
        return get_future_terms_for_date()


class AllImportCommand(ImportCommand):
    name = "all"


class CurrentNextImportCommand(ImportCommand):
    """Import data of the current and next term from Untis."""

    name = "current_next"

    @classmethod
    def get_terms(cls) -> Optional[QuerySet]:
        future_terms = get_future_terms_for_date()
        if future_terms.exists():
            future_term = future_terms.first()
            return get_terms().filter(
                get_terms_for_date_query()
                | Q(
                    school_id=future_term.school_id,
                    schoolyear_id=future_term.schoolyear_id,
                    version_id=future_term.version_id,
                    term_id=future_term.term_id,
                )
            )
        else:
            return get_terms_for_date()


class CurrentFutureImportCommand(ImportCommand):
    """Import data of the current and future terms from Untis."""

    name = "current_future"

    @classmethod
    def get_terms(cls) -> Optional[QuerySet]:
        terms = get_terms().filter(get_future_terms_for_date_query() | get_terms_for_date_query())
        return terms


COMMANDS_BY_NAME = {c.name: c for c in ImportCommand.__subclasses__()}
COMMANDS_BY_TASK_NAME = {c.task_name: c for c in ImportCommand.__subclasses__()}
