from flask_restful import Resource
from marshmallow import fields, post_load
from marshmallow.utils import _Missing

from database.manager import Manager
from database.schema import BaseSchema
from database.schema_fields import IdField


class ModelBase(Resource):
    @classmethod
    def get_scheme_cls(cls, class_to_create=None):
        class_to_create = class_to_create or cls

        class ModelBaseSchema(BaseSchema):
            # allow none for new items
            _id = IdField(allow_none=True)
            deleted = fields.Boolean(default=False)

            @post_load
            def make_instance(self, data):
                return class_to_create(**data)

        return ModelBaseSchema

    @classmethod
    def manager(cls):
        return Manager(cls)

    def __init__(self, **kwargs):
        super().__init__()
        self._deleted_ = False
        # iterate over all fields from schema and read values from kwargs to self.
        for field_name, field in self.get_scheme_cls()().declared_fields.items():
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
        self._load_fields()

    def _get_fields(self):
        reversed_classes = reversed(self.__class__.__mro__)
        fields_per_cls = [getattr(cls, 'fields', {}) for cls in reversed_classes]

        result = {}
        for _fields in fields_per_cls:
            result.update(_fields)
        return result

    def _load_fields(self):
        _fields = self._get_fields()
        for field_name, field in _fields.items():
            field.load(field_name=field_name, obj=self)

    def _serialize_fields(self, exclude=[]):
        _fields = self._get_fields()
        for field_name, field in _fields.items():
            if field_name in exclude:
                continue
            field.serialize(field_name=field_name, obj=self)

    def deleted(self, val=None):
        if val is not None:
            self._deleted_ = bool(val)
        return self._deleted_

    def is_new(self):
        return self._id is None

    def serialize(self, exclude=(), exclude_fields=(), field_filter_fn=None):
        self._serialize_fields(exclude=exclude_fields)

        schema = self.get_scheme_cls()(exclude=exclude, field_filter_fn=field_filter_fn)
        dump_result = schema.dump(self)
        return dump_result.data
