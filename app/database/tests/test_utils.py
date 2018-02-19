import unittest
import random

from bson import ObjectId

from database import utils


class TestIdObjToInt(unittest.TestCase):

    def test_creates_an_int_from_the_id(self):
        id_byes = b'foo-bar-quux'
        id_int = int.from_bytes(id_byes, "big")
        id_obj = ObjectId(id_byes)

        self.assertEqual(utils.id_obj_to_int(id_obj), id_int)

    def test_creates_an_id_from_an_int(self):
        id_int = random.randint(1, int(
            12*'f', 16
        ))
        id_obj = utils.int_to_id_obj(id_int)
        self.assertEqual(
            int.from_bytes(id_obj.binary, 'big'),
            id_int
        )

    def test_creates_a_hex_str_from_an_id_obj(self):
        rand_int = random.randint(1, int(
            12*'f', 16
        ))
        hex_str = hex(rand_int)
        id_obj = utils.int_to_id_obj(rand_int)
        hex_from_obj = utils.id_obj_to_hex_str(id_obj)
        # we cannot compare the strings directly because they are formatted differently
        # (leading zeroes + leading 0x. but they should represent the same integer.
        self.assertEqual(
            int(hex_str, 16), int(hex_from_obj, 16)
        )

    def test_creates_an_id_obj_from_a_hex_str(self):
        rand_int = random.randint(1, int(
            12 * 'f', 16
        ))
        hex_str = hex(rand_int)
        id_obj = utils.hex_str_to_id_obj(hex_str)
        self.assertEqual(
            rand_int,
            utils.id_obj_to_int(id_obj)
        )
