from flask_restful import Resource
from marshmallow import Schema, fields, post_load
from marshmallow.utils import _Missing

from database.fields import IdField
from database.manager import Manager


class ModelBase(Resource):
    @classmethod
    def get_scheme(cls, class_to_create=None):
        class_to_create = class_to_create or cls

        class BaseSchema(Schema):
            # allow none for new items
            _id = IdField(allow_none=True)
            deleted = fields.Boolean(default=False)

            @post_load
            def make_instance(self, data):
                return class_to_create(**data)

        return BaseSchema

    @classmethod
    def manager(cls):
        return Manager(cls)

    def __init__(self, **kwargs):
        super().__init__()

        # iterate over all fields from schema and read values from kwargs to self.
        for field_name, field in self.__class__.get_scheme()._declared_fields.items():
            try:
                getattr(self, field_name)
            except AttributeError:
                val = kwargs.get(field_name)
                if val is None:
                    if field.allow_none:
                        pass
                    elif not isinstance(field.default, _Missing):
                        val = field.default

                if val is None and not field.allow_none:
                    raise AttributeError(field_name)
                setattr(self, field_name, val)

    def deleted(self, val=None):
        if val is not None:
            self._deleted_ = val
        return self._deleted_

    def is_new(self):
        return self._id is None

    def serialize(self, exclude=[]):
        schema = self.__class__.get_scheme()(exclude=exclude)
        dump_result = schema.dump(self)
        return dump_result.data
