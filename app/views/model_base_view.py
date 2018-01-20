from flask import abort, request
from flask_restful import Api, Resource


class BaseModelView(Resource):

    @classmethod
    def register(cls, app_or_blueprint, *url):
        api = Api(app_or_blueprint)
        api.add_resource(cls, *url)

    def __init__(self, model_cls):
        self.model_cls = model_cls
        self.manager = self.model_cls.manager()

    def get(self,  **kwargs):
        if kwargs:
            return self._get_single(**kwargs)
        else:
            return self._get_list()

    def _get_single(self, **kwargs):
        item = self.manager.get_one(kwargs)
        if item:
            return item.serialize()
        else:
            abort(404)

    def _get_list(self):
        serialized_items = [
            item.serialize() for item in
            self.manager.get({
                'deleted': False
            })
        ]
        return serialized_items

    def put(self, **kwargs):
        data = request.json[self.field_name]
        item = self.model_cls(**data)
        saved_instance = self.manager.save(item, **kwargs)
        return saved_instance.serialize()

    def post(self, **kwargs):
        data = request.json[self.field_name]
        item = self.model_cls(**data)
        saved_instance = self.manager.save(item, **kwargs)
        return saved_instance.serialize()

    def delete(self, **kwargs):
        return self.manager.delete(**kwargs)