import os.path

from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from aleksis.core.models import SchoolTerm
from aleksis.core.util import messages

from ...models import ImportJob, ImportTemplate
from ...tasks import import_csv
from ...util.process import import_csv as import_csv_base


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "csv_path",
            help=_("Path to CSV file"),
        )
        parser.add_argument(
            "template",
            help=_("Name of import template which should be used"),
        )
        parser.add_argument(
            "--school-term",
            help=_("ID of School term to which the imported objects should belong"),
            type=int,
        )
        parser.add_argument(
            "--background",
            action="store_true",
            help="Run import job in background using Celery",
        )

    def handle(self, *args, **options):
        template_name = options["template"]
        try:
            template = ImportTemplate.objects.get(name=template_name)
        except ImportTemplate.DoesNotExist:
            messages.error(None, _("The provided template does not exist."))
            return

        try:
            pk = options["school_term"]
            school_term = SchoolTerm.objects.get(pk=pk)
        except SchoolTerm.DoesNotExist:
            school_term = None

        filename = os.path.split(options["csv_path"])[1]

        import_job = ImportJob(template=template, school_term=school_term)
        with open(options["csv_path"], "r") as csv_file:
            import_job.data_file.save(filename, csv_file)
        import_job.save()

        if options["background"]:
            import_csv.delay(import_job.pk)
        else:
            import_csv_base(import_job)
