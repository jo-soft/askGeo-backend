import random
import unittest
from unittest import mock

from database.location_manager import LocationManager
from models.geojsonp import Point
from models.location_model import LocationBasedModel


class TestManager(unittest.TestCase):

    def setUp(self):
        self.patcher = mock.patch('database.manager.get_db')
        self.get_db_mock = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_creates_manager_for_class(self):
        class TestCls(LocationBasedModel):
            pass

        manager = TestCls.manager()
        self.assertEqual(manager.content_class, TestCls)
        self.assertTrue(
            isinstance(manager, LocationManager)
        )


class TestLocationModel(unittest.TestCase):
    def setUp(self):
        self.data = {
            'loc': {
                'type': 'Point',
                'coordinates': (
                    float(random.randint(0, 180)),
                    float(random.randint(0, 360))
                )
            }
        }
        serialized = LocationBasedModel.get_scheme_cls()().load(self.data)
        self.assertDictEqual(serialized.errors, {})
        self.instance = serialized.data

    def test_deserialize_valid(self):
        self.assertTrue(
            isinstance(self.instance.loc, Point)
        )
        self.assertEqual(self.instance.loc.longitude, self.data['loc']['coordinates'][0])
        self.assertEqual(self.instance.loc.latitude, self.data['loc']['coordinates'][1])

    def test_deserialize_no_type(self):
        invalid_data = {
            'loc': {
                'coordinates': [
                    random.randint(0, 180),
                    random.randint(0, 360)
                ]
            }
        }
        errors = LocationBasedModel.get_scheme_cls()().load(invalid_data).errors
        self.assertEqual(errors, {'loc': {'type': ['Missing data for required field.']}})

    def test_deserialize_no_type(self):
        invalid_data = {
            'loc': {
                'type': 'Point'
            }
        }
        errors = LocationBasedModel.get_scheme_cls()().load(invalid_data).errors
        self.assertEqual(errors, {'loc': {'coordinates': ['Missing data for required field.']}})

    def test_deserialize_invalid_type(self):
        invalid_data = {
            'loc': {
                'type': 'bla',
                'coordinates': [
                    random.randint(0, 180),
                    random.randint(0, 360)
                ]
            }
        }
        errors = LocationBasedModel.get_scheme_cls()().load(invalid_data).errors
        self.assertEqual(
            len(errors['loc']['type']), 1
        )
        self.assertTrue(
            isinstance(errors['loc']['type'][0], KeyError)
        )
        self.assertEqual(
            errors['loc']['type'][0].args, ('bla',)
        )

    def test_deserialize_invalid_coordinates1(self):
        invalid_data = {
            'loc': {
                'type': 'Point',
                'coordinates': [
                    None,
                    random.randint(0, 360)
                ]
            }
        }
        serialized = LocationBasedModel.get_scheme_cls()().load(invalid_data)
        errors = serialized.errors
        self.assertIsNone(
            errors['loc']['coordinates'][1]
        )
        self.assertEqual(
            errors['loc']['coordinates'][0].messages,
            ['Field may not be null.']
        )

    def test_deserialize_invalid_coordinates2(self):
        invalid_data = {
            'loc': {
                'type': 'Point',
                'coordinates': [
                    random.randint(0, 180),
                    None
                ]
            }
        }
        serialized = LocationBasedModel.get_scheme_cls()().load(invalid_data)
        errors = serialized.errors
        self.assertIsNone(
            errors['loc']['coordinates'][0]
        )
        self.assertEqual(
            errors['loc']['coordinates'][1].messages,
            ['Field may not be null.']
        )

    def test_serialize_valid(self):
        serialized = self.instance.serialize()
        self.assertEqual(
            serialized['loc'],
            self.data['loc']
        )
