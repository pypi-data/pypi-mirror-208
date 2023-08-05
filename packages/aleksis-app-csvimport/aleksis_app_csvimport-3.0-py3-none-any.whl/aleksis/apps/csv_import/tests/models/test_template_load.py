import os

from django.contrib.contenttypes.models import ContentType

import pytest

from aleksis.apps.csv_import.default_templates import update_or_create_templates_from_yaml
from aleksis.apps.csv_import.models import ImportTemplate, ImportTemplateField
from aleksis.core.models import Person

pytestmark = pytest.mark.django_db


TEST_FILE_1 = """
test_template:
  model: core.Person
  verbose_name: 'Pedasos: Teachers'
  extra_args:
    has_header_row: true
    separator: "\t"
  fields:
    - short_name
    - last_name
    - first_name
    - date_of_birth
    - sex
    - field_type: departments
      arg_1: foo
      arg_2: 2
    - ignore

"""

TEST_FILE_2 = """
test_template:
  model: core.Person
  verbose_name: 'Pedasos: Teacher'
  extra_args:
    has_header_row: false
    separator: "\t"
  fields:
    - last_name
    - short_name
    - first_name
    - field_type: sex
      arg_1: baz
      arg_2: 3
    - departments
    - ignore
"""


def test_load_sample_template(tmp_path):
    test_filename = os.path.join(tmp_path, "templates.yaml")
    with open(test_filename, "w") as f:
        f.write(TEST_FILE_1)

    assert ImportTemplate.objects.all().count() == 0

    update_or_create_templates_from_yaml(test_filename)

    assert ImportTemplate.objects.all().count() == 1
    assert ImportTemplateField.objects.all().count() == 7
    template = ImportTemplate.objects.all()[0]

    assert template.content_type == ContentType.objects.get_for_model(Person)
    assert template.name == "test_template"
    assert template.verbose_name == "Pedasos: Teachers"
    assert template.has_header_row
    assert template.separator == "\t"

    # Normal field
    field_1 = ImportTemplateField.objects.get(template=template, field_type="short_name")
    assert field_1.index == 0
    assert field_1.args == {}

    # Field with args
    field_2 = ImportTemplateField.objects.get(template=template, field_type="departments")
    assert field_2.index == 5
    assert field_2.args == {"arg_1": "foo", "arg_2": 2}

    # NEW IMPORT

    test2_filename = os.path.join(tmp_path, "templates2.yaml")
    with open(test2_filename, "w") as f:
        f.write(TEST_FILE_2)

    update_or_create_templates_from_yaml(test2_filename)

    assert ImportTemplate.objects.all().count() == 1
    assert ImportTemplateField.objects.all().count() == 6

    template = ImportTemplate.objects.all()[0]
    assert template.name == "test_template"
    assert template.verbose_name == "Pedasos: Teacher"

    # Normal field
    field_1 = ImportTemplateField.objects.get(template=template, field_type="last_name")
    assert field_1.index == 0
    assert field_1.args == {}

    # Normal field removed
    with pytest.raises(ImportTemplateField.DoesNotExist):
        ImportTemplateField.objects.get(template=template, field_type="date_of_birth")

    # Field with args (newly added)
    field_2 = ImportTemplateField.objects.get(template=template, field_type="sex")
    assert field_2.index == 3
    assert field_2.args == {"arg_1": "baz", "arg_2": 3}

    # Field with args (removed)
    field_3 = ImportTemplateField.objects.get(template=template, field_type="departments")
    assert field_3.index == 4
    assert field_3.args == {}
