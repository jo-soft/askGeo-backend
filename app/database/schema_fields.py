from bson import ObjectId
from marshmallow import fields, ValidationError

from database.utils import hex_str_to_id_obj, id_obj_to_hex_str
from models.misc import CachedObj


class TupleField(fields.Field):
    def __init__(self, tuple_entries, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tuple_entries = tuple_entries

    def _validate_helper_single(self, field, fn, val):
        try:
            getattr(field, fn)(val)
        except ValidationError as ve:
            return ve
        else:
            return None

    def _validate_helper(self, fn, value):
        items = zip(self.tuple_entries, value)
        validation_errors = [
            self._validate_helper_single(field, fn, val) for field, val in items
        ]
        if validation_errors and any(validation_errors):
            raise ValidationError(message={
                idx: err for idx, err in enumerate(validation_errors)
            })

    def _validate(self, value):
        super()._validate(value)
        self._validate_helper('_validate', value)

    def _validate_missing(self, value):
        super()._validate_missing(value)
        super()._validate(value)
        self._validate_helper('_validate_missing', value)

    def _serialize(self, attr, obj, accessor=None):
        return tuple(
            (field._serialize(val, obj, accessor) for field, val in zip(self.tuple_entries, attr))
        )

    def _deserialize(self, value, attr=None, data=None):
        return tuple(
            (field._deserialize(val, attr, data) for field, val in zip(self.tuple_entries, value))
        )


class IdField(fields.String):
    def _deserialize(self, value, attr, data=None):
        if isinstance(value, ObjectId):
            value = id_obj_to_hex_str(value)
        return super()._deserialize(value, attr, data)


class ReverseIdField(fields.String):
    def _deserialize(self, value, attr, data=None):
        if not isinstance(value, ObjectId):
            value = hex_str_to_id_obj(value)
        return value


class UnCacheField(fields.Field):
    def _serialize(self, attr, obj, accessor=None):
        if isinstance(attr, CachedObj):
            return attr.value
        else:
            return attr
