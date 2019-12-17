import jinja2
import json

from django.contrib.postgres.fields import JSONField


class SilentUndefined(jinja2.Undefined):
    def _fail_with_undefined_error(self, *args, **kwargs):
        return None


class JsonFieldTransitionHelper(JSONField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def from_db_value(self, value, expression, connection):
        if isinstance(value, str):
            return json.loads(value)

        return value
