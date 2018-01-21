from database.exceptions import LoadError, InsertFailedError, UpdateFailedError, NotFoundError
from database.utils import int_to_id_obj, id_obj_to_int
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

    def get_one_by_id(self, _id, filter_data={}, **kwargs):
        filter_data['_id'] = int_to_id_obj(_id)
        return self.get_one(filter_data, **kwargs)

    def get_one(self, filter_data, **kwargs):
        raw_data = self.db_table.find_one(filter_data, **kwargs)
        if not raw_data:
            raise NotFoundError(self.db_table, filter_data)
        return self._load(raw_data)

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
        item._id = id_obj_to_int(insert_result.inserted_id)
        return item

    def _update(self, item):
        data = item.serialize()
        update_data_with_operator = {"$set": data}
        filter_data = {'_id': item._id}
        update_result = self.db_table.update_one(filter_data, update=update_data_with_operator)

        if not update_result.matched_count:
            raise NotFoundError(self.db_table, item._id)
        if not update_result.modified_count:
            raise UpdateFailedError(self.db_table, item)
        return item

    def delete(self, _id):
        return self.delete_by_id(
            int_to_id_obj(_id)
        )

    def delete_by_id(self, item_id):
        delete_result = self.db_table.delete_one({'_id': item_id})
        if not delete_result.deleted_count:
            raise NotFoundError(self.db_table, item_id)
