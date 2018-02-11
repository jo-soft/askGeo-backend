from marshmallow import Schema, fields, post_load, pre_dump

from database.location_manager import LocationManager
from database.schema_fields import TupleField
from models.geojsonp import locationEntityFactory
from models.model_base import ModelBase


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
    def get_scheme_cls(cls, class_to_create=None):
        class_to_create = class_to_create or cls
        base_schema = super(LocationBasedModel, cls).get_scheme_cls(class_to_create)

        location_schema_cls = type('LocationBasedSchema', (base_schema,), {
            cls.locationField: fields.Nested(LocationSchema)
        })
        return location_schema_cls
