from django.core.exceptions import ImproperlyConfigured
from django.db import OperationalError, ProgrammingError

from aleksis.core.util.apps import AppConfig


class CSVImportConfig(AppConfig):
    name = "aleksis.apps.csv_import"
    dist_name = "AlekSIS-App-CSVImport"
    verbose_name = "AlekSIS — CSV import"

    urls = {
        "Repository": "https://edugit.org/AlekSIS/official/AlekSIS-App-CSVImport/",
    }
    licence = "EUPL-1.2+"
    copyright_info = (
        ([2019, 2020, 2022], "Dominik George", "dominik.george@teckids.org"),
        ([2020, 2021, 2022], "Jonathan Weth", "dev@jonathanweth.de"),
        ([2019], "mirabilos", "thorsten.glaser@teckids.org"),
        ([2019], "Tom Teichler", "tom.teichler@teckids.org"),
        ([2022], "magicfelix", "felix@felix-zauberer.de"),
    )

    def ready(self):
        super().ready()

        # Create default import templates
        try:
            from aleksis.apps.csv_import.default_templates import (  # noqa
                update_or_create_default_templates,
            )

            update_or_create_default_templates()
        except (ProgrammingError, OperationalError, ImproperlyConfigured) as e:
            # Catch if there are no migrations yet
            pass  # noqa
