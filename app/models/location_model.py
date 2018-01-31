from marshmallow import Schema, fields, post_load, pre_dump

from database.location_manager import LocationManager
from models.geojsonp import locationEntityFactory
from models.model_base import ModelBase


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


class LocationSchema(Schema):
    type = fields.String(required=True)
    coordinates = TupleField(
        (fields.Number(required=True), fields.Number(required=True))
    )

    @pre_dump
    def serialize(self, obj):
        return obj.serialize()

    @post_load
    def make_instance(self, data):
        return locationEntityFactory.create(data['type'], data['coordinates'])


class LocationBasedModel(ModelBase):
    locationField = "loc"

    @classmethod
    def manager(cls):
        return LocationManager(cls)

    @classmethod
    def get_scheme(cls, class_to_create=None):
        class_to_create = class_to_create or cls
        base_schema = super(LocationBasedModel, cls).get_scheme(class_to_create)

        location_schema_cls = type('LocationBasedSchema', (base_schema,), {
            cls.locationField: fields.Nested(LocationSchema)
        })
        return location_schema_cls
