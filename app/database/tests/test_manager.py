import random
import unittest
import unittest.mock as mock
from copy import copy

from marshmallow.fields import Field

import models.model_base as model_base
from database import manager, utils
from database.exceptions import NotFoundError, InsertFailedError, UpdateFailedError
from database.utils import int_to_id_obj, id_obj_to_hex_str


class BaseManagerTest(unittest.TestCase):
    class DbMock:
        def __init__(self):
            self.find_one = mock.MagicMock()
            self.find = mock.MagicMock()
            self.insert_one = mock.MagicMock()
            self.update_one = mock.MagicMock()

    class Model(model_base.ModelBase):
        pass

    def setUp(self):
        db_mock = self.DbMock()
        self.patcher = mock.patch('database.manager.get_db')
        self.get_db_mock = self.patcher.start()
        self.manager = self.Model.manager()

    def tearDown(self):
        self.patcher.stop()


class TestGetOneById(BaseManagerTest):
    def test_calls_find_one(self):
        some_id = hex(random.randint(1, 10000))

        filter_data = {
            'foo': 'bar'
        }
        kwarg = {
            'bam': 'baz'
        }
        extended_filter_data = copy(filter_data)
        extended_filter_data['_id'] = utils.hex_str_to_id_obj(some_id)

        def side_effect(filter_data, **kwargs):
            self.assertEqual(filter_data, extended_filter_data)
            self.assertEqual(kwargs['bam'], kwarg['bam'])

            return {
                '_id': some_id,
                'delete': False
            }

        self.manager.collection.find_one.side_effect = side_effect

        item = self.manager.get_one_by_id(
            some_id,
            filter_data, **kwarg
        )

        self.assertEqual(
            item._id,
            some_id
        )

    def test_throws_not_found_if_find_one_returns_none(self):
        self.manager.collection.find_one.return_value = None

        some_id = str(random.randint(1, 10000))
        filter_data = {
            'foo': 'bar'
        }
        kwarg = {
            'bam': 'baz'
        }
        with self.assertRaises(NotFoundError):
            self.manager.get_one_by_id(
                some_id, filter_data, **kwarg
            )


class TestGetOne(BaseManagerTest):
    def test_calls_find_one(self):
        filter_data = {
            'foo': 'bar'
        }
        kwarg = {
            'bam': 'baz'
        }
        some_id = hex(random.randint(1, 10000))

        def side_effect(_filter_data, **kwargs):
            self.assertEqual(filter_data, _filter_data)
            self.assertEqual(kwargs['bam'], kwarg['bam'])

            return {
                '_id': some_id,
                'delete': False
            }

        self.manager.collection.find_one.side_effect = side_effect

        item = self.manager.get_one(
            filter_data, **kwarg
        )

        self.assertEqual(
            item._id,
            some_id
        )

    def test_throws_not_found_if_find_one_returns_none(self):
        self.manager.collection.find_one.return_value = None

        filter_data = {
            'foo': 'bar'
        }
        kwarg = {
            'bam': 'baz'
        }
        with self.assertRaises(NotFoundError):
            self.manager.get_one(
                filter_data, **kwarg
            )


class TestGet(BaseManagerTest):
    def test_calls_find(self):
        filter_data = {
            'foo': 'bar'
        }
        kwarg = {
            'bam': 'baz'
        }
        some_id1 = hex(random.randint(1, 10000))
        some_id2 = hex(random.randint(1, 10000))

        def side_effect(_filter_data, **kwargs):
            self.assertEqual(filter_data, _filter_data)
            self.assertEqual(kwargs['bam'], kwarg['bam'])

            return [
                {
                    '_id': some_id1,
                    'delete': False
                },
                {
                    '_id': some_id2,
                    'delete': False
                }
            ]

        self.manager.collection.find.side_effect = side_effect

        items = self.manager.get(
            filter_data, **kwarg
        )

        self.assertEqual(
            len(items),
            2
        )

        self.assertEqual(
            items[0]._id,
            some_id1
        )

        self.assertEqual(
            items[1]._id,
            some_id2
        )

    def test_return_empty_array_for_no_data(self):
        self.manager.collection.find.return_value = []

        filter_data = {
            'foo': 'bar'
        }
        kwarg = {
            'bam': 'baz'
        }
        items = self.manager.get(
            filter_data, **kwarg
        )

        self.assertEqual(
            len(items),
            0
        )


class TestExist(BaseManagerTest):
    def build_mock(self, count):
        class ResultMock:
            class WithCount:
                def __init__(self):
                    self.count = mock.MagicMock(return_value=count)

            def __init__(self):
                self.limit = mock.Mock(return_value=self.__class__.WithCount()
                                       )

        return ResultMock()

    def test_calls_find(self):
        filter_data = {
            'foo': 'bar'
        }
        kwarg = {
            'bam': 'baz'
        }

        def side_effect(_filter_data, **kwargs):
            self.assertEqual(filter_data, _filter_data)
            self.assertEqual(kwargs['bam'], kwarg['bam'])

            self.resultMock = self.build_mock(1)
            return self.resultMock

        self.manager.collection.find.side_effect = side_effect

        exists = self.manager.exists(
            filter_data, **kwarg
        )

        self.resultMock.limit.assert_called_with(1)
        self.assertTrue(exists)

    def test_return_empty_array_for_no_data(self):
        def side_effect(_filter_data, **kwargs):
            self.assertEqual(filter_data, _filter_data)
            self.assertEqual(kwargs['bam'], kwarg['bam'])

            self.resultMock = self.build_mock(0)
            return self.resultMock

        self.manager.collection.find.side_effect = side_effect

        filter_data = {
            'foo': 'bar'
        }
        kwarg = {
            'bam': 'baz'
        }

        exists = self.manager.exists(
            filter_data, **kwarg
        )

        self.assertFalse(exists)


