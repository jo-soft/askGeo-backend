from flask_restful import Api, Resource, reqparse
from flask import abort


class BaseModelView(Resource):

    @classmethod
    def register(cls, app_or_blueprint, *url):
        api = Api(app_or_blueprint)
        api.add_resource(cls, *url)

    def __init__(self, model_cls):
        self.manager = model_cls.manager()
        self.parser = reqparse.RequestParser()

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
        args = self.parser.parse_args(**kwargs)
        return self.manager.save(args['item'])

    def post(self, **kwargs):
        args = self.parser.parse_args()
        return self.manager.save(args['item'], **kwargs)

    def delete(self, **kwargs):
        return self.manager.delete(**kwargs)