import random
import unittest
import unittest.mock as mock

from database.exceptions import NotFoundError
from models.misc import CachedObj
from models.model_reference_fields import ReferenceTargetField


class ReferenceTargetFieldBase(unittest.TestCase):
    def setUp(self):
        class ManagerMock:
            def __init__(self):
                self.get = mock.MagicMock()
                self.exists = mock.MagicMock()
                self.collection = {}

        class ModelMock:
            @classmethod
            def manager(cls):
                return self.manager

        self.manager = ManagerMock()
        self.modelMockCls = ModelMock


class TestReferenceTargetFieldSerialize(ReferenceTargetFieldBase):
    def test_serialize_no_value_transformer_no_exists(self):
        field = ReferenceTargetField(
            target_cls=self.modelMockCls,
            validate_exists=False
        )

        val = random.randint(0, 1000)
        serialized = field._serialize(val)
        self.assertEqual(val, serialized)
        self.manager.exists.assert_not_called()

    def test_serialize_no_value_transformer_item_exists(self):
        field = ReferenceTargetField(
            target_cls=self.modelMockCls,
        )
        self.manager.exists.return_value = True

        val = random.randint(0, 1000)
        serialized = field._serialize(val)
        self.assertEqual(val, serialized)
        self.manager.exists.assert_called_once_with({
            '_id': val
        })

    def test_serialize_wirg_transformer_item_exists(self):
        value_transformer = lambda x: x + 1
        field = ReferenceTargetField(
            target_cls=self.modelMockCls,
            value_transformer=value_transformer
        )
        self.manager.exists.return_value = True

        val = random.randint(0, 1000)
        serialized = field._serialize(val)
        self.assertEqual(value_transformer(val), serialized)
        self.manager.exists.assert_called_once_with({
            '_id': value_transformer(val)
        })

    def test_serialize_no_value_transformer_item_does_notexists(self):
        field = ReferenceTargetField(
            target_cls=lambda: self.modelMockCls,
        )
        self.manager.exists.return_value = False

        val = random.randint(0, 1000)
        with self.assertRaises(NotFoundError):
            field._serialize(val)


class TestReferenceTargetFieldLoad(ReferenceTargetFieldBase):
    def test_load_creates_a_cached_obj(self):
        self.manager.get.return_value = ()
        field = ReferenceTargetField(
            target_cls=lambda: self.modelMockCls,
        )
        val = random.randint(0, 1000)
        saved = field._load(val)

        self.assertTrue(
            isinstance(saved, CachedObj)
        )

    def test_load_returns_none_if_no_item_is_found(self):
        self.manager.get.return_value = ()
        field = ReferenceTargetField(
            target_cls=lambda: self.modelMockCls,
        )
        val = random.randint(0, 1000)
        saved = field._load(val)
        self.assertIsNone(
            saved.value
        )
        self.manager.get.assert_called_once_with({
            '_id': val
        })

    def test_load_returns_found_item(self):
        result = random.randint(0, 1000)
        target_field = "target"
        self.manager.get.return_value = [result]
        field = ReferenceTargetField(
            target_cls=lambda: self.modelMockCls,
            target_field=target_field
        )
        val = random.randint(0, 1000)
        saved = field._load(val)
        self.assertEqual(
            saved.value, result
        )
        self.manager.get.assert_called_once_with({
            target_field: val
        })
