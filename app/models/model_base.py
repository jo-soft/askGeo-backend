from bson import ObjectId
from flask_restful import Resource
from marshmallow import Schema, fields, post_load
from marshmallow.utils import _Missing

from models.db import get_db


def hex_to_int(num_as_hex_str):
    return int(num_as_hex_str, 16)


def id_Obj_to_int(id_obj):
    return hex_to_int(id_obj.binary.hex())


class TableModificationFaildError(ValueError):
    pass


class InsertFailedError(TableModificationFaildError):
    def __init__(self, table, item, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.table = table
        self.item = item


class UpdateFailedError(TableModificationFaildError):
    def __init__(self, table, item, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.table = table
        self.item = item


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
        raw_data = self.db_table.find(filter_data, show_record_id=True, **kwargs)
        return map(lambda data: self.content_class(**data), raw_data)

    def save(self, item):
        if item.is_new():
            return self._save(item)
        else:
            return self._update(item)

    def _save(self, item):
        data = item.serialize(exclude=['_id'])
        insert_result = self.db_table.insert_one(data)

        if not insert_result.inserted_id:
            raise InsertFailedError(self.db_table, item)

        hex_id = insert_result.inserted_id.binary.hex()
        item._id = hex_to_int(hex_id)

        return item

    def _update(self, item):
        data = item.serialize()
        update_data_with_operator = {"$set": data}
        update_result = self.db_table.update_one({'_id': item._id}, update=update_data_with_operator, upsert=True)

        if not update_result.affected_rows:
            raise UpdateFailedError(self.db_table, item)

        hex_id = update_result.upserted_id.binary.hex()
        item._id = hex_to_int(hex_id)
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

        self._set_id(kwargs.get('_id'))

        # iterate over all fields from schema and read values from kwargs to self.
        for field_name, field in self.__class__.get_scheme(self.__class__)._declared_fields.items():
            try:
                getattr(self, field_name)
            except AttributeError:
                val = kwargs.get(field_name)
                if val is None:
                    if field.allow_none:
                        continue
                    elif not isinstance(field.default, _Missing):
                        val = field.default

                if val is None:
                    raise AttributeError(field_name)
                setattr(self, field_name, val)

    def _set_id(self, _id):
        if isinstance(_id, ObjectId):
            self._id = id_Obj_to_int(_id)
        else:
            self._id = _id

    def deleted(self, val=None):
        if val is not None:
            self._deleted_ = val
        return self._deleted_

    def is_new(self):
        return self._id is None

    def serialize(self, exclude=[]):
        schema = self.__class__.get_scheme(self.__class__)(exclude=exclude)
        dump_result = schema.dump(self)
        return dump_result.data
