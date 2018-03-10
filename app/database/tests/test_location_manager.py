import random
from copy import copy

from database.tests.test_manager import BaseManagerTest
from models.geojsonp import Point
from models.location_model import LocationBasedModel


class BaseLocationTest(BaseManagerTest):
    class Model(LocationBasedModel):
        locationField = "location"


class TestGetWithIn(BaseLocationTest):
    def setUp(self):
        super().setUp()
        self.filter_data = {
            'foo': 'bar'
        }
        self.kwarg = {
            'bam': 'baz'
        }
        some_id1 = hex(random.randint(1, 10000))
        some_id2 = hex(random.randint(1, 10000))

        self.vertices = list(map(lambda d: Point(d), [
            [0, 0],
            [1, 1],
            [-1, -2]
        ]))

        def side_effect(_filter_data, **kwargs):
            extended_filter_data = copy(self.filter_data)
            extended_filter_data[self.manager.location_field] = {
                "$geoWithin": {
                    "$polygon": [
                        [vertex.longitude, vertex.latitude] for vertex in self.vertices
                    ]
                }
            }
            self.assertEqual(_filter_data, extended_filter_data)
            self.assertEqual(kwargs['bam'], self.kwarg['bam'])

            return [
                {
                    '_id': some_id1,
                    'delete': False,
                    'location': {
                        'type': 'Point',
                        'coordinates': [random.randint(0, 360), random.randint(0, 180)]
                    }
                },
                {
                    '_id': some_id2,
                    'delete': False,
                    'location': {
                        'type': 'Point',
                        'coordinates': [random.randint(0, 360), random.randint(0, 180)]
                    }
                }
            ]

        self.manager.collection.find.side_effect = side_effect

    def test_calls_get_With_geo_within(self):
        self.manager.get_within(
            self.vertices,
            self.filter_data,
            **self.kwarg
        )
        self.manager.collection.find.assert_called_once()


class TestGetNear(BaseLocationTest):
    def setUp(self):
        super().setUp()
        self.filter_data = {
            'foo': 'bar'
        }
        self.kwarg = {
            'bam': 'baz'
        }
        some_id1 = hex(random.randint(1, 10000))
        some_id2 = hex(random.randint(1, 10000))

        self.location = Point([random.randint(0, 360), random.randint(0, 180)])
        self.min_distance = random.randint(0, 10000)
        self.max_distance = self.min_distance + random.randint(0, 10000)

        def side_effect(_filter_data, **kwargs):
            extended_filter_data = copy(self.filter_data)
            extended_filter_data[self.manager.location_field] = {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [self.location.longitude, self.location.latitude]
                    },
                    "$maxDistance": self.max_distance,
                    "$minDistance": self.min_distance
                }
            }
            self.assertEqual(_filter_data, extended_filter_data)
            self.assertEqual(kwargs['bam'], self.kwarg['bam'])

            return [
                {
                    '_id': some_id1,
                    'delete': False,
                    'location': {
                        'type': 'Point',
                        'coordinates': [random.randint(0, 360), random.randint(0, 180)]
                    }
                },
                {
                    '_id': some_id2,
                    'delete': False,
                    'location': {
                        'type': 'Point',
                        'coordinates': [random.randint(0, 360), random.randint(0, 180)]
                    }
                }
            ]

        self.manager.collection.find.side_effect = side_effect

    def test_calls_get_With_geo_within(self):
        self.manager.get_near(
            self.location,
            self.max_distance,
            min_distance=self.min_distance,
            additional_filter_data=self.filter_data,
            **self.kwarg
        )
        self.manager.collection.find.assert_called_once()
