from aleksis.core.celery import app

from .commands import COMMANDS_BY_TASK_NAME, ImportCommand

TASKS = {}
for import_command in ImportCommand.__subclasses__():

    @app.task(name=import_command.task_name, bind=True)
    def _task(self, *args, **kwargs):
        import_command = COMMANDS_BY_TASK_NAME[self.name]
        import_command.run(*args, **kwargs)

    TASKS[import_command.task_name] = _task
