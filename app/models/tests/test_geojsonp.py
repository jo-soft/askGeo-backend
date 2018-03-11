import random
import unittest

from models.geojsonp import locationEntityFactory, Point


class TestLocationEntityFactory(unittest.TestCase):
    def test_get_class_returns_an_registered_class_by_type_property(self):
        class TestClass:
            type = "TestClass"

        locationEntityFactory.register(TestClass)
        self.assertEqual(
            locationEntityFactory.get_class('TestClass'), TestClass
        )

    def test_get_class_returns_an_class_registered_with_a_name(self):
        class TestClassForName:
            pass

        name = 'name'
        locationEntityFactory.register(TestClassForName, name)
        self.assertEqual(
            locationEntityFactory.get_class(name), TestClassForName
        )

    def test_has_Point_registered(self):
        self.assertEqual(
            locationEntityFactory.get_class('Point'), Point
        )


class TestPoint(unittest.TestCase):
    def setUp(self):
        self.longitude = random.randint(0, 180)
        self.latitude = random.randint(0, 360)

        self.point = Point([self.longitude, self.latitude])

    def test_constructor(self):
        self.assertEquals(
            self.point.longitude, self.longitude
        )
        self.assertEquals(
            self.point.latitude, self.latitude
        )

    def test_serialize(self):
        serialized = self.point.serialize()
        self.assertEqual(serialized,
                         {
                             'type': "Point",
                             'coordinates': tuple((self.longitude, self.latitude))
                         })
