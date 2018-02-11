from marshmallow import fields

from database.schema_fields import UnCacheField
from models.location_model import LocationBasedModel
from models.model_reference_fields import ReferenceField


def _question_answer_model():
    from models.answer import AnswerModel
    return AnswerModel


class QuestionModel(LocationBasedModel):
    fields = {
        "answers": ReferenceField(
            target_cls=_question_answer_model,
            reference_field="question_id"
        )
    }

    @classmethod
    def get_scheme_cls(cls, class_to_create=None):
        class_to_create = class_to_create or cls
        base_schema = super(QuestionModel, cls).get_scheme_cls(class_to_create)

        class QuestionSchema(base_schema):
            topic = fields.String()
            question = fields.String()
            score = fields.Integer(default=0)
            answers = UnCacheField(allow_none=True, internal=False)
        return QuestionSchema

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
