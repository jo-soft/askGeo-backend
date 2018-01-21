from bson import ObjectId
from marshmallow import fields

from database.utils import id_obj_to_int


class IdField(fields.Integer):
    def _deserialize(self, value, attr, data):
        if isinstance(value, ObjectId):
            value = id_obj_to_int(value)
        return super()._deserialize(value, attr, data)
