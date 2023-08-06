class BaseField:
    def json_schema_render(self):
        raise NotImplementedError

    def __get__(self, __instance__, __owner__):
        return self.value

    def __set__(self, __instance__, value):
        self.value = value

    value = None
    contribute_to_class = True


class StringField(BaseField):
    def json_schema_render(self):
        return {"type": "string"}

    def __set__(self, __instance__, value):
        if not isinstance(value, str):
            raise ValueError("Value must be a string")
        self.value = value


class BooleanField(BaseField):
    def json_schema_render(self):
        return {"type": "boolean"}


class IntegerField(BaseField):
    def json_schema_render(self):
        return {"type": "integer"}


class DateTimeField(BaseField):
    def json_schema_render(self):
        return {
            "type": "string",
            "pattern": "^([\\+-]?\\d{4}(?!\\d{2}\\b))((-?)((0[1-9]|1[0-2])(\\3([12]\\d|0[1-9]|3[01]))?|W([0-4]\\d|5[0-2])(-?[1-7])?|(00[1-9]|0[1-9]\\d|[12]\\d{2}|3([0-5]\\d|6[1-6])))([T\\s]((([01]\\d|2[0-3])((:?)[0-5]\\d)?|24\\:?00)([\\.,]\\d+(?!:))?)?(\\17[0-5]\\d([\\.,]\\d+)?)?([zZ]|([\\+-])([01]\\d|2[0-3]):?([0-5]\\d)?)?)?)?$",
        }


class UrlField(BaseField):
    def json_schema_render(self):
        return {
            "type": "string",
            "pattern": "^([a-zA-Z0-9]+(-[a-zA-Z0-9]+)*\\.)+[a-zA-Z]{2,}",
        }


class ArrayField(BaseField):
    def __init__(self, type: BaseField):
        self.type = type

    def json_schema_render(self):
        return {"type": "array", "items": self.type.json_schema_render()}


class EnumField(BaseField):
    def __init__(self, enum):
        self.enum = enum

    def json_schema_render(self):
        return {
            "type": "string",
            "enum": [e.value for e in self.enum],
        }
