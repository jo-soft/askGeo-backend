from bson import ObjectId
from marshmallow import fields

from database.utils import hex_str_to_id_obj, id_obj_to_hex_str
from models.model_reference_fields import CachedObj


class TupleField(fields.Field):
    def __init__(self, tuple_entries, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tuple_entries = tuple_entries

    def _serialize(self, attr, obj, accessor=None):
        return tuple(
            (field._serialize(val, obj, accessor) for field, val in zip(self.tuple_entries, attr))
        )

    def _deserialize(self, value, attr=None, data=None):
        return (
            (field._deserialize(val, attr, data) for field, val in zip(self.tuple_entries, value))
        )


class IdField(fields.String):
    def _deserialize(self, value, attr, data):
        if isinstance(value, ObjectId):
            value = id_obj_to_hex_str(value)
        return super()._deserialize(value, attr, data)


class ReverseIdField(fields.String):
    def _deserialize(self, value, attr, data):
        if not isinstance(value, ObjectId):
            value = hex_str_to_id_obj(value)
        return value


class UnCacheField(fields.Field):
    def _serialize(self, value, attr, obj):
        if isinstance(value, CachedObj):
            return value.value
        else:
            return value
