from flask import Blueprint

from models.answer import AnswerModel
from views.LocationModelView import LocationModelView

answer_bp = Blueprint('/answers', __name__)
answer_bp.record(lambda _: register())


def register():
    AnswerList.register(answer_bp, '/answers/', '/answers/<int:_id>')


class AnswerList(LocationModelView):
    def __init__(self):
        super().__init__(AnswerModel)
        self.field_name = "answer"
