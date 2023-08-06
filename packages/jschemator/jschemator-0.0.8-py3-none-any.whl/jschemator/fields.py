class BaseField:
    def __init__(self, description=None, **__kwargs__):
        self.description = description

    def json_schema_render(self):
        if self.description:
            return {"description": self.description}
        return {}

    def __get__(self, __instance__, __owner__):
        return self.value

    def __set__(self, __instance__, value):
        self.value = value

    value = None
    contribute_to_class = True


class StringField(BaseField):
    def json_schema_render(self):
        schema = super(StringField, self).json_schema_render()
        schema.update({"type": "string"})
        return schema

    def __set__(self, __instance__, value):
        if not isinstance(value, str):
            raise ValueError("Value must be a string")
        self.value = value


class BooleanField(BaseField):
    def json_schema_render(self):
        schema = super(BooleanField, self).json_schema_render()
        schema.update({"type": "boolean"})
        return schema


class IntegerField(BaseField):
    def json_schema_render(self):
        schema = super(IntegerField, self).json_schema_render()
        schema.update({"type": "integer"})
        return schema


class NumberField(BaseField):
    def json_schema_render(self):
        schema = super(NumberField, self).json_schema_render()
        schema.update({"type": "number"})
        return schema


class DateTimeField(BaseField):
    def json_schema_render(self):
        schema = super(DateTimeField, self).json_schema_render()
        schema.update(
            {
                "type": "string",
                "pattern": "^([\\+-]?\\d{4}(?!\\d{2}\\b))((-?)((0[1-9]|1[0-2])(\\3([12]\\d|0[1-9]|3[01]))?|W([0-4]\\d|5[0-2])(-?[1-7])?|(00[1-9]|0[1-9]\\d|[12]\\d{2}|3([0-5]\\d|6[1-6])))([T\\s]((([01]\\d|2[0-3])((:?)[0-5]\\d)?|24\\:?00)([\\.,]\\d+(?!:))?)?(\\17[0-5]\\d([\\.,]\\d+)?)?([zZ]|([\\+-])([01]\\d|2[0-3]):?([0-5]\\d)?)?)?)?$",
            }
        )
        return schema


class UrlField(BaseField):
    def json_schema_render(self):
        schema = super(UrlField, self).json_schema_render()
        schema.update(
            {
                "type": "string",
                "pattern": "^([a-zA-Z0-9]+(-[a-zA-Z0-9]+)*\\.)+[a-zA-Z]{2,}",
            }
        )
        return schema


class ArrayField(BaseField):
    def __init__(self, type, **kwargs):
        self.type = type
        super(ArrayField, self).__init__(**kwargs)

    def json_schema_render(self):
        schema = super(ArrayField, self).json_schema_render()
        schema.update(
            {"type": "array", "items": self.type.json_schema_render()}
        )
        return schema


class EnumField(BaseField):
    def __init__(self, enum, **kwargs):
        self.enum = enum
        super(EnumField, self).__init__(**kwargs)

    def json_schema_render(self):
        schema = super(EnumField, self).json_schema_render()
        schema.update(
            {
                "type": "string",
                "enum": [e.value for e in self.enum],
            }
        )
        return schema


class Compose:
    def __init__(self, *types):
        self.types = types

    def json_schema_render(self):
        return [type.json_schema_render() for type in self.types]


class ObjectField(BaseField):
    def __init__(self, sub_schema, **kwargs):
        self.sub_schema = sub_schema
        super(ObjectField, self).__init__(**kwargs)

    def json_schema_render(self):
        schema = super(ObjectField, self).json_schema_render()
        schema.update(self.sub_schema.json_schema())
        return schema
