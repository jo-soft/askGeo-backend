import random
import unittest
import unittest.mock as mock

from database.exceptions import NotFoundError
from models.misc import CachedObj
from models.model_reference_fields import ReferenceTargetField, ReferenceField


class ReferenceFieldBase(unittest.TestCase):
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

            def __init__(self):
                self._id = random.randint(0, 100)

        self.manager = ManagerMock()
        self.modelMockCls = ModelMock


class TestReferenceTargetFieldSerialize(ReferenceFieldBase):
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


class TestReferenceTargetFieldLoad(ReferenceFieldBase):
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


class TestReferenceFieldSerialize(ReferenceFieldBase):
    def test_returns_serialized_value_for_single_value(self):
        field = ReferenceField(
            target_cls=lambda: self.modelMockCls,
            filter_conditions={'foo': 'bar'}
        )

        class SerializableMock:
            def __init__(self, serialized):
                self.serialized = serialized

            def serialize(self):
                return self.serialized

        serialized_value = random.randint(0, 100)

        result = SerializableMock(serialized_value)

        val = CachedObj(
            lambda: result
        )
        self.assertEqual(
            field._serialize(val),
            serialized_value
        )

    def test_returns_serialized_value_for_each_hit(self):
        field = ReferenceField(
            target_cls=lambda: self.modelMockCls,
        )

        class SerializableMock:
            def __init__(self, serialized):
                self.serialized = serialized

            def serialize(self):
                return self.serialized

        serialized_values = [
            random.randint(0, 100),
            random.randint(0, 100)
        ]

        result = [
            SerializableMock(serialized_val) for serialized_val in serialized_values
        ]

        val = CachedObj(
            lambda: result
        )
        self.assertEqual(
            field._serialize(val),
            serialized_values
        )


class TestReferenceFieldLoadWithoutCache(ReferenceFieldBase):
    def test_returns_matching_val_from_manager(self):
        field_name = "fieldNameFoo"

        class DummyObj(self.modelMockCls):
            def __init__(self):
                super().__init__()
                self.fieldNameFoo = random.randint(0, 100)

        obj = DummyObj()

        field = ReferenceField(
            target_cls=lambda: DummyObj,
            cache=False
        )

        get_return_value = random.randint(0, 100)
        self.manager.get.return_value = get_return_value
        field.load(obj, field_name)
        loaded1 = getattr(obj, field_name)
        field.load(obj, field_name)
        loaded2 = getattr(obj, field_name)

        self.assertEqual(loaded1.__class__, CachedObj)
        loaded_value1 = loaded1.value

        loaded1.value  # trigger load again
        self.assertNotEqual(
            id(loaded1), id(loaded2)
        )

        self.assertEqual(get_return_value, loaded_value1)

        self.manager.get.assert_called_with({
            '_id': obj._id
        })


class TestReferenceFieldLoadWithCache(ReferenceFieldBase):
    def test_returns_matching_val_from_manager(self):
        from_field_name = "fieldNameFoo"
        to_field_name = "fieldNameBar"

        class DummyObj(self.modelMockCls):
            def __init__(self):
                super().__init__()
                self.fieldNameFoo = random.randint(0, 100)

        obj = DummyObj()

        field = ReferenceField(
            target_cls=lambda: DummyObj,
            load_from=from_field_name
        )

        get_return_value = random.randint(0, 100)
        self.manager.get.return_value = get_return_value
        field.load(obj, to_field_name)

        loaded1 = getattr(obj, to_field_name)
        field.load(obj, to_field_name)
        loaded2 = getattr(obj, to_field_name)

        self.assertEqual(loaded1.__class__, CachedObj)
        loaded_value = loaded1.value

        loaded1.value  # trigger load again
        self.assertEqual(
            id(loaded1), id(loaded2)
        )

        self.assertEqual(loaded1.__class__, CachedObj)
        self.manager.get.assert_called_once_with({
            '_id': obj._id
        })
        self.assertEqual(get_return_value, loaded_value)
