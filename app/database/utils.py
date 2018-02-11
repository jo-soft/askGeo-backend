from bson import ObjectId

BYTE_ORDER = "big"
# 12 bytes length is required by bson
# see: http://api.mongodb.com/python/current/api/bson/objectid.html#bson.objectid.ObjectId
BYTE_LENGTH = 12


def id_obj_to_int(id_obj):
    return int.from_bytes(id_obj.binary, BYTE_ORDER)


def int_to_id_obj(_id):
    bytes_array = int.to_bytes(_id, BYTE_LENGTH, BYTE_ORDER)
    return ObjectId(bytes_array)


def id_obj_to_hex_str(id_obj):
    return id_obj.binary.hex()


def hex_str_to_id_obj(hex_str):
    id_as_int = int(hex_str, 16)
    return int_to_id_obj(id_as_int)
