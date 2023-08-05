from django.contrib.contenttypes.models import ContentType

import pytest

from aleksis.apps.csv_import.field_types import FirstNameFieldType, LastNameFieldType
from aleksis.apps.csv_import.models import ImportTemplate
from aleksis.core.models import Person

pytestmark = pytest.mark.django_db


def test_converters_none():
    template = ImportTemplate.objects.create(
        content_type=ContentType.objects.get_for_model(Person),
        name="foo",
        verbose_name="Bar",
    )

    field_0 = template.fields.create(field_type=FirstNameFieldType.name, index=0)
    field_1 = template.fields.create(field_type=LastNameFieldType.name, index=1)

    field_0_cls = field_0.field_type_class(None, "", **field_0.args)
    field_1_cls = field_1.field_type_class(None, "", **field_1.args)

    field_0_chain = field_0_cls.get_converter()
    field_1_chain = field_1_cls.get_converter()

    convert_in = " foo "
    convert_out_0 = field_0_chain(convert_in)
    convert_out_1 = field_1_chain(convert_in)

    assert convert_out_0 == convert_in
    assert convert_out_1 == convert_in


def test_converters_one():
    template = ImportTemplate.objects.create(
        content_type=ContentType.objects.get_for_model(Person),
        name="foo",
        verbose_name="Bar",
    )

    field_0 = template.fields.create(
        field_type=FirstNameFieldType.name, index=0, args={"converter_pre": "lstrip"}
    )
    field_1 = template.fields.create(
        field_type=LastNameFieldType.name, index=1, args={"converter_post": "rstrip"}
    )

    field_0_cls = field_0.field_type_class(None, "", **field_0.args)
    field_1_cls = field_1.field_type_class(None, "", **field_1.args)

    field_0_chain = field_0_cls.get_converter()
    field_1_chain = field_1_cls.get_converter()

    convert_in = " foo "
    convert_out_0 = field_0_chain(convert_in)
    convert_out_1 = field_1_chain(convert_in)

    assert convert_out_0 == convert_in.lstrip()
    assert convert_out_1 == convert_in.rstrip()


def test_converters_multiple():
    template = ImportTemplate.objects.create(
        content_type=ContentType.objects.get_for_model(Person),
        name="foo",
        verbose_name="Bar",
    )

    field_0 = template.fields.create(
        field_type=FirstNameFieldType.name, index=0, args={"converter_pre": ["lstrip", "rstrip"]}
    )
    field_1 = template.fields.create(
        field_type=LastNameFieldType.name,
        index=1,
        args={"converter_pre": "rstrip", "converter_post": "lstrip"},
    )

    field_0_cls = field_0.field_type_class(None, "", **field_0.args)
    field_1_cls = field_1.field_type_class(None, "", **field_1.args)

    field_0_chain = field_0_cls.get_converter()
    field_1_chain = field_1_cls.get_converter()

    convert_in = " foo "
    convert_out_0 = field_0_chain(convert_in)
    convert_out_1 = field_1_chain(convert_in)

    assert convert_out_0 == convert_in.strip()
    assert convert_out_1 == convert_in.strip()
