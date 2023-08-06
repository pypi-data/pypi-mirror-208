from jschemator.fields import Compose, StringField, IntegerField


def test_compose_json_schema_render_should_return_a_list():
    composed = Compose(StringField(), IntegerField())
    assert isinstance(composed.json_schema_render(), list)
