class LocationEntityFactory(object):
    def __init__(self):
        self.classes = {}

    def register(self, cls, type_name=None):
        type_name = type_name or cls.type
        self.classes[type_name] = cls

    def get_class(self, type_name):
        return self.classes[type_name]


class Point(object):
    type = "Point"

    def __init__(self, coordinates):
        self.longitude, self.latitude = coordinates

    def serialize(self):
        return {
            'type': self.type,
            'coordinates': tuple((self.longitude, self.latitude))
        }


locationEntityFactory = LocationEntityFactory()
locationEntityFactory.register(Point)
