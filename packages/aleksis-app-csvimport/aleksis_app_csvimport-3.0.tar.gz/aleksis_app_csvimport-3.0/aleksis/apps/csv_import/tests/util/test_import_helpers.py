from aleksis.apps.csv_import.util.import_helpers import with_prefix
from aleksis.core.models import Group, GroupType, Person


def test_with_prefix():
    assert with_prefix("Foo", "Bar") == "Foo Bar"
    assert with_prefix("", "Bar") == "Bar"
    assert with_prefix(None, "Bar") == "Bar"
    assert with_prefix(None, "") == ""
    assert with_prefix("", "") == ""
