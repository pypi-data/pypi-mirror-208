from django.contrib.contenttypes.models import ContentType

import pytest

from aleksis.apps.csv_import.field_types import ShortNameFieldType, UniqueReferenceFieldType
from aleksis.apps.csv_import.models import ImportTemplate
from aleksis.core.models import Person

pytestmark = pytest.mark.django_db


def test_import_template_str():
    template = ImportTemplate.objects.create(
        content_type=ContentType.objects.get_for_model(Person),
        name="foo",
        verbose_name="Bar",
    )
    assert str(template) == "Bar"


def test_import_template_field():
    template = ImportTemplate.objects.create(
        content_type=ContentType.objects.get_for_model(Person),
        name="foo",
        verbose_name="Bar",
    )
    field_0 = template.fields.create(field_type=UniqueReferenceFieldType.name, index=0)
    field_1 = template.fields.create(field_type=ShortNameFieldType.name, index=1)

    assert field_0.field_type_class == UniqueReferenceFieldType
    assert field_1.field_type_class == ShortNameFieldType

    assert template.fields.count() == 2
