import logging
import os
from glob import glob
from tempfile import TemporaryDirectory
from typing import Optional
from zipfile import ZipFile

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.template import Context, Template
from django.utils.translation import gettext as _

import chardet
import pandas
from pandas.errors import ParserError
from tqdm import tqdm

from aleksis.apps.csv_import.field_types import (
    DirectMappingFieldType,
    MatchFieldType,
    ProcessFieldType,
)
from aleksis.apps.csv_import.settings import FALSE_VALUES, TRUE_VALUES
from aleksis.core.models import Group, Person
from aleksis.core.util.celery_progress import ProgressRecorder
from aleksis.core.util.core_helpers import process_custom_context_processors

from ..models import ImportJob


@transaction.atomic
def import_csv(
    import_job: ImportJob,
    recorder: Optional[ProgressRecorder] = None,
) -> None:
    """Import one CSV/ZIP file from a job."""
    # We work in a temporary directory locally to allow more import scenarios,
    # like ZIP files that need to be preprocessed
    with TemporaryDirectory() as temp_dir:
        # Get the job and the target of the import
        template = import_job.template
        model = template.content_type.model_class()
        school_term = import_job.school_term

        # Dissect template definition
        # These structures will be filled with information for columns
        data_types = {}
        converters = {}
        field_types = {}
        virtual_fields = []
        for field in template.fields.all():
            # Get field type and prepare for import
            field_type = field.field_type_class(school_term, temp_dir, **field.args)
            column_name = field_type.get_column_name()

            if not field.virtual:
                # Get data type and conversion rules, if any,
                # to be passed to Pandas
                data_types[column_name] = field_type.get_data_type()
                if field_type.get_converter():
                    converters[column_name] = field_type.get_converter()
            else:
                # Mark field as virtual so as to not handle with Pandas
                virtual_fields.append(column_name)
                field_type.template = field.virtual_tmpl

            field_types[column_name] = field_type

        # Determine whether the data file is a plain CSV or an archive
        if import_job.data_file.name.endswith(".zip"):
            # Unpack to temporary directory
            with ZipFile(import_job.data_file.open("rb")) as zip_file:
                zip_file.extractall(temp_dir)

            # Find all CSV files
            csv_names = glob(os.path.join(temp_dir, "*.csv")) + glob(
                os.path.join(temp_dir, "**", "*.csv")
            )
        else:
            # Copy CSV file to temporary directory verbatim
            temp_csv_name = os.path.join(temp_dir, os.path.basename(import_job.data_file.name))
            with open(temp_csv_name, "wb") as temp_csv:
                temp_csv.write(import_job.data_file.open("rb").read())

            csv_names = [temp_csv_name]

        for csv_name in csv_names:
            # chdir() to current CSV file directory; needed for finding
            # related files if importing file columns from zipped CSVs
            os.chdir(os.path.dirname(csv_name))

            # Guess encoding first
            with open(csv_name, "rb") as csv:
                encoding = chardet.detect(csv.read())["encoding"]

            with open(csv_name, newline="", encoding=encoding) as csv:
                try:
                    # Use discovered column configurations for one-off Pandas loading
                    data = pandas.read_csv(
                        csv,
                        sep=template.parsed_separator,
                        names=data_types.keys(),
                        header=0 if template.has_header_row else None,
                        index_col=template.has_index_col,
                        dtype=data_types,
                        usecols=lambda k: not k.startswith("_"),
                        keep_default_na=False,
                        converters=converters,
                        quotechar=template.parsed_quotechar,
                        encoding=encoding,
                        true_values=TRUE_VALUES,
                        false_values=FALSE_VALUES,
                    )
                except ParserError as e:
                    msg = _("There was an error while parsing the CSV file:\n{}").format(e)
                    if recorder:
                        recorder.add_message(messages.ERROR, msg)
                    else:
                        logging.error(msg)
                    continue

                # Exclude all empty rows
                data = data.where(data.notnull(), None)

                all_ok = True
                inactive_refs = []
                created_count = 0

                data_as_dict = data.transpose().to_dict().values()

                iterator = recorder.iterate(data_as_dict) if recorder else tqdm(data_as_dict)
                for row in iterator:
                    # Generate virtual and post-processed field data
                    for column_name, field_type in field_types.items():
                        # Generate field using a Django template string, and the row as context
                        tmpl_str = field_type.get_template()
                        if not tmpl_str:
                            continue
                        tmpl = Template(tmpl_str)
                        ctx = Context(row)
                        ctx.update(
                            process_custom_context_processors(
                                settings.NON_REQUEST_CONTEXT_PROCESSORS
                            )
                        )
                        data = tmpl.render(ctx).strip()

                        if column_name in virtual_fields:
                            # Post-process virtual fields using converter
                            data = field_type.get_converter()(data)

                        # Store
                        row[column_name] = data

                    # Build dict with all fields that should be directly updated
                    update_dict = {}
                    for key, value in row.items():
                        if key in field_types:
                            field_type = field_types[key]
                            if isinstance(field_type, DirectMappingFieldType):
                                update_dict[field_type.get_db_field()] = value

                    # Set group type for imported groups if defined in template globally
                    if template.group_type and model == Group:
                        update_dict["group_type"] = template.group_type

                    # Determine available fields for finding existing instances
                    get_dict = {}
                    match_field_priority = 0
                    for (
                        column_name,
                        field_type,
                    ) in sorted(
                        filter(lambda f: isinstance(f[1], MatchFieldType), field_types.items()),
                        key=lambda f: f[1].priority,
                    ):
                        if match_field_priority and match_field_priority < field_type.priority:
                            # We found a match field, but with less important priority than
                            # those before, so we write data from the field
                            update_dict[field_type.get_db_field()] = row[column_name]
                        elif column_name in row:
                            get_dict[field_type.get_db_field()] = row[column_name]
                            match_field_priority = field_type.priority

                    if not match_field_priority:
                        raise ValueError(_("Missing unique reference or other matching fields."))

                    # Set alternatives for some fields
                    for column_name, field_type in field_types.items():
                        for alternative_db_field in field_type.get_alternative_db_fields():
                            origin_db_field = field_type.get_db_field()
                            if (
                                hasattr(model, alternative_db_field)
                                and alternative_db_field not in update_dict
                            ):
                                if origin_db_field in update_dict:
                                    update_dict[alternative_db_field] = update_dict[origin_db_field]
                                elif origin_db_field in get_dict:
                                    update_dict[alternative_db_field] = get_dict[origin_db_field]

                    # Set school term globally if model is school term related
                    if hasattr(model, "school_term") and school_term:
                        get_dict["school_term"] = school_term

                    created = False
                    try:
                        get_dict["defaults"] = update_dict
                        instance, created = model.objects.update_or_create(**get_dict)
                        if created:
                            created_count += 1

                        # Process field types with custom logic
                        for column_name, field_type in filter(
                            lambda f: isinstance(f[1], ProcessFieldType), field_types.items()
                        ):
                            try:
                                field_type.process(instance, row[column_name])
                            except (RuntimeError, IndexError) as e:
                                if recorder:
                                    recorder.add_message(messages.ERROR, str(e))
                                else:
                                    logging.error(str(e))

                        # Add current instance to group if import defines a target group for persons
                        if template.group and isinstance(instance, Person):
                            instance.member_of.add(template.group)
                    except (
                        ValueError,
                        ValidationError,
                        model.MultipleObjectsReturned,
                        model.DoesNotExist,
                    ) as e:
                        msg = _("Failed to import {verbose_name} {row}:\n{e}").format(
                            verbose_name=model._meta.verbose_name, row=row, e=e
                        )
                        if recorder:
                            recorder.add_message(
                                messages.ERROR,
                                msg,
                            )
                        else:
                            logging.error(msg)
                            all_ok = False

                if created_count:
                    msg = _("{created_count} {verbose_name} were newly created.").format(
                        created_count=created_count, verbose_name=model._meta.verbose_name_plural
                    )
                    if recorder:
                        recorder.add_message(messages.SUCCESS, msg)
                    else:
                        logging.info(msg)

                if all_ok:
                    msg = _("All {verbose_name} were imported successfully.").format(
                        verbose_name=model._meta.verbose_name_plural
                    )
                    if recorder:
                        recorder.add_message(messages.SUCCESS, msg)
                    else:
                        logging.info(msg)
                else:
                    msg = _("Some {verbose_name} failed to be imported.").format(
                        verbose_name=model._meta.verbose_name_plural
                    )
                    if recorder:
                        recorder.add_message(messages.WARNING, msg)
                    else:
                        logging.warning(msg)
