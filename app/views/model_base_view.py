from flask import abort, request
from flask_restful import Api, Resource

from database.exceptions import NotFoundError
from database.utils import int_to_id_obj
from views.decorators import requires_argument


class BaseModelView(Resource):

    @classmethod
    def register(cls, app_or_blueprint, *url):
        api = Api(app_or_blueprint)
        api.add_resource(cls, *url)

    def __init__(self, model_cls):
        self.model_cls = model_cls
        self.manager = self.model_cls.manager()

    def get(self,  **kwargs):
        try:
            if kwargs:
                return self._get_single(**kwargs)
            else:
                return self._get_list()
        except NotFoundError as not_found:
            abort(404, not_found._id)

    @requires_argument()
    def _get_single(self, _id, **kwargs):
        item = self.manager.get_one_by_id(_id, **kwargs)
        if item:
            return item.serialize()
        else:
            abort(404)

    def _get_list(self):
        items = self.manager.get({
            'deleted': False
        })
        serialized_items = [
            item.serialize() for item in
            items
        ]
        return serialized_items

    def post(self):
        data = request.json[self.field_name]
        item = self.model_cls(**data)
        saved_instance = self.manager.save(item)
        return saved_instance.serialize(), 201

    @requires_argument()
    def put(self, **kwargs):
        data = request.json[self.field_name]
        item = self.model_cls(**data)
        item._id = int_to_id_obj(kwargs['_id'])
        try:
            saved_instance = self.manager.save(item)
            return saved_instance.serialize()
        except NotFoundError as not_found:
            abort(404, not_found._id)

    @requires_argument()
    def delete(self, **kwargs):
        try:
            self.manager.delete(**kwargs)
        except NotFoundError as not_found:
            abort(404, not_found._id)
        except Exception as err:
            abort(500, err)
