import random
import unittest

from marshmallow import fields

from database.schema_fields import TupleField, IdField, ReverseIdField, UnCacheField
from database.utils import int_to_id_obj, id_obj_to_hex_str
from models.misc import CachedObj


class TestTupleField(unittest.TestCase):
    def setUp(self):
        self.field = TupleField(
            (fields.String(), fields.Boolean())
        )

    def test_serialize_success(self):
        data = ('abc', True)

        serialized = self.field._serialize(data, {})
        self.assertEqual(
            serialized, data
        )

    def test_deserialize_success(self):
        data = ('abc', True)

        deserialized = self.field._deserialize(data, {})
        self.assertEqual(
            tuple(deserialized), data
        )


class TestIdField(unittest.TestCase):
    def setUp(self):
        self.field = IdField()

    def test_deserialize_with_id_obj(self):
        random_id = random.randint(0, 1000)
        _id = int_to_id_obj(random_id)

        deserialized = self.field._deserialize(_id, {})
        self.assertEqual(
            deserialized,
            id_obj_to_hex_str(_id)
        )

    def test_deserialize_with_hex_str(self):
        random_id = random.randint(0, 1000)
        _id = int_to_id_obj(random_id)
        id_hex_str = id_obj_to_hex_str(_id)
        deserialized = self.field._deserialize(id_hex_str, {})
        self.assertEqual(
            deserialized, id_hex_str
        )


class TestReverseIdField(unittest.TestCase):
    def setUp(self):
        self.field = ReverseIdField()

    def test_deserialize_with_id_obj(self):
        random_id = random.randint(0, 1000)
        _id = int_to_id_obj(random_id)

        deserialized = self.field._deserialize(_id, {})
        self.assertEqual(
            deserialized,
            _id
        )

    def test_deserialize_with_hex_str(self):
        random_id = random.randint(0, 1000)
        _id = int_to_id_obj(random_id)
        id_hex_str = id_obj_to_hex_str(_id)
        deserialized = self.field._deserialize(id_hex_str, {})
        self.assertEqual(
            deserialized, _id
        )


class TestUnCacheField(unittest.TestCase):
    def setUp(self):
        self.field = UnCacheField()
        self.value = random.randint(0, 10000)

    def test_returns_value_from_cached_obj(self):
        val = CachedObj(
            lambda: self.value
        )

        serialized = self.field._serialize(val, {})
        self.assertEqual(serialized, self.value)

    def test_returns_value_if_not_cached(self):
        serialized = self.field._serialize(self.value, {})
        self.assertEqual(serialized, self.value)
