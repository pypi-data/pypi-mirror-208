import json


from jschemator.fields import BaseField


class Schema:
    def __init__(self, *__args__, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get_fields(self):
        fields = {}
        for attribute_name, attribute_description in type(
            self
        ).__dict__.items():
            if not attribute_name.startswith("__") and isinstance(
                attribute_description, BaseField
            ):
                fields[attribute_name] = getattr(self, attribute_name)
        return fields

    def to_dict(self):
        return self.get_fields()

    def json_schema(self):
        properties = {
            schema_field: type(self)
            .__dict__[schema_field]
            .json_schema_render()
            for schema_field in self.get_fields()
        }
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": properties,
        }


__all__ = ["Schema"]
