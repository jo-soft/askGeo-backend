from marshmallow import fields

from database.schema_fields import ReverseIdField
from database.utils import hex_str_to_id_obj
from models.location_model import LocationBasedModel
from models.model_reference_fields import ReferenceTargetField


def _get_question_model():
    from models.question import QuestionModel
    return QuestionModel


class AnswerModel(LocationBasedModel):
    fields = {
        "question": ReferenceTargetField(
            target_cls=_get_question_model,
            value_transformer=lambda v: hex_str_to_id_obj(v.value._id),
            load_from="question_id",
            dump_to='question_id'
        )
    }

    @classmethod
    def get_scheme_cls(cls, class_to_create=None):
        class_to_create = class_to_create or cls
        base_schema = super(AnswerModel, cls).get_scheme_cls(class_to_create)

        class AnswerSchema(base_schema):
            text = fields.String()
            score = fields.Integer(default=0)
            question_id = ReverseIdField()

        return AnswerSchema
