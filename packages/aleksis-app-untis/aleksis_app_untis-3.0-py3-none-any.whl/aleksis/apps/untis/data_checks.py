from django.utils.translation import gettext_lazy as _

from aleksis.core.data_checks import DataCheck, IgnoreSolveOption


class CourseGroupNotFoundAndCreated(DataCheck):
    name = "untis_mysql_course_group_not_found_and_created"
    verbose_name = _(
        "Course groups created by the Untis import because no matching group has been found."
    )
    problem_name = _(
        "The Untis import created a new course group because no matching group has been found."
    )

    solve_options = {IgnoreSolveOption.name: IgnoreSolveOption}

    @classmethod
    def run_check_data(cls):
        pass


class CourseGroupNotFoundAndNotCreated(DataCheck):
    name = "untis_not_created_not_primary_source"
    verbose_name = _(
        "Course group not set by the Untis import because no matching group has been found."
    )
    problem_name = _(
        "The Untis import didn't set a course group "
        "for a lesson because no matching group has been found."
    )

    solve_options = {IgnoreSolveOption.name: IgnoreSolveOption}

    @classmethod
    def run_check_data(cls):
        pass