class TestSaveForNewItems(BaseManagerTest):
    class Model(model_base.ModelBase):

        externalField = Field(external=True)
        noneInternalField = Field(internal=False)
        field = Field(allow_none=True)

    def setUp(self):
        super().setUp()
        self.some_id = random.randint(1, 10000)

        self.item = self.Model()
        self.item_json = self.item.serialize(
            exclude=['_id'], field_filter_fn=self.manager._default_exclude_in_save_fn
        )

        def side_effect(data):
            self.assertEqual(self.item_json, data)

            self.assertFalse(
                'field' in data
            )
            self.assertFalse(
                'externalField' in data
            )
            self.assertFalse(
                'noneInternalField' in data
            )

            class InsertResultMock:
                def __init__(self, inserted_int_id):
                    if inserted_int_id:
                        self.inserted_id = int_to_id_obj(inserted_int_id)
                    else:
                        self.inserted_id = inserted_int_id

            return InsertResultMock(self.some_id)

        self.manager.collection.insert_one.side_effect = side_effect

    def assert_function_calls(self):
        self.manager.collection.insert_one.assert_called_once()
        self.manager.collection.update_one.assert_not_called()

    def test_calls_insert_one_with_serialized_data(self):

        saved_item = self.manager.save(self.item)
        hex_str_from_id = id_obj_to_hex_str(
            int_to_id_obj(self.some_id)
        )
        self.assertEqual(saved_item._id, hex_str_from_id)
        self.assert_function_calls()

    def test_throws_insert_fails_exception_if_no_inserted_id_is_returned(self):
        self.some_id = None

        with self.assertRaises(InsertFailedError):
            self.manager.save(self.item)


class TestSaveForExistingItems(BaseManagerTest):
    class Model(model_base.ModelBase):
        externalField = Field(external=True)
        noneInternalField = Field(internal=False)
        field = Field(allow_none=True)

    def setUp(self):
        super().setUp()
        self.some_id = random.randint(1, 10000)
        self.matched_count = 1
        self.modified_count = 1

        self.item = self.Model(_id=int_to_id_obj(self.some_id))
        self.item_json = self.item.serialize(
            field_filter_fn=self.manager._default_exclude_in_save_fn
        )

        def side_effect(filter_data, update):

            self.assertEqual(update, {"$set": self.item_json})

            self.assertFalse(
                'field' in update['$set']
            )
            self.assertFalse(
                'externalField' in update['$set']
            )
            self.assertFalse(
                'noneInternalField' in update['$set']
            )

            self.assertEqual(filter_data, {"_id": int_to_id_obj(self.some_id)})

            class UpdateResultMock:
                def __init__(self, matched_count, modified_count):
                    self.matched_count = matched_count
                    self.modified_count = modified_count

            return UpdateResultMock(self.matched_count, self.modified_count)

        self.manager.collection.update_one.side_effect = side_effect

    def assert_function_calls(self):
        self.manager.collection.insert_one.assert_not_called()
        self.manager.collection.update_one.assert_called_once()

    def test_calls_update_one_with_serialized_data(self):
        saved_item = self.manager.save(self.item)

        self.assertEqual(saved_item, self.item)
        self.assert_function_calls()

    def test_throws_not_found_exception_if_no_item_was_found(self):
        self.matched_count = 0
        self.modified_count = 0

        with self.assertRaises(NotFoundError):
            self.manager.save(self.item)

    def test_throws_updated_failed_exception_if_no_item_gets_updated(self):
        self.matched_count = 1
        self.modified_count = 0

        with self.assertRaises(UpdateFailedError):
            self.manager.save(self.item)


class TestDelete(BaseManagerTest):
    def setUp(self):
        super().setUp()
        self.some_id = random.randint(1, 10000)
        self.deleted_count = 1

        self.item = self.Model(_id=self.some_id)

        def side_effect(filter_data):
            self.assertEqual(
                filter_data,
                {"_id": int_to_id_obj(self.item._id)}
            )

            class DeleteResultMock:
                def __init__(self, deleted_count):
                    self.deleted_count = deleted_count

            return DeleteResultMock(self.deleted_count)

        self.manager.collection.delete_one.side_effect = side_effect

    def test_delete_calls_delete_one(self):
        self.manager.delete(hex(self.item._id))
        self.manager.collection.delete_one.assert_called_once()

    def test_throws_not_found_exception_if_no_item_was_found(self):
        self.deleted_count = 0

        with self.assertRaises(NotFoundError):
            self.manager.delete(hex(self.item._id))

    def test_delete_by_id_calls_delete_one(self):
        self.manager.delete_by_id(int_to_id_obj(self.some_id))
        self.manager.collection.delete_one.assert_called_once()

    def test_throws_not_found_exception_if_no_item_was_found_for_given_id(self):
        self.deleted_count = 0

        with self.assertRaises(NotFoundError):
            self.manager.delete_by_id(int_to_id_obj(self.some_id))
