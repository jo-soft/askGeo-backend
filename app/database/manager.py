from database.exceptions import LoadError, InsertFailedError, UpdateFailedError
from database.utils import hex_to_int
from models.db import get_db


class Manager(object):
    @property
    def db_table(self):
        return get_db()[self.table_name]

    def __init__(self, content_class, table_name=None):
        self.table_name = table_name or content_class.__name__
        self.content_class = content_class

    def _load(self, raw_data, many=False):
        schema = self.content_class.get_scheme()(many=many)
        serialized_data = schema.load(raw_data)
        if serialized_data.errors:
            raise LoadError(serialized_data.errors)
        return serialized_data.data

    def get_one(self, filter_data, **kwargs):
        raw_data = self.db_table.find_one(filter_data, **kwargs)
        if raw_data:
            return self._load(raw_data)
        else:
            return None

    def get(self, filter_data, **kwargs):
        raw_data = self.db_table.find(filter_data, show_record_id=True, **kwargs)
        return self._load(raw_data, many=True)

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
