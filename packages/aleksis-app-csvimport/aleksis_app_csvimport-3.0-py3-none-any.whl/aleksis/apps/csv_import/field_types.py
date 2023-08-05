import os
import re
from typing import Any, Callable, Optional, Sequence, Tuple, Type, Union
from uuid import uuid4

from django.apps import apps
from django.core.files import File
from django.db.models import Model
from django.utils.translation import gettext as _

from aleksis.apps.csv_import.util.class_range_helpers import (
    get_classes_per_grade,
    get_classes_per_short_name,
    parse_class_range,
)
from aleksis.apps.csv_import.util.converters import converter_registry
from aleksis.apps.csv_import.util.import_helpers import with_prefix
from aleksis.core.models import Group, Person, SchoolTerm
from aleksis.core.util.core_helpers import get_site_preferences


class FieldType:
    name: str = ""
    verbose_name: str = ""
    models: Sequence = []
    data_type: type = str
    db_field: str = ""
    converter: Optional[Union[str, Sequence[str]]] = None
    alternative_db_fields: Optional[str] = None
    template: str = ""
    args: Optional[dict] = None

    @classmethod
    def get_data_type(cls) -> type:
        return cls.data_type

    def get_converter(self) -> Callable[[Any], Any]:
        converters_pre = self.get_args().get("converter_pre", [])
        if isinstance(converters_pre, str):
            converters_pre = [converters_pre]
        converters_post = self.get_args().get("converter_post", [])
        if isinstance(converters_post, str):
            converters_post = [converters_post]
        converters = self.get_args().get("converter") or self.converter
        if converters is None:
            converters = []
        elif isinstance(converters, str):
            converters = [converters]
        converters = converters_pre + converters + converters_post

        funcs = [converter_registry.get_from_name(name) for name in converters]

        def _converter_chain(val: Any) -> Any:
            new_val = val
            for func in funcs:
                new_val = func(new_val)
            return new_val

        return _converter_chain

    def get_args(self) -> dict:
        return self.args or {}

    def get_db_field(self) -> str:
        if self.get_args().get("db_field"):
            return self.get_args()["db_field"]
        return self.db_field

    def get_alternative_db_fields(self) -> list[str]:
        if self.get_args().get("alternative_db_fields"):
            return self.get_args()["alterntive_db_fields"]
        return self.alternative_db_fields or []

    def get_column_name(self) -> str:
        """Get column name for use in Pandas structures."""
        if self.get_args().get("column_name"):
            return self.get_args()["column_name"]
        return self.column_name

    def get_template(self) -> str:
        if self.get_args().get("template"):
            return self.get_args()["template"]
        return self.template or ""

    def __init__(self, school_term: SchoolTerm, base_path: str, **kwargs):
        self.school_term = school_term
        self.base_path = os.path.realpath(base_path)
        self.column_name = f"col_{uuid4()}"
        self.args = kwargs


class FieldTypeRegistry:
    def __init__(self):
        self.field_types = {}

    def register(self, field_type: Type[FieldType]):
        """Add new `FieldType` to registry.

        Can be used as decorator, too.
        """
        if field_type.name in self.field_types:
            raise ValueError(f"The field type {field_type.name} is already registered.")
        self.field_types[field_type.name] = field_type

        return field_type

    def get_from_name(self, name: str) -> FieldType:
        """Get `FieldType` by its name."""
        return self.field_types[name]

    @property
    def choices(self) -> Sequence[Tuple[str, str]]:
        """Return choices in Django format."""
        return [(f.name, f.verbose_name) for f in self.field_types.values()]


field_type_registry = FieldTypeRegistry()


@field_type_registry.register
class MatchFieldType(FieldType):
    """Field type for getting an instance."""

    name: str = "match"
    priority: int = 1

    def get_priority(self):
        return self.get_args().get("priority", "") or self.priority


class DirectMappingFieldType(FieldType):
    """Set value directly in DB."""


class ProcessFieldType(FieldType):
    """Field type with custom logic for importing."""

    def process(self, instance: Model, value):
        pass


@field_type_registry.register
class RegExFieldType(ProcessFieldType):
    """Field type to apply a regex transformation."""

    name: str = "reg_ex"
    data_type = str
    reg_ex: str = ""
    fail_if_no_match: bool = False

    def get_reg_ex(self):
        return self.reg_ex or self.get_args().get("reg_ex", "")

    def get_fail_if_no_match(self):
        return self.fail_if_no_match or self.get_args().get("fail_if_no_match", False)

    def process(self, instance: Model, value):
        match = re.fullmatch(self.get_reg_ex(), value)
        if match:
            for key, item in match.groupdict().items():
                setattr(instance, key, item)
            instance.save()
        elif self.get_fail_if_no_match():
            raise IndexError(
                _("No match on {} for regular expression {} found.").format(
                    value, self.get_reg_ex()
                )
            )


