import pytest

from jschemator.fields import BaseField


class BareClass:
    field = BaseField()


def test_get_and_set():
    item = BareClass()
    item.field = "foo"
    assert item.field == "foo"


def test_complex_type_unimplemented_schema_render():
    field = BaseField()
    with pytest.raises(NotImplementedError):
        field.json_schema_render()
