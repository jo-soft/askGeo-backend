from marshmallow import fields

from models.model_base import ModelBase


class QuestionModel(ModelBase):
    @classmethod
    def get_scheme(cls, class_to_create=None):
        class_to_create = class_to_create or cls
        base_schema = super(QuestionModel, cls).get_scheme(class_to_create)

        class QuestionSchema(base_schema):
            topic = fields.String()
            question = fields.String()
            score = fields.Integer(default=0)

        return QuestionSchema

    def __init__(self,
                 **kwargs):
        super().__init__(**kwargs)
