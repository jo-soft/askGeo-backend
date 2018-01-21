from marshmallow import Schema, fields

from models.model_base import ModelBase


class LocationSchema(Schema):
    longitude = fields.Number
    latitude = fields.Number


class LocationBasedModel(ModelBase):
    locationField = "loc"

    @classmethod
    def get_scheme(cls, class_to_create=None):
        class_to_create = class_to_create or cls
        base_schema = super(LocationBasedModel, cls).get_scheme(class_to_create)

        class LocationBasedSchema(base_schema):
            def __new__(inner_cls, *args, **kwargs):
                super().__new__(*args, **kwargs)
                setattr(inner_cls,
                        cls.locationField,
                        fields.Nested(LocationSchema)
                        )

        return LocationBasedSchema
