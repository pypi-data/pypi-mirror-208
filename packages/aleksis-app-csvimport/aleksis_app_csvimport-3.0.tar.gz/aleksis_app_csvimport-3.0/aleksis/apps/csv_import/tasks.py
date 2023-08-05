from aleksis.apps.csv_import.models import ImportJob
from aleksis.core.util.celery_progress import ProgressRecorder, recorded_task

from .util.process import import_csv as _import_csv


@recorded_task
def import_csv(
    import_job: int,
    recorder: ProgressRecorder,
) -> None:
    import_job = ImportJob.objects.get(pk=import_job)
    _import_csv(import_job, recorder)