@field_type_registry.register
class UniqueReferenceFieldType(MatchFieldType):
    name = "unique_reference"
    verbose_name = _("Unique reference")
    db_field = "import_ref_csv"
    priority = 10


@field_type_registry.register
class NameFieldType(DirectMappingFieldType):
    name = "name"
    verbose_name = _("Name")
    db_field = "name"
    alternative_db_fields = ["short_name"]


@field_type_registry.register
class FirstNameFieldType(DirectMappingFieldType):
    name = "first_name"
    verbose_name = _("First name")
    db_field = "first_name"


@field_type_registry.register
class LastNameFieldType(DirectMappingFieldType):
    name = "last_name"
    verbose_name = _("Last name")
    db_field = "last_name"


@field_type_registry.register
class AdditionalNameFieldType(DirectMappingFieldType):
    name = "additional_name"
    verbose_name = _("Additional name")
    db_field = "additional_name"


@field_type_registry.register
class ShortNameFieldType(MatchFieldType):
    name = "short_name"
    verbose_name = _("Short name")
    priority = 8
    db_field = "short_name"
    alternative_db_fields = ["name", "first_name", "last_name"]


@field_type_registry.register
class EmailFieldType(MatchFieldType):
    name = "email"
    verbose_name = _("Email")
    db_field = "email"
    priority = 12

    def get_converter(self) -> Optional[Callable]:
        if "email_domain" in self.get_args():

            def add_domain_to_email(value: str) -> str:
                if "@" in value:
                    return value
                else:
                    return f"{value}@{self.get_args()['email_domain']}"

            return add_domain_to_email
        return super().get_converter()


@field_type_registry.register
class DateOfBirthFieldType(DirectMappingFieldType):
    name = "date_of_birth"
    verbose_name = _("Date of birth")
    db_field = "date_of_birth"
    converter = "parse_date"


@field_type_registry.register
class SexFieldType(DirectMappingFieldType):
    name = "sex"
    verbose_name = _("Sex")
    db_field = "sex"
    converter = "parse_sex"


@field_type_registry.register
class StreetFieldType(DirectMappingFieldType):
    name = "street"
    verbose_name = _("Street")
    db_field = "street"


@field_type_registry.register
class HouseNumberFieldType(DirectMappingFieldType):
    name = "housenumber"
    verbose_name = _("Housenumber")
    db_field = "housenumber"


@field_type_registry.register
class StreetAndHouseNumberFieldType(RegExFieldType):
    name = "street_housenumber"
    verbose_name = _("Street and housenumber")
    reg_ex = r"^(?P<street>[\w\s]{3,})\s+(?P<housenumber>\d+\s*[a-zA-Z]*)$"


@field_type_registry.register
class PostalCodeFieldType(DirectMappingFieldType):
    name = "postal_code"
    verbose_name = _("Postal code")
    db_field = "postal_code"


@field_type_registry.register
class PlaceFieldType(DirectMappingFieldType):
    name = "place"
    verbose_name = _("Place")
    db_field = "place"


@field_type_registry.register
class PhoneNumberFieldType(DirectMappingFieldType):
    name = "phone_number"
    verbose_name = _("Phone number")
    db_field = "phone_number"
    converter = "parse_phone_number"


@field_type_registry.register
class MobileNumberFieldType(DirectMappingFieldType):
    name = "mobile_number"
    verbose_name = _("Mobile number")
    db_field = "mobile_number"
    converter = "parse_phone_number"


@field_type_registry.register
class IgnoreFieldType(FieldType):
    name = "ignore"
    verbose_name = _("Ignore data in this field")


@field_type_registry.register
class DepartmentsFieldType(ProcessFieldType):
    name = "departments"
    verbose_name = _("Comma-seperated list of departments")
    converter = "parse_comma_separated_data"

    def process(self, instance: Model, value):
        with_chronos = apps.is_installed("aleksis.apps.chronos")
        if with_chronos:
            Subject = apps.get_model("chronos", "Subject")

        group_type = get_site_preferences()["csv_import__group_type_departments"]
        group_prefix = get_site_preferences()["csv_import__group_prefix_departments"]

        groups = []
        for subject_name in value:
            if with_chronos:
                # Get department subject
                subject, __ = Subject.objects.get_or_create(
                    short_name=subject_name, defaults={"name": subject_name}
                )
                name = subject.name
                short_name = subject.short_name
            else:
                name = subject_name
                short_name = subject_name

            # Get department group
            group, __ = Group.objects.get_or_create(
                group_type=group_type,
                short_name=short_name,
                defaults={"name": with_prefix(group_prefix, name)},
            )
            if with_chronos:
                group.subject = subject
            group.save()

            groups.append(group)

        instance.member_of.add(*groups)


