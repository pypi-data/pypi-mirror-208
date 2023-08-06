from django.db import migrations

from aleksis.core.util.core_helpers import get_site_preferences


def guess_school_id(apps, schema_editor):
    db_alias = schema_editor.connection.alias

    from aleksis.apps.chronos.models import ValidityRange

    try:
        vr = ValidityRange.objects.using(db_alias).first()
    except ValidityRange.DoesNotExist:
        return

    if not vr or not vr.school_id_untis:
        return

    get_site_preferences()["untis_mysql__school_id"] = school_id


class Migration(migrations.Migration):

    dependencies = [
        ('untis', '0002_auto_20200820_1542'),
    ]

    operations = [
        migrations.RunPython(guess_school_id),
    ]
