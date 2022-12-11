from marshmallow import fields, INCLUDE, validate
from portcast_app import mm
from portcast_app.utils import InvalidField

def get_request_schema(name: str):
    schema_hash = {
        'SEARCH': Search,
    }
    if name in schema_hash:
        return schema_hash[name]()
    raise InvalidField(f'{name} schema is invalid')


class Search(mm.Schema):
    keywords = fields.List(fields.String(required=True))
    operator = fields.String(validate=validate.OneOf(['OR', 'AND']))