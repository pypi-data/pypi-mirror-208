from django.core.management.base import BaseCommand

from ...commands import COMMANDS_BY_NAME


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "command", nargs="?", default="current", type=str, choices=list(COMMANDS_BY_NAME.keys())
        )
        parser.add_argument(
            "--background",
            action="store_true",
            help="Run import job in background using Celery",
        )
        parser.add_argument(
            "--plan-version",
            help="Select explicit Untis plan version",
        )
        parser.add_argument(
            "--school-id",
            help="Select explicit Untis school ID",
        )

    def handle(self, *args, **options):
        command = COMMANDS_BY_NAME[options["command"]]
        background = options["background"]
        school_id = options.get("school_id", None)
        version = options.get("plan_version", None)
        command.run(background=background, version=version)
