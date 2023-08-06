import pytest, json
from jschemator import Schema
from jschemator.fields import StringField


class Item(Schema):
    name = StringField()


def test_creation():
    e = Item(name="foo")
    assert e.name == "foo"


def test_incorrect_creation():
    with pytest.raises(ValueError):
        Item(name=2)


def test_from_dict():
    e = Item(**{"name": "foo"})
    assert e.name == "foo"


def test_to_dict():
    e = Item(**{"name": "foo"})
    assert e.to_dict() == {"name": "foo"}


def test_json_schema():
    e = Item(**{"name": "foo"})
    assert e.json_schema() == {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {"name": {"type": "string"}},
    }
