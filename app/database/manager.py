from copy import copy

from database.exceptions import LoadError, InsertFailedError, UpdateFailedError, NotFoundError
from database.utils import hex_str_to_id_obj, id_obj_to_hex_str
from models.db import get_db


class Manager(object):

    @property
    def collection(self):
        return get_db()[self.collection_name]

    def __init__(self, content_class, table_name=None):
        self.collection_name = table_name or content_class.__name__
        self.content_class = content_class

    def _load(self, raw_data, many=False):
        schema = self.content_class.get_scheme_cls()(many=many)
        loaded = schema.load(raw_data)
        if loaded.errors:
            raise LoadError(loaded.errors)
        return loaded.data

    def get_one_by_id(self, _id, filter_data={}, **kwargs):
        filter_data = copy(filter_data)
        filter_data['_id'] = hex_str_to_id_obj(_id)
        return self.get_one(filter_data, **kwargs)

    def get_one(self, filter_data, **kwargs):
        raw_data = self.collection.find_one(filter_data, **kwargs)
        if not raw_data:
            raise NotFoundError(self.collection, filter_data)
        return self._load(raw_data)

    def get(self, filter_data, **kwargs):
        raw_data = self.collection.find(filter_data, show_record_id=True, **kwargs)
        return self._load(raw_data, many=True)

    def exists(self, filter_data, **kwargs):
        raw_data = self.collection.find(filter_data, **kwargs).limit(1)
        return raw_data.count() == 1

    def save(self, item):
        if item.is_new():
            return self._save(item)
        else:
            return self._update(item)

    def _default_exclude_in_save_fn(self, field):
        meta = getattr(field, 'meta', {})
        meta_data = getattr(field, 'metaData', {})
        # exclude all fields which are marked as external or not internal
        is_external = meta.get('external', False) or meta_data.get('external', False)
        is_internal = meta.get('internal', True) or meta_data.get('internal', True)
        return not is_internal or is_external

    def _save(self, item):
        data = item.serialize(exclude=['_id'], field_filter_fn=self._default_exclude_in_save_fn)
        insert_result = self.collection.insert_one(data)

        if not insert_result.inserted_id:
            raise InsertFailedError(self.collection, item)
        item._id = id_obj_to_hex_str(insert_result.inserted_id)
        return item

    def _update(self, item):
        data = item.serialize(field_filter_fn=self._default_exclude_in_save_fn)
        update_data_with_operator = {"$set": data}
        filter_data = {'_id': item._id}
        update_result = self.collection.update_one(filter_data, update=update_data_with_operator)

        if not update_result.matched_count:
            raise NotFoundError(self.collection, item._id)
        if not update_result.modified_count:
            raise UpdateFailedError(self.collection, item)
        return item

    def delete(self, _id):
        return self.delete_by_id(
            hex_str_to_id_obj(_id)
        )

    def delete_by_id(self, item_id):
        delete_result = self.collection.delete_one({'_id': item_id})
        if not delete_result.deleted_count:
            raise NotFoundError(self.collection, item_id)
