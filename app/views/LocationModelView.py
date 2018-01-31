from flask import request, abort

from database.exceptions import NotFoundError
from views.model_base_view import BaseModelView


class LocationModelView(BaseModelView):
    def is_nearby_request(self, kwargs):
        return "_id" not in kwargs and all([
            key in request.args for key in [
                "longitude",
                "latitude",
                "max_distance"
            ]
        ])

    def is_within_request(self, kwargs):
        return "_id" not in kwargs and "vertices" in request.args

    def is_single_item_request(self, kwargs):
        return "_id" in kwargs

    def get(self, **kwargs):

        query_params = request.args

        if self.is_nearby_request(kwargs):
            min_distance = float(query_params.get("min_distance")) if 'min_distance' in query_params else None
            return [model.serialize() for model in self.manager.get_near(
                location={
                    "longitude": float(query_params.get("longitude")),
                    "latitude": float(query_params.get("latitude"))
                },
                max_distance=float(query_params.get("max_distance")),
                min_distance=min_distance,
                **kwargs
            )]
        elif self.is_within_request(kwargs):
            # todo: ensure vertices is an array of 2-tuples of int
            return [model.serialize() for model in self.manager.get_within(
                vertices=query_params.vertices,
                **kwargs
            )]
        elif self.is_single_item_request(kwargs):
            try:
                return self._get_single(**kwargs)
            except NotFoundError as not_found:
                abort(404, not_found._id)

        else:
            return self._get_list(**kwargs)
