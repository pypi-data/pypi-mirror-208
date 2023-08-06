from jschemator.fields import BaseField, StringField, ObjectField
from jschemator import Schema


class BareClass:
    field = BaseField()


class SomeSchemaClass(Schema):
    field = StringField(description="Some description")


class SchemaClass(Schema):
    field = StringField(description="Some description")
    ref = ObjectField(SomeSchemaClass, description="Some description")


def test_get_and_set():
    item = BareClass()
    item.field = "foo"
    assert item.field == "foo"


def test_description():
    assert (
        SchemaClass().json_schema()["properties"]["field"]["description"]
        == "Some description"
    )
    assert (
        SchemaClass().json_schema()["properties"]["ref"]["description"]
        == "Some description"
    )
