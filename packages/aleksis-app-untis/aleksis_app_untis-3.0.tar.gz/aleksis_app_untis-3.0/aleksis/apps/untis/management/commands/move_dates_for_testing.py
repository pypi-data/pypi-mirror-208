from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from calendarweek import CalendarWeek
from tqdm import tqdm

from aleksis.apps.chronos.models import (
    Absence,
    Event,
    Exam,
    ExtraLesson,
    Holiday,
    LessonSubstitution,
    ValidityRange,
)
from aleksis.core.models import SchoolTerm


class Command(BaseCommand):
    help = "Move all dates to current school year"  # noqa

    def add_arguments(self, parser):
        parser.add_argument("--dry", action="store_true")

    def translate_date_start_end(self, name: str, qs):
        self.stdout.write(name.upper())
        for instance in tqdm(qs):
            date_start = instance.date_start
            date_end = instance.date_end
            date_start_new = date_start + self.time_delta
            date_end_new = date_end + self.time_delta
            self.stdout.write(f"{date_start} → {date_start_new}; {date_end} → {date_end_new}")
            instance.date_start = date_start_new
            instance.date_end = date_end_new
            if not self.dry:
                instance.save()

    def translate_date(self, name: str, qs):
        self.stdout.write(name.upper())
        for instance in tqdm(qs):
            date_old = instance.date
            date_new = date_old + self.time_delta
            self.stdout.write(f"{date_old} → {date_new}")
            instance.date = date_new
            if not self.dry:
                instance.save()

    def translate_week_year(self, name: str, qs):
        self.stdout.write(name.upper())
        for instance in tqdm(qs):
            date_old = instance.date
            date_new = instance.date + self.time_delta
            week_new = CalendarWeek.from_date(date_new)
            self.stdout.write(f"{date_old}, {instance.week} → {date_new}, {week_new.week}")
            instance.year = date_new.year
            instance.week = week_new.week
            if not self.dry:
                instance.save()

    def handle(self, *args, **options):
        self.dry = options["dry"]

        school_terms = SchoolTerm.objects.order_by("-date_end")

        if not school_terms.exists():
            raise RuntimeError("No school term available.")

        school_term = school_terms.first()
        self.stdout.write(f"Used school term: {school_term}")

        date_start = school_term.date_start
        date_end = school_term.date_end
        current_date = timezone.now().date()
        current_year = current_date.year
        if date_start.month <= current_date.month and date_start.day < current_date.day:
            current_year -= 1
        date_end = date(year=current_year, day=date_start.day, month=date_start.month)
        self.stdout.write(f"{current_year}, {date_end}")
        days = (date_end - date_start).days
        self.weeks = round(days / 7)
        self.time_delta = timedelta(days=self.weeks * 7)
        self.stdout.write(f"{days}, {self.weeks}")

        self.translate_date_start_end("SCHOOL TERM", [school_term])

        self.translate_date_start_end(
            "VALIDITY RANGES", ValidityRange.objects.filter(school_term=school_term)
        )

        if not self.weeks:
            self.stdout.write(self.style.ERROR("There are no data that have to be moved."))
            return

        self.translate_week_year(
            "SUBSTITUTIONS",
            LessonSubstitution.objects.filter(
                lesson_period__lesson__validity__school_term=school_term
            ),
        )
        self.translate_week_year(
            "EXTRA LESSONS", ExtraLesson.objects.filter(school_term=school_term)
        )
        self.translate_date_start_end("ABSENCES", Absence.objects.filter(school_term=school_term))
        self.translate_date("EXAMS", Exam.objects.filter(school_term=school_term))
        self.translate_date_start_end(
            "HOLIDAYS", Holiday.objects.within_dates(date_start, date_end)
        )
        self.translate_date_start_end("EVENTS", Event.objects.filter(school_term=school_term))