@field_type_registry.register
class GroupSubjectByShortNameFieldType(ProcessFieldType):
    name = "group_subject_short_name"
    verbose_name = _("Short name of the subject")

    def process(self, instance: Model, value):
        with_chronos = apps.is_installed("aleksis.apps.chronos")
        if with_chronos:
            Subject = apps.get_model("chronos", "Subject")
            subject, __ = Subject.objects.get_or_create(short_name=value, defaults={"name": value})
            instance.subject = subject
            instance.save()


@field_type_registry.register
class ClassRangeFieldType(ProcessFieldType):
    name = "class_range"
    verbose_name = _("Class range (e. g. 7a-d)")

    def __init__(self, school_term: SchoolTerm, base_path: str, **kwargs):
        # Prefetch class groups
        self.classes_per_short_name = get_classes_per_short_name(school_term)
        self.classes_per_grade = get_classes_per_grade(self.classes_per_short_name.keys())

        super().__init__(school_term, base_path, **kwargs)

    def process(self, instance: Model, value):
        classes = parse_class_range(
            self.classes_per_short_name,
            self.classes_per_grade,
            value,
        )
        instance.parent_groups.set(classes)


@field_type_registry.register
class PrimaryGroupByShortNameFieldType(ProcessFieldType):
    name = "primary_group_short_name"
    verbose_name = _("Short name of the person's primary group")

    def process(self, instance: Model, value):
        group, __ = Group.objects.get_or_create(
            short_name=value, school_term=self.school_term, defaults={"name": value}
        )
        instance.primary_group = group
        instance.member_of.add(group)
        instance.save()


@field_type_registry.register
class PrimaryGroupOwnerByShortNameFieldType(ProcessFieldType):
    name = "primary_group_owner_short_name"
    verbose_name = _("Short name of an owner of the person's primary group")

    def process(self, instance: Model, value):
        if instance.primary_group:
            owners = Person.objects.filter(short_name=value)
            instance.primary_group.owners.set(owners)


@field_type_registry.register
class GroupOwnerByShortNameFieldType(ProcessFieldType):
    name = "group_owner_short_name"
    verbose_name = _("Short name of a single group owner")

    def process(self, instance: Model, short_name: str):
        group_owner, __ = Person.objects.get_or_create(
            short_name=short_name,
            defaults={"first_name": "?", "last_name": short_name},
        )
        if self.get_args().get("clear", False):
            instance.owners.set([group_owner])
        else:
            instance.owners.add(group_owner)


@field_type_registry.register
class GroupMembershipByShortNameFieldType(ProcessFieldType):
    name = "group_membership_short_name"
    verbose_name = _("Short name of the group the person is a member of")

    def process(self, instance: Model, short_name: str):
        try:
            group = Group.objects.get(short_name=short_name, school_term=self.school_term)
            instance.member_of.add(group)
        except Group.DoesNotExist:
            pass


@field_type_registry.register
class ParentGroupByShortNameFieldType(ProcessFieldType):
    name = "parent_group_short_name"
    verbose_name = _("Short name of the group's parent group")

    def process(self, instance: Model, value):
        group, __ = Group.objects.get_or_create(
            short_name=value, school_term=self.school_term, defaults={"name": value}
        )
        instance.parent_groups.add(group)
        instance.save()


@field_type_registry.register
class MemberOfByNameFieldType(ProcessFieldType):
    name = "member_of_by_name"
    verbose_name = _("Name of a group the person is a member of")

    def process(self, instance: Model, value):
        group, __ = Group.objects.get_or_create(name=value, school_term=self.school_term)
        instance.member_of.add(group)
        instance.save()


@field_type_registry.register
class ChildByUniqueReference(ProcessFieldType):
    name = "child_by_unique_reference"
    verbose_name = _("Child by unique reference (from students import)")

    def process(self, instance: Model, value):
        child = Person.objects.get(import_ref_csv=value)
        instance.children.add(child)


@field_type_registry.register
class FileFieldType(ProcessFieldType):
    """Field type that stores a referenced file on a file field."""

    def process(self, instance: Model, value: str):
        # Test path for unwanted path traversal
        abs_path = os.path.realpath(value)
        if not self.base_path == os.path.commonpath((self.base_path, abs_path)):
            raise ValueError(f"Disallowed path traversal importing file from {value}")

        # Get target FileField and save content
        field_name = self.get_db_field()
        file_field = getattr(instance, field_name)
        file_field.save(os.path.basename(abs_path), File(open(abs_path, "rb")))

        instance.save()


@field_type_registry.register
class AvatarFieldType(FileFieldType):
    name = "avatar"
    db_field = "avatar"


@field_type_registry.register
class PhotoFieldType(FileFieldType):
    name = "photo"
    db_field = "photo"
