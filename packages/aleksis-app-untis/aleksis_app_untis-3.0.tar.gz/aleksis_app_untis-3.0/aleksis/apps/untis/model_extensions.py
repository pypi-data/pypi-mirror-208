from django.utils.translation import gettext as _

from jsonstore import IntegerField

from aleksis.apps.chronos import models as chronos_models
from aleksis.core import models as core_models

core_models.SchoolTerm.field(
    import_ref_untis=IntegerField(verbose_name=_("Untis import reference"), null=True, blank=True)
)
core_models.Person.field(
    import_ref_untis=IntegerField(verbose_name=_("Untis import reference"), null=True, blank=True)
)
core_models.Group.field(
    import_ref_untis=IntegerField(verbose_name=_("Untis import reference"), null=True, blank=True)
)

# Chronos models
chronos_models.ValidityRange.field(
    import_ref_untis=IntegerField(verbose_name=_("Untis import reference"), null=True, blank=True)
)
chronos_models.ValidityRange.field(
    school_year_untis=IntegerField(verbose_name=_("Untis school year ID"), null=True, blank=True)
)
chronos_models.ValidityRange.field(
    school_id_untis=IntegerField(verbose_name=_("Untis school id"), null=True, blank=True)
)
chronos_models.ValidityRange.field(
    version_id_untis=IntegerField(verbose_name=_("Untis version id"), null=True, blank=True)
)
chronos_models.Subject.field(
    import_ref_untis=IntegerField(verbose_name=_("Untis import reference"), null=True, blank=True)
)
core_models.Room.field(
    import_ref_untis=IntegerField(verbose_name=_("Untis import reference"), null=True, blank=True)
)
chronos_models.SupervisionArea.field(
    import_ref_untis=IntegerField(verbose_name=_("Untis import reference"), null=True, blank=True)
)
chronos_models.Lesson.field(
    lesson_id_untis=IntegerField(verbose_name=_("Lesson id in Untis"), null=True, blank=True)
)
chronos_models.Lesson.field(
    element_id_untis=IntegerField(
        verbose_name=_("Number of lesson element in Untis"), null=True, blank=True
    )
)
chronos_models.LessonPeriod.field(
    element_id_untis=IntegerField(
        verbose_name=_("Number of lesson element in Untis"), null=True, blank=True
    )
)
chronos_models.LessonSubstitution.field(
    import_ref_untis=IntegerField(verbose_name=_("Untis import reference"), null=True, blank=True)
)
chronos_models.LessonSubstitution.field(
    absence_ref_untis=IntegerField(verbose_name=_("Untis absence reference"), null=True, blank=True)
)
chronos_models.SupervisionSubstitution.field(
    import_ref_untis=IntegerField(verbose_name=_("Untis import reference"), null=True, blank=True)
)
chronos_models.AbsenceReason.field(
    import_ref_untis=IntegerField(verbose_name=_("Untis import reference"), null=True, blank=True)
)
chronos_models.Absence.field(
    import_ref_untis=IntegerField(verbose_name=_("Untis import reference"), null=True, blank=True)
)
chronos_models.Event.field(
    import_ref_untis=IntegerField(verbose_name=_("UNTIS import reference"), null=True, blank=True)
)
chronos_models.Holiday.field(
    import_ref_untis=IntegerField(verbose_name=_("UNTIS import reference"), null=True, blank=True)
)
chronos_models.ExtraLesson.field(
    import_ref_untis=IntegerField(verbose_name=_("UNTIS import reference"), null=True, blank=True)
)
chronos_models.Exam.field(
    import_ref_untis=IntegerField(verbose_name=_("UNTIS import reference"), null=True, blank=True)
)
