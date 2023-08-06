import logging
from typing import Dict

from tqdm import tqdm

from aleksis.apps.chronos import models as chronos_models
from aleksis.apps.chronos.models import ValidityRange

from .... import models as mysql_models
from ..util import TQDM_DEFAULTS, run_default_filter, untis_date_to_date

logger = logging.getLogger(__name__)


def import_holidays(validity_range: ValidityRange) -> Dict[int, chronos_models.Holiday]:
    """Import holidays."""
    ref = {}

    # Get holidays
    holidays = run_default_filter(validity_range, mysql_models.Holiday.objects, filter_term=False)

    for holiday in tqdm(holidays, desc="Import holidays", **TQDM_DEFAULTS):
        import_ref = holiday.holiday_id

        # Check if needed data are provided
        if not holiday.name:
            raise RuntimeError(
                "Holiday ID {}: Cannot import holiday without short name.".format(import_ref)
            )

        title = holiday.name[:50]
        comments = holiday.longname

        date_start = untis_date_to_date(holiday.datefrom)
        date_end = untis_date_to_date(holiday.dateto)

        logger.info("Import holiday {} …".format(title))

        # Get or create holiday
        new_holiday, created = chronos_models.Holiday.objects.get_or_create(
            import_ref_untis=import_ref,
            defaults={
                "title": title,
                "comments": comments,
                "date_start": date_start,
                "date_end": date_end,
            },
        )

        if created:
            logger.info("  New holiday created")

        if (
            new_holiday.title != title
            or new_holiday.comments != comments
            or new_holiday.date_start != date_start
            or new_holiday.date_end != date_end
        ):
            new_holiday.title = title
            new_holiday.comments = comments
            new_holiday.date_start = date_start
            new_holiday.date_end = date_end
            new_holiday.save()
            logger.info("  Holiday updated")

        ref[import_ref] = new_holiday

    return ref
