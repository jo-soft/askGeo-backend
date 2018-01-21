from pymongo import GEO2D

from database.manager import Manager


class LocationManager(Manager):
    def __init__(self, location_field="loc", *args, **kwargs):
        super.__init__(*args, **kwargs)
        self.location_field = location_field
        self.db_table.createIndex([
            (location_field, GEO2D)
        ])

    def _build_filter_data(self, base_filter, location_filter):
        filter_data = base_filter.copy()
        filter_data[self.location_field] = location_filter
        return filter_data

    def get_within(self, vertices, additional_filter_data={}, **kwargs):
        filter_data = self._build_filter_data(
            additional_filter_data,
            {

                "$geoWithin": {
                    "$polygon": [
                        [vertex.longitude, vertex.latitude] for vertex in vertices
                    ]
                }
            }
        )
        return super().get(filter_data, **kwargs)

    def get_near(self, location, dist, additional_filter_data={}, min_dist=0, **kwargs):
        filter_data = self._build_filter_data(
            additional_filter_data,
            {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [location.longitude, location.latitude]
                    },
                    "$maxDistance": dist,
                    "$minDistance": min_dist
                }
            }
        )
        return super().get(filter_data, **kwargs)
