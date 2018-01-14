from flask_restful import Resource
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
        raw_data = item.serialize()
        upsert_result = self.db_table.update_one({'_id': item._id}, update=raw_data, upsert=True)
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
    def manager(cls):
        return Manager(cls)

    def __init__(self, _id=None, deleted=False):
        super().__init__()
        self._id = _id
        self._deleted_ = deleted

    def deleted(self, val=None):
        if val is not None:
            self._deleted_ = val
        return self._deleted_

    def serialize(self):
        return {
            '_id': self._id,
            'deleted': self.deleted()
        }