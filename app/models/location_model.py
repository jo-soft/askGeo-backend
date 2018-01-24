from marshmallow import Schema, fields

from database.location_manager import LocationManager
from models.model_base import ModelBase


class LocationSchema(Schema):
    # todo: replace number by longidute and latidue field with validation
    longitude = fields.Number()
    latitude = fields.Number()


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
