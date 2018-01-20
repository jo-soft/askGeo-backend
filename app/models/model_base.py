from flask_restful import Resource
from marshmallow import Schema, fields, post_load
from marshmallow.utils import _Missing

from models.db import get_db


class Manager(object):

    @property
    def db_table(self):
        return get_db()[self.table_name]

    def __init__(self, content_class, table_name=None):
        self.table_name = table_name or content_class.__name__
        self.content_class = content_class

    def get_one(self, filter_data, **kwargs):
        raw_data = self.db_table.find_one(filter_data, **kwargs)
        if raw_data:
            return self.content_class(raw_data)
        else:
            return None

    def get(self, filter_data, **kwargs):
        raw_data = self.db_table.find(filter_data, **kwargs)
        return map(lambda data: self.content_class(data), raw_data)

    def save(self, item):
        update_data_with_operator = {"$set": item.serialize()}
        upsert_result = self.db_table.update_one({'_id': item._id}, update=update_data_with_operator, upsert=True)
        if upsert_result.upserted_id:
            hex_id = upsert_result.upserted_id.binary.hex()
            item._id = hex_id
        else:
            pass
            # maybe throw an error?
        return item

    def delete(self, item):
        return self.delete_by_id(item._id)

    def delete_by_id(self, item_hex_id):
        return self.db_table.delete_one({'_id': item_hex_id})


class ModelBase(Resource):
    @classmethod
    def get_scheme(cls, class_to_create):
        class BaseSchema(Schema):
            # allow none for new items
            _id = fields.Integer(allow_none=True)
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

        # iterate
        for field_name, field in self.__class__.get_scheme(self.__class__)._declared_fields.items():
            try:
                getattr(self, field_name)
            except AttributeError:
                val = kwargs.get(field_name)
                if val is None:
                    if field.allow_none:
                        if not isinstance(field.default, _Missing):
                            val = field.default
                    else:
                        raise AttributeError(field_name)
                setattr(self, field_name, val)

    def deleted(self, val=None):
        if val is not None:
            self._deleted_ = val
        return self._deleted_

    def serialize(self):
        schema = self.__class__.get_scheme(self.__class__)()

        dump_result = schema.dump(self)
        return dump_result.data
