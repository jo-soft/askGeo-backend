def hex_to_int(num_as_hex_str):
    return int(num_as_hex_str, 16)


def id_obj_to_int(id_obj):
    return hex_to_int(id_obj.binary.hex())
