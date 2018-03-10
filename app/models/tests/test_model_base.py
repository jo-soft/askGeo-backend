import random
import unittest
import unittest.mock as mock
from copy import copy

from marshmallow import fields

from database.manager import Manager
from database.schema_fields import IdField
from database.utils import int_to_id_obj
from models.model_base import ModelBase


class TestModelBaseSchema(unittest.TestCase):
    def setUp(self):
        schema_cls = ModelBase.get_scheme_cls()
        self.schema = schema_cls()

    def test_has_id_and_delete_field(self):
        self.assertTrue(
            isinstance(self.schema.fields['_id'], IdField)
        )
        self.assertTrue(
            self.schema.fields['_id'].allow_none
        )
        self.assertTrue(
            isinstance(self.schema.fields['deleted'], fields.Boolean)
        )
        self.assertFalse(
            self.schema.fields['deleted'].default
        )

    def test_creates_instance_of_model(self):
        instance = self.schema.make_instance({})
        self.assertTrue(
            isinstance(instance, ModelBase)
        )

    def test_creates_instance_of_given_cls(self):
        class Dummy:
            pass

        schema_cls = ModelBase.get_scheme_cls(Dummy)
        schema = schema_cls()
        instance = schema.make_instance({})
        self.assertTrue(
            isinstance(instance, Dummy)
        )


class TestManager(unittest.TestCase):
    def test_creates_manager_for_class(self):
        class TestCls(ModelBase):
            pass

        manager = TestCls.manager()
        self.assertEqual(manager.content_class, TestCls)
        self.assertTrue(
            isinstance(manager, Manager)
        )


class TestNew(unittest.TestCase):
    def test_is_true_if_no_id_is_present(self):
        instance = ModelBase()
        self.assertTrue(instance.is_new())

    def test_is_false_if_id_is_given(self):
        instance = ModelBase(
            _id=int_to_id_obj(random.randint(1, 10000))
        )
        self.assertFalse(
            instance.is_new()
        )


class TestDeleted(unittest.TestCase):
    def test_sets_the_value(self):
        instance = ModelBase()
        self.assertFalse(
            instance.deleted()
        )
        instance.deleted(True)
        self.assertTrue(
            instance.deleted()
        )


class DummyField:
    def __init__(self):
        self.load = mock.MagicMock()
        self.serialize = mock.MagicMock()


class TestSerialization(unittest.TestCase):
    class Dummy(ModelBase):
        fields = {
            'dummy_field': DummyField()
        }

        @classmethod
        def get_scheme_cls(cls, class_to_create=None):
            base_schema = super(TestSerialization.Dummy, cls).get_scheme_cls(class_to_create)

            class DummySchema(base_schema):
                dummy_field_1 = fields.Integer()
                dummy_field_2 = fields.Integer()

            return DummySchema

    def setUp(self):
        self.dummy_data = {
            'dummy_field_1': random.randint(0, 1000),
            'dummy_field_2': random.randint(1000, 300000)
        }
        self.dummy_instance = TestSerialization.Dummy(**self.dummy_data)

    def test_creates_an_instance(self):
        self.assertEqual(
            self.dummy_instance.dummy_field_1,
            self.dummy_data['dummy_field_1']
        )
        self.assertEqual(
            self.dummy_instance.dummy_field_2,
            self.dummy_data['dummy_field_2']
        )

    def test_serialize(self):
        serialized_dummy = self.dummy_instance.serialize()
        extended_dummy_data = copy(self.dummy_data)
        extended_dummy_data['_id'] = None
        extended_dummy_data['deleted'] = False

        self.assertEqual(
            serialized_dummy,
            extended_dummy_data
        )

    def test_serialize_deleted(self):
        self.dummy_instance.deleted(True)
        serialized_dummy = self.dummy_instance.serialize()
        extended_dummy_data = copy(self.dummy_data)
        extended_dummy_data['_id'] = None
        extended_dummy_data['deleted'] = True

        self.assertEqual(
            serialized_dummy,
            extended_dummy_data
        )

    def test_serialize_field(self):
        self.Dummy.fields['dummy_field'].serialize.reset_mock()
        self.dummy_instance.serialize()
        self.Dummy.fields['dummy_field'].serialize.assert_called_once_with(
            field_name='dummy_field', obj=self.dummy_instance
        )

    def test_load_field(self):
        self.Dummy.fields['dummy_field'].load.reset_mock()
        self.dummy_instance = TestSerialization.Dummy(**self.dummy_data)
        self.Dummy.fields['dummy_field'].load.assert_called_once_with(
            field_name='dummy_field', obj=self.dummy_instance
        )
